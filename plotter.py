import numpy as np
from matplotlib.widgets import Slider
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D  # This line is needed for a 3d plot


class TrajectoryPlotter:
    def __init__(self, trajectory, interactive=True):
        self.data_trajectory = trajectory
        self.fig = None
        self.axes = None
        self.interactive = interactive
        self.colors = mcolors.TABLEAU_COLORS
        if self.interactive:
            mpl.use('TkAgg')
        else:
            pass

    def original_data_with_timestep_slider(self, min_max=None):
        """
        Creates an interactive plot window, where the plotted data at a timestep can be chosen by a Slider.
        Used as in https://matplotlib.org/stable/gallery/widgets/slider_demo.html
        :param min_max: data range of the data with a min and a max value
        """
        if not self.interactive:
            raise ValueError('Plotter has to be interactive to use this plot.')

        # if 'Axes3D' not in sys.modules:
        #    raise ModuleNotFoundError('Axes3D has to be imported from mpl_toolkits.mplot3d to use 3d plotting.')

        if min_max is None:  # min_max is a list of two elements
            min_max = [0, self.data_trajectory.dim['time_steps']]

        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111, projection='3d')

        plt.subplots_adjust(bottom=0.25)
        # noinspection PyTypeChecker
        ax_freq = plt.axes([0.25, 0.1, 0.65, 0.03])
        freq_slider = Slider(
            ax=ax_freq,
            label='Time Step',
            valmin=min_max[0],  # minimun value of range
            valmax=min_max[-1] - 1,  # maximum value of range
            valinit=0,
            valstep=1,  # step between values
            valfmt='%0.0f'
        )
        freq_slider.on_changed(self.update_on_slider_change)
        plt.show()

    def plot_original_data_at(self, timeframe):
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111, projection='3d')
        self.update_on_slider_change(timeframe)

    def update_on_slider_change(self, timeframe):
        if 0 <= timeframe <= self.data_trajectory.traj.n_frames:
            timeframe = int(timeframe)
            x_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 0]
            y_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 1]
            z_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 2]
            self.axes.cla()
            self.axes.scatter(x_coordinates, y_coordinates, z_coordinates, c='r', marker='.')
            self.axes.set_xlim([self.data_trajectory.coordinate_mins['x'], self.data_trajectory.coordinate_maxs['x']])
            self.axes.set_ylim([self.data_trajectory.coordinate_mins['y'], self.data_trajectory.coordinate_maxs['y']])
            self.axes.set_zlim([self.data_trajectory.coordinate_mins['z'], self.data_trajectory.coordinate_maxs['z']])
            self.axes.set_xlabel('x-Axis')
            self.axes.set_ylabel('y-Axis')
            self.axes.set_zlabel('z-Axis')
            plt.show()
        else:
            raise IndexError('Timestep does not exist')

    def plot_models(self, model1, model2, reduced1, reduced2, heat_map=False):
        self.fig, self.axes = plt.subplots(3, 2)
        data_elements = [0, 1, 2]
        # data_elements = [2]
        if heat_map:
            self.plot_transformed_data_heat_map(self.axes[0][0], reduced1, data_elements, model=model1)
            self.plot_transformed_data_heat_map(self.axes[0][1], reduced2, data_elements, model=model2)
        else:
            self.plot_transformed_data_on_axis(self.axes[0][0], reduced1, data_elements, model=model1)
            self.plot_transformed_data_on_axis(self.axes[0][1], reduced2, data_elements, model=model2)
        self.plot_time_tics(self.axes[1][0], reduced1, data_elements, component=0)
        self.plot_time_tics(self.axes[2][0], reduced1, data_elements, component=1)
        self.plot_time_tics(self.axes[1][1], reduced2, data_elements, component=0)
        self.plot_time_tics(self.axes[2][1], reduced2, data_elements, component=1)
        self.fig.tight_layout()
        plt.show()

    def plot_one_model(self, model, reduced_data):
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.cla()
        self.axes.scatter(reduced_data[0][:, 0], reduced_data[0][:, 1], c='r', marker='.')
        self.axes.scatter(reduced_data[1][:, 0], reduced_data[1][:, 1], c='b', marker='.')
        self.axes.scatter(reduced_data[2][:, 0], reduced_data[2][:, 1], c='g', marker='.')
        plt.show()

    def plot_transformed_data_on_axis(self, ax, data_list, data_elements, model):
        ax.cla()
        ax.set_title(str(model))
        ax.set_xlabel('1st component')
        ax.set_ylabel('2nd component')
        for i in data_elements:
            ax.scatter(data_list[i][:, 0], data_list[i][:, 1], c=list(self.colors.values())[i], marker='.')
        self.print_model_properties(ax, data_list, model)

    def plot_time_tics(self, ax, data_list, data_elements, component):
        ax.cla()
        ax.set_xlabel('Time step')
        ax.set_ylabel('Model Component {}'.format(component+1))

        for i in data_elements:
            ax.plot(data_list[i][:, component], c=list(self.colors.values())[i])

    def plot_transformed_data_heat_map(self, ax, data_list, data_elements, model):
        ax.cla()
        ax.set_title(str(model))
        ax.set_xlabel('1st component')
        ax.set_ylabel('2nd component')
        for i in data_elements:
            xi = data_list[i][:, 0]
            yi = data_list[i][:, 1]
            bins = 57
            z, x, y = np.histogram2d(xi, yi, bins)
            F = -np.log(z)
            extent = [x[0], x[-1], y[0], y[-1]]
            ax.contour(F.T, bins, cmap=plt.cm.hot, extent=extent)
        self.print_model_properties(ax, data_list, model)

    @staticmethod
    def print_model_properties(ax, data_list, model):
        try:
            print(data_list[0].shape)
            print(model.eigenvectors_, model.eigenvalues_)
            ax.arrow(0, 0, 3 * model.eigenvectors_[0, 0], 3 * model.eigenvectors_[1, 0], color='tab:cyan')
        except AttributeError as e:
            print('%s: %s'.format(e, model))


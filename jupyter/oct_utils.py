""" Utilities for parsing data
"""
import itertools
import math
from pathlib import Path
import numpy as np
from typing import Dict, List
import matplotlib.pyplot as plt


class ConvergenceData:
    # Map column names to column indices
    mapping = {'iter': 0,
               'energy': 1,
               'energy_diff': 2,
               'abs_dens': 3,
               'rel_dens': 4,
               'abs_ev': 5,
               'rel_ev': 6
               }

    def __init__(self, root, load_on_init=True):
        self.root = root
        self.load_on_init = load_on_init
        if self.load_on_init:
            self.load()
        else:
            self.data: np.ndarray | None = None

    def load(self):
        self.data = np.loadtxt(Path(self.root, 'static/convergence'), skiprows=1)

    def get(self, key: str):
        try:
            index = self.mapping[key]
            return self.data[:, index]
        except KeyError:
            raise KeyError(f'Invalid data field key: {key}')

    def list_fields(self) -> list:
        return list(self.mapping)

    def size(self) -> tuple:
        return self.data.shape

    def n_scf_iterations(self) -> int:
        """ Get number of SCF iterations run (does not imply convergence)
        Number of SCF iterations == number of rows
        """
        return self.data.shape[0]


# def parse_convergence_calculations(subdirs: List[str], columns=None, get_system_name=lambda x: x) -> dict:
#     """ Parse data from convergence files into a dictionary.
#
#     Generality of routine broken by `mixer` key, which is specific to
#     preconditioning calculations.
#
#     :param subdirs: List of calculation directories. Expect the full path
#     :param columns: Optional list of columns to return. Defaults to relative
#     change in density.
#     :return: system_calcs: Dict with keys of system names, and values
#     = {'mixer': 'mixer', 'data': np.ndarray}
#     """
#     if columns is None:
#         columns = [0, 4]
#
#     system_calcs = {}
#
#     for subdir in map(Path, subdirs):
#         if not subdir.is_dir():
#             raise NotADirectoryError(f'Cannot find {subdir.as_posix()}')
#         # Note, this is also not general, but specific to my naming convention
#         subnames = Path(subdir).name.split('_')
#         mixer = subnames.pop()
#         system_name = "".join(s + '_' for s in subnames)[:-1]
#
#         data = np.loadtxt(Path(subdir, 'static/convergence'), skiprows=1)
#         system_calcs[system_name] = {'mixer': mixer, 'data': data[:, columns]}
#
#     return system_calcs


def parse_convergence_calculations(dirs: List[str], columns=None, get_system_name=lambda d: d.name) -> dict:
    """ Parse data from convergence files into a dictionary.

    :param subdirs: List of calculation directories. Expect the full path
    :param columns: Optional list of columns to return. Defaults to relative
    change in density.
    :param get_system_name: Callable function that gets the system name from the subdirectory.
    Default assumes subdirectory name is the system name.

    :return: system_calcs: Dict with keys of system names, and values: {'directory', 'data'}
    """
    if columns is None:
        columns = [0, 4]

    system_calcs = {}
    for dir in map(Path, dirs):
        if not dir.is_dir():
            raise NotADirectoryError(f'Cannot find {dir.as_posix()}')
        system_name = get_system_name(dir)
        data = np.loadtxt(Path(dir, 'static/convergence'), skiprows=1)
        system_calcs[system_name] = {'directory': dir.as_posix(), 'data': data[:, columns]}

    return system_calcs


def parse_profiling(root) -> dict:
    """
    :param root:
    :return:
    """
    with open(Path(root, "profiling/time.000000")) as fid:
        lines = fid.readlines()

    n_header = 4
    timings = {'cumulative': {}, 'self': {}}

    for line in lines[n_header:]:
        split_data = line.split()
        key = split_data[0]
        n_calls = int(split_data[1])

        float_data = [float(x) for x in split_data[2:8]]
        timings['cumulative'].update({key:
                                       {'NUM_CALLS': n_calls,
                                        'TOTAL_TIME': float_data[0],
                                        'TIME_PER_CALL': float_data[1],
                                        'MIN_TIME': float_data[2],
                                        'MFLOPS': float_data[3],
                                        'MBYTES/S': float_data[4],
                                        '%TIME': float_data[5]
                                        }
                                   })

        float_data = [float(x) for x in split_data[9:]]
        timings['self'].update({key:
                                       {'NUM_CALLS': n_calls,
                                        'TOTAL_TIME': float_data[0],
                                        'TIME_PER_CALL': float_data[1],
                                        'MFLOPS': float_data[2],
                                        'MBYTES/S': float_data[3],
                                        '%TIME': float_data[4]
                                        }
                                   })
    return timings


# TODO(Alex) This is generic, and could be moved to plotting
def initialise_subplot(n_plots: int, n_cols: int):
    """ Initialise matplotlib subplots for a specified grid.

    :param n_plots: Number of plots
    :param n_cols:  Number of columns.
    :return: fig, axs
    """
    # Plot settings
    assert n_cols > 0, "Must have at least one column"
    n_rows = math.ceil(n_plots / n_cols)

    # Calculate the aspect ratio of standard A4
    aspect_ratio = 297.0 / 210.0

    # Calculate the width of the figure in inches
    fig_width = 8.3  # A4 width in inches (approx)

    # Calculate the height of the figure in inches to maintain aspect ratio
    fig_height = fig_width / aspect_ratio * (n_rows / n_cols)

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height))
    fig.set_tight_layout(True)

    # axs will annoyingly return as a 1D array
    if n_rows == 1:
        axs = np.reshape(axs, (1, n_cols))

    return fig, axs


def plot_convergence(system_calcs: Dict[str, list], n_cols: int, common_settings: dict):
    """Plot N calculations per system

    TODO(Alex) Note, the font sizes etc, should scale with the number of cols per row.
    Effectively hard-coded for 2 columns.

    :param system_calcs:
    :param n_cols:
    :param common_settings:
    :return:
    """
    n_systems = len(system_calcs)
    n_rows = math.ceil(n_systems / n_cols)
    fig, axes = initialise_subplot(n_systems, n_cols=n_cols)

    # Initialise counters
    empty_lims = 0, 0
    i_cmp = -1

    map_index_to_name = {i: name for i, name in enumerate(system_calcs.keys())}

    for i, j in itertools.product(range(n_rows), range(n_cols)):
        i_cmp += 1

        # Exit when last entry is reached.
        if i_cmp > len(system_calcs) - 1:
            empty_lims = i, j
            break

        # All calculations for ith system
        name = map_index_to_name[i_cmp]
        calculations = system_calcs[name]

        # Plot calculations for a given system
        for calc in calculations:
            try:
                data = calc.pop('data')
                axes[i, j].plot(data[:, 0], data[:, 1], **calc['plot_options'])
            except KeyError:
                calc_type = 'preconditioning' if calc['preconditioning'] else 'no preconditioning'
                print(f'No data for {name} computed with {calc_type}')

        # Scales
        axes[i, j].set_yscale('log')

        # Ticks
        axes[i, j].tick_params(axis='both', which='major', labelsize=common_settings['label_size'])
        axes[i, j].tick_params(axis='both', which='minor', labelsize=common_settings['label_size'])

        # Labels
        axes[i, j].set_xlabel(common_settings['xlabel'], fontsize=common_settings['font_size'])
        axes[i, j].set_ylabel(common_settings['ylabel'], fontsize=common_settings['font_size'])
        axes[i, j].legend(prop={'size': common_settings['legend_fsize']})
        axes[i, j].set_title(f'{name}', fontsize=common_settings['font_size'])

    # Remove any empty subplots
    if empty_lims != (0, 0):
        for i, j in itertools.product(range(empty_lims[0], n_rows), range(empty_lims[1], n_cols)):
            axes[i, j].remove()

    plt.tight_layout()

    if 'title' in common_settings:
        fig.suptitle(common_settings['title'])

    return fig, axes


# TODO(Alex) This is generic, and could be moved to plotting
def bar_plot(systems: List[str], fields: List[dict], width=0.27, bar_labels=None, title=''):
    """ Plot several bar plots (one per field) for each system

    Adapted from this reference:
    https://stackoverflow.com/questions/14270391/how-to-plot-multiple-bars-grouped

    :param systems:
    :param fields:
    :param width:
    :return:
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x_dummy = np.arange(len(systems))  # the x locations for the systems
    ax.set_title(title)

    plots = []
    field_labels = []
    for i, field in enumerate(fields):
        data = field.pop('data')
        label = field.pop('label')
        # Plot a bar chart for single field, for all systems
        plot = ax.bar(x_dummy + (i * width), data, width, **field)
        plots.append(plot)
        field_labels.append(label)

    ax.set_ylabel('Time (s)')
    ax.set_xticks(x_dummy + ((len(fields) - 1) * 0.5 * width))
    ax.set_xticklabels(systems)
    ax.legend(plots, field_labels)

    if bar_labels is None:
        return

    # Add N SCF iterations as labels. Want plots 0 and 1
    for labels_for_field in bar_labels:
        ifield = labels_for_field['field']
        labels = labels_for_field['labels']
        assert len(labels) == len(systems)
        # For a given field, loop over each bar of the plot
        # i.e iterate over all systems contributing data to this field
        for i, bar in enumerate(plots[ifield]):
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, labels[i], ha='center', va='bottom')

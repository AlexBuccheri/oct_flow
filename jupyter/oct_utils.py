""" Utilities for parsing data
"""
import math
from pathlib import Path
import numpy as np
from typing import List
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


def parse_convergence_calculations(subdirs: List[str], columns=None) -> dict:
    """ Parse data from convergence files into a dictionary.

    Generality of routine broken by `mixer` key, which is specific to
    preconditioning calculations.

    :param subdirs: List of calculation directories. Expect the full path
    :param columns: Optional list of columns to return. Defaults to relative
    change in density.
    :return: system_calcs: Dict with keys of system names, and values
    = {'mixer': 'mixer', 'data': np.ndarray}
    """
    if columns is None:
        columns = [0, 4]

    system_calcs = {}

    for subdir in map(Path, subdirs):
        if not subdir.is_dir():
            raise NotADirectoryError(f'Cannot find {subdir.as_posix()}')
        # Note, this is also not general, but specific to my naming convention
        subnames = Path(subdir).name.split('_')
        mixer = subnames.pop()
        system_name = "".join(s + '_' for s in subnames)[:-1]

        data = np.loadtxt(Path(subdir, 'static/convergence'), skiprows=1)
        system_calcs[system_name] = {'mixer': mixer, 'data': data[:, columns]}

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


# TODO(Alex) This is generic, and could be moved
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

""" Utilities for parsing data
"""
from pathlib import Path
import numpy as np


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

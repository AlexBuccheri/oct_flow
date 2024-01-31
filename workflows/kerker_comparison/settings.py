""" Settings

Configuration file in python rather than YAML or TOML, much like the NOX package approach
"""
import re

from octopus_workflows.oct_parse import parse_oct_input


def file_to_oct_dict(file) -> dict:
    """ Convert a file string to Octopus inputs
    Always has to return a dict with a valid key:value

    No subs are done, as we do not manipulate the input files (and it's not reliable due to the regex)
    This means an entry like ""O" | u | u | 0.0" will be stored as a string, and never converted
    to/from floats. This is fine, as the workflow does no manipulation of atomic positions.
    :return:
    """
    with open(file, mode='r') as fid:
        structure_string = fid.read()
    return parse_oct_input(structure_string, do_substitutions=False)


# Fixed options, used for all calculations
fixed_options = {'CalculationMode': 'gs',
                 'ExperimentalFeatures': 'yes',
                 'RestartWrite': 'No',
                 'ProfilingMode': 'prof_time',
                 # Solver
                 'MaximumIter': 200,
                 'Eigensolver': 'chebyshev_filter',
                 'EigensolverTolerance': 1.e-7,
                 'ChebyshevFilterDegree': 30,
                 'ExtraStatesInPercent': 25,
                 'MixingScheme': 'broyden'
                 # Grid should be entirely specified in the benchmark structure settings
                 }

# Kerker-specific operations
kerker_options = {'MixField': 'density',
                  'MixingKerker': 'yes',
                  'MixingKerkerFactor': '1.0',  # Default 1.0
                  'Mixing': '0.3'}  # Default 0.3

meta_key = "^"
meta_value_ops = {'^system_files': file_to_oct_dict}
benchmark_root = "/Users/alexanderbuccheri/Codes/cell_building/data/benchmark_structures/"


# Job permutations.
matrix = {'^system_files': ["1ALA", "2ALA", "2Dharmonic", "3ALA", "4ALA", "ASC", "Cr3", "Fe_cubic",
                            "Fe_primitive", "N_GNF", "NiO", "Si", "Si001_1x1_2H", "TiO2",
                            "WSe2", "benzene", "beta-cyclodextrin", "betaine", "methane", "oxyluciferin",
                            "polyFePc", "tetraazacubane"],
          }


# Prepend with benchmark root
matrix['^system_files'] = [benchmark_root + name for name in matrix['^system_files']]


def find_pseudopotential(input_string: str) -> dict:
    """ For input strings that depend on .UPF,
    return the specific .UPF locations.

    Function must define location of existing files
    """
    location = {'Ti.UPF': "data/benchmark_structures/Ti.UPF",
                "O.UPF": "data/benchmark_structures/O.UPF",
                "Cr.UPF": "data/benchmark_structures/Cr.UPF"
                }
    pattern = re.compile(r'"([^"]+\.UPF)"')
    files = pattern.findall(input_string)
    return {f: location[f] for f in files}


file_rules = [find_pseudopotential]

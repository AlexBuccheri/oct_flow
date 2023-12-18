""" Settings

TODO(Alex)
Need some exception behaviour where for specific systems, the workflow copies the pseudos

* Given the final processed input dict - specific some info in that one can identify the system from
* OR define the behaviour for unique job ids

"""
from octopus_workflows.oct_parse import parse_oct_input


def file_to_oct_dict(file) -> dict:
    """ Convert a file string to Octopus inputs
    Always has to return a dict with a valid key:value
    No subs are done, as we do not manipulate the input files (and it's not reliable due to the regex)
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
                 # Grid should be entirely specified in the benchmark structure settings
                 }

# Kerker-specific operations
kerker_options = {'MixField': 'potential',
                  'MixingKerker': 'yes',
                  'MixingKerkerFactor': '1.0',  # Default
                  'Mixing': '0.3'}  # Default

meta_key = "^"
meta_value_ops = {'^system_files': file_to_oct_dict}
benchmark_root = "/Users/alexanderbuccheri/Codes/cell_building/data/benchmark_structures/"

# Job permutations.
matrix = {'^system_files': [benchmark_root + 'TiO2'],
          'MixingScheme': ['linear', 'broyden']}

# If input matches x , i.e. species_pseudo has a file section that contains "*.UPF", easy - regex the final string
# copy from benchmark_root/*.UPF to destination/*.UPF
# Ah, a better thing would be if input matches, create an addition to the depends-on field:
# {'depends-on': {'source': 'path/2/source', 'destination': 'path/2/copy/location'}
# Then handle depends-on in main.py. Should supply a function that actually handles the jobs dict container
def find_pseudopotential():
    """
    Given a species block like:
    "Ti" | species_pseudo | file | "Ti.UPF" | hubbard_l | 2 | hubbard_u | 0.0
    stored as
    [['"Ti"', 'species_pseudo', 'file', '"Ti.UPF"', 'hubbard_l', '2', 'hubbard_u', '0.0'],
    ['"O"', 'species_pseudo', 'file', '"O.UPF"', 'hubbard_l', '1', 'hubbard_u', '0.0']]

    Note where the UPF files are and where to copy them to
    :return:


    Actually looks like this whole parsing of species, reduced ordinates etc
    """

    pass

file_rules = {'upf': find_pseudopotential()}
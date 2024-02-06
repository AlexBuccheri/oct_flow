import re

import pytest

from src.octopus_workflows.components import set_job_file_dependencies, directory_generation
from workflows.kerker_comparison.settings import find_pseudopotential



def test_set_job_file_dependencies():

    inp_string = """PeriodicDimensions = 3
BoxShape = parallelepiped
XCFunctional = gga_x_pbe + gga_c_pbe
aCell = 4.594*Angstrom
bCell = 4.594*Angstrom
cCell = 2.959*Angstrom
KPointsUseSymmetries = no
u = 0.305
Spacing = 0.3
SpinComponents = polarized
%Species
"Ti" | species_pseudo | file | "Ti.UPF" | hubbard_l | 2 | hubbard_u | 0.0
"O" | species_pseudo | file | "O.UPF" | hubbard_l | 1 | hubbard_u | 0.0
%
%LatticeParameters
aCell | bCell | cCell
%
%LatticeVectors
1.0 | 0.0 | 0.0
0.0 | 1.0 | 0.0
0.0 | 0.0 | 1.0
%
%ReducedCoordinates
"Ti" | 0.0 | 0.0 | 0.0
"Ti" | 0.5 | 0.5 | 0.5
"O" | u | u | 0.0
"O" | 1-u | 1-u | 0.0
"O" | 1/2+u | 1/2-u | 1/2
"O" | 1/2-u | 1/2+u | 1/2
%
%KPointsGrid
2 | 2 | 2
%
#ParKPoints = 8
"""

    # Define a file matching rule
    def find_pseudopotential(input_string: str) -> dict:
        """ Match any *.UPF
        Function must define location of existing files
        """
        location = {'Ti.UPF': "data/benchmark_structures/Ti.UPF",
                          "O.UPF": "data/benchmark_structures/O.UPF"
                         }
        pattern = re.compile(r'"([^"]+\.UPF)"')
        files = pattern.findall(input_string)
        return {f: location[f] for f in files}

    ref_files = {'Ti.UPF': {'source': 'data/benchmark_structures/Ti.UPF',
                            'dest': 'new/location/Ti.UPF'
                            },
                 'O.UPF': {'source': 'data/benchmark_structures/O.UPF',
                           'dest': 'new/location/O.UPF'
                           }
                 }
    files = set_job_file_dependencies(inp_string, "new/location", [find_pseudopotential])
    assert files == ref_files

    # No matches
    inp_string = "Dummy string - will not match"
    files = set_job_file_dependencies(inp_string, "new/location", [find_pseudopotential])
    assert files == {}


def test_directory_generation():
    """
    Create directory names from each permutation of dict values
    """
    matrix = {'^system_files': ['benchmark_structures/1ALA'],
              'MixingKerkerFactor': [1.0, 2.0],
              'Mixing': [0.3]
              }
    expected_dir_names = ['1ALA_1.0_0.3', '1ALA_2.0_0.3']
    dir_names = directory_generation(matrix)
    assert dir_names == expected_dir_names

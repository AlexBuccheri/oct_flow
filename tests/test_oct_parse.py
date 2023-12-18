import pytest

from src.octopus_workflows.oct_parse import parse_oct_input, parse_oct_input_string


@pytest.fixture()
def inp_file() -> str:
    input = """
    PeriodicDimensions = 2
    BoxShape = parallelepiped
    KPointsUseSymmetries = no
    a = 10.26120

    %LatticeParameters
    a/sqrt(2) | a/sqrt(2) | a
    %

    %LatticeVectors
    1.0 | 0.0 | 0.0
    0.0 | 1.0 | 0.0
    0.0 | 0.0 | 10.0
    %

    %Spacing
    0.45 | 0.45 | 0.35
    %

    %KPointsGrid
    2 | 2 | 1
    %
    %Coordinates
    "H"  | -7.614776392008550e+00 | 0.000000000000000e+00 | -3.108956374400000e+01
    "H"  | -3.268869762658550e+00 | 0.000000000000000e+00 | -3.108956374400000e+01
    "Si" | -5.441823077333550e+00 | 0.000000000000000e+00 | -2.933590080400000e+01
    "Si" | -5.441823077333550e+00 | 3.627882051555700e+00 | -2.684439934300000e+01
    "Si" | -1.813941025777850e+00 | 3.627882051555700e+00 | -2.430715492340000e+01
    "Si" | -1.813941025777850e+00 | 0.000000000000000e+00 | -2.177268432930000e+01
    "H"  | -3.986894340452850e+00 | 0.000000000000000e+00 | 3.108956374400000e+01
    "H"  | 3.590122888971500e-01  | 0.000000000000000e+00 | 3.108956374400000e+01
    %
    """
    return input


def test_parse_oct_input_string(inp_file):
    """Parse keys and values as strings
    """
    key_values, blocks = parse_oct_input_string(inp_file)
    input = {**key_values, **blocks}
    ref_input = {'PeriodicDimensions': '2',
            'BoxShape': 'parallelepiped',
            'KPointsUseSymmetries': 'no',
            'a': '10.26120',
            'LatticeParameters': ['a/sqrt(2)', 'a/sqrt(2)', 'a'],
            'LatticeVectors': [['1.0', '0.0', '0.0'], ['0.0', '1.0', '0.0'], ['0.0', '0.0', '10.0']],
            'Spacing': ['0.45', '0.45', '0.35'], 'KPointsGrid': ['2', '2', '1'],
            'Coordinates': [['H', '-7.614776392008550e+00', '0.000000000000000e+00', '-3.108956374400000e+01'],
                            ['H', '-3.268869762658550e+00', '0.000000000000000e+00', '-3.108956374400000e+01'],
                            ['Si', '-5.441823077333550e+00', '0.000000000000000e+00', '-2.933590080400000e+01'],
                            ['Si', '-5.441823077333550e+00', '3.627882051555700e+00', '-2.684439934300000e+01'],
                            ['Si', '-1.813941025777850e+00', '3.627882051555700e+00', '-2.430715492340000e+01'],
                            ['Si', '-1.813941025777850e+00', '0.000000000000000e+00', '-2.177268432930000e+01'],
                            ['H', '-3.986894340452850e+00', '0.000000000000000e+00', '3.108956374400000e+01'],
                            ['H', '3.590122888971500e-01', '0.000000000000000e+00', '3.108956374400000e+01']]
            }
    assert input == ref_input


def test_parse_oct_input(inp_file):
    """Parse keys and values as data
    """
    # No substitution of variables
    ref_input = {'PeriodicDimensions': 2.0,
                 'BoxShape': 'parallelepiped',
                 'KPointsUseSymmetries': 'no',
                 'a': 10.2612,
                 'LatticeParameters': ['a/sqrt(2)', 'a/sqrt(2)', 'a'],
                 'LatticeVectors': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 10.0]],
                 'Spacing': [0.45, 0.45, 0.35],
                 'KPointsGrid': [2.0, 2.0, 1.0],
                 'Coordinates': [['H', -7.61477639200855, 0.0, -31.089563744],
                                 ['H', -3.26886976265855, 0.0, -31.089563744],
                                 ['Si', -5.44182307733355, 0.0, -29.335900804],
                                 ['Si', -5.44182307733355, 3.6278820515557, -26.844399343],
                                 ['Si', -1.81394102577785, 3.6278820515557, -24.3071549234],
                                 ['Si', -1.81394102577785, 0.0, -21.7726843293],
                                 ['H', -3.98689434045285, 0.0, 31.089563744],
                                 ['H', 0.35901228889715, 0.0, 31.089563744]]
                 }
    input = parse_oct_input(inp_file, do_substitutions=False)
    assert input == ref_input

    # Parse and perform substitution of variables
    # Note, one still does not evaluate the mathematical expressions
    ref_input['LatticeParameters'] = ['10.26120/sqrt(2)', '10.26120/sqrt(2)', 10.2612]
    input = parse_oct_input(inp_file, do_substitutions=True)
    assert input == ref_input

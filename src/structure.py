""" Convert Octopus-formatted structure input to ASE Atoms, and vice versa.
"""
import re
from typing import Tuple, List

import ase
import numpy as np
import scipy.linalg
from sympy.parsing.sympy_parser import parse_expr

bohr_to_ang = 0.52917721092
ang_to_bohr = 1. / bohr_to_ang


def parse_key_value_pairs(input:str) -> dict:
    """ Parse key-value blocks from Octopus input files.

    Key-values are defined as key = value.

    :param input: Octopus input file string.
    :return: Dict of key-value pairs from Octopus input.
    Values are returned as strings.
    """
    input_dict = {}

    # Grab all key = value instances
    pattern = r'([^=]+)=(.+)'

    # Search for the substring
    matches = re.findall(pattern, input)
    for match in matches:
        key = match[0].strip()
        value = match[1].strip()
        input_dict[key] = value

    return input_dict


def parse_block(input: str, key: str) -> list:
    """ Parse a block from an Octopus input file string.

    Blocks are defined as:

    ```
    %Key
    x | y | z
    %
    ```

    with entries separated by "|". Blocks can be multiple lines/

    :param input: Octopus input file string.
    :param key: Key of the block (see above).
    :return: block: List, with len n_lines, where each element contains
     a line of the parsed block. BLock lines returned as strings.
    """
    block = []
    match = re.search(rf'%{key}(.*?)%', input, re.DOTALL)
    if match:
        # Strip whitespace and split w.r.t. line breaks
        string = match.group(1).strip().replace(" ", "").split('\n')

        # Single line blocks
        if len(string) == 1:
            return [i for i in string[0].split('|')]

        # Multi-line blocks
        else:
            for line in string:
                block.append([i for i in line.split('|')])

    return block


def parse_oct_input_string(input: str) -> Tuple[dict, dict]:
    """

    This returns the input file options as strings, having not
    done any recursive substitution on them

    :param input:
    :return:
    """
    key_values = parse_key_value_pairs(input)

    blocks = {}
    for key in ['LatticeVectors', 'LatticeParameters', 'Spacing', 'KPointsGrid', 'Coordinates']:
        blocks[key] = parse_block(input, key)

    # Clean up species quotations
    coordinates = []
    for entry in blocks['Coordinates']:
        coordinates.append([x.replace("\"", '') for x in entry])
    blocks['Coordinates'] = coordinates

    return key_values, blocks


def parse_oct_dict_to_values(key_values: dict, blocks: dict) -> dict:
    """
    Do recursive substitution on the values, according to matching
    with prior keys
    Convert from strings to numbers where appropriate


    :param options:
    :return:
    """
    # Function to recursively apply re.sub for all elements of lists/nested lists
    # Will not work for non-lists (silently gives wrong result), hence try/except
    # block in body of `parse_oct_dict_to_values` double-loop
    def recursive_modify(lst, key: str, replace_val):
        for i, item in enumerate(lst):
            if isinstance(item, list):
                recursive_modify(item, key,replace_val)
            else:
                lst[i] = re.sub(rf'{key}', replace_val, item)

    # key-values from input
    for key, var_val in key_values.items():
        # blocks, which should not define variables, only use variables
        for key2, block_val in blocks.items():
            if not isinstance(block_val, list):
                blocks[key2] = re.sub(rf'{key}', var_val, block_val)
            else:
                recursive_modify(block_val, key, var_val)

    return {**key_values, **blocks}


def eval_string(value):
    """

    :param value:
    :param no_convert:
    :return:
    """
    try:
        float(value)
        return float(value)
    except (TypeError, ValueError):
        return value


def evaluate_strings(options: dict) -> dict:
    """

    Essentially run this on specific keys once the dict is parsed,
    as sympy is too aggressive. i.e. 'H' gets converted to a Symbol,
    parallelepiped gets converted to a Symbol, etc.

    :param options:
    :return:
    """
    # Function to recursively apply eval_string for all elements of lists/nested lists
    # Will not work for non-lists (silently gives wrong result)
    def recursive_eval(lst):
        for i, item in enumerate(lst):
            if isinstance(item, list):
                recursive_eval(item)
            else:
                lst[i] = eval_string(item)

    # Keys that should not be interpreted as symbolic
    # no_convert = {sympy.symbols('no'): 'no', sympy.symbols('H'): 'H'}

    for key in options.keys():
        if not isinstance(options[key], list):
            options[key] = eval_string(options[key])
        else:
            recursive_eval(options[key])

    return options


def parse_oct_input(input: str, do_substitutions=True) -> dict:
    """ Top level parser routine for Ocotpus input file.

    :param input:
    :param do_substitutions: Substitute variable definitions in strings
    and evaluate strings, converting to float where appropriate.
    Note, this does not evaluate mathematical expressions
    :return:
    """
    key_values, blocks = parse_oct_input_string(input)
    if do_substitutions:
        options = parse_oct_dict_to_values(key_values, blocks)
        return evaluate_strings(options)
    else:
        return {**key_values, **blocks}


def evaluate_expressions(options: dict, keys: str | List[str], expressions: dict) -> dict:
    """

    :param options:
    :param keys:
    :param expressions:
    :return:
    """
    def recursive_eval(lst, local_dict):
        for i, item in enumerate(lst):
            if isinstance(item, list):
                recursive_eval(item, local_dict)
            else:
                try:
                    lst[i] = parse_expr(item, local_dict=expressions).evalf()
                except (AttributeError, TypeError, ValueError, SyntaxError):
                    pass

    if type(keys) == str:
        keys = [keys]

    for key in keys:
        if isinstance(options[key], list):
            recursive_eval(options[key],expressions)
        else:
            options[key] = parse_expr(options[key], local_dict=expressions).evalf()

    return options


def unit_vector(a):
    return np.asarray(a) / scipy.linalg.norm(a)


def parse_oct_structure_to_atoms(options: dict) -> ase.atoms.Atoms:
    """

    Lattice vectors stored rowwise.

    :param options:
    :return:
    """

    # Get cell angles from the lattice vectors
    lattice_vectors = options['LatticeVectors']
    n_dim = len(lattice_vectors)

    assert n_dim == 3, "Calculation of angles between lattice vectors only coded for 3D systems"

    lattice_angles = []
    for i in range(0, n_dim):
        j = (i + 1) % n_dim
        angle = np.arccos(np.dot(unit_vector(lattice_vectors[i]), unit_vector(lattice_vectors[j])))
        lattice_angles.append(np.degrees(angle))

    lattice_parameters = [x * bohr_to_ang for x in options['LatticeParameters']]

    # TODO(Alex) No idea what convention they're using
    # Multiply each lattice parameter by norm of each lattice vector
    for i in range(0, n_dim):
        lattice_parameters[i] *= scipy.linalg.norm(lattice_vectors[i])

    # TODO(Alex) User can specify input units - would need to check for those.
    #  Yes/No can be appended to the end of a Coordinate line - would need to check for that too
    # Convert units
    positions = []
    #  Need shift the atomic positions. Is this a problem for Octopus?
    origin = np.array([r * bohr_to_ang for r in options['Coordinates'][0][1:]])
    for entry in options['Coordinates']:
        positions.append(np.array([r * bohr_to_ang for r in entry[1:]]) - origin)

    atoms = ase.atoms.Atoms(symbols=[entry[0] for entry in options['Coordinates']],
                            positions=positions,
                            pbc=True
                            )

    # If cell is six numbers, assume three lengths, then three angles.
    atoms.set_cell(lattice_parameters + lattice_angles, scale_atoms=False)

    return atoms


def ase_atoms_to_oct_structure(atoms: ase.atoms.Atoms, fractional=True) -> str:
    """ Convert ASE Atoms instance to Octopus input substring for:
    LatticeVectors and Coordinates, noting that LatticeParameters
    are absorbed in the LatticeVectors.

    :param atoms: Atoms instance.
    :return: input_string: Structure substring
    """
    input_string = ""

    # LatticeParameters
    constants_and_angles = atoms.cell.cellpar()
    constants = np.asarray(constants_and_angles[0:3]) * ang_to_bohr
    input_string += "%LatticeParameters\n"
    input_string += " ".join(f"{constant} |" for constant in constants[0:3])[:-1] + '\n'
    input_string += "%\n"

    # LatticeVectors (row-wise in ASE, and Octopus input)
    lattice = atoms.get_cell().array * ang_to_bohr
    n_vectors, n_components = len(lattice), len(lattice[0])

    # Define origin before dividing through by lattice constants
    origin = np.zeros(shape=n_components)
    for i in range(0, n_vectors):
        origin[:] += 0.5 * np.asarray(lattice[i, :])

    # Divide lattice vectors by respective parameters
    lattice = [v / constants[i] for i, v in enumerate(lattice)]

    input_string += "%LatticeVectors\n"
    for vector in lattice:
        input_string += " ".join(f"{r:.9f} |" for r in vector)[:-1] + '\n'
    input_string += "%\n"

    # Coordinates
    species = atoms.get_chemical_symbols()

    # Note that in Octopus the origin of coordinates is in the center of the cell,
    if fractional:
        # The coordinates inside the cell are in the range [-0.5, 0.5)
        key = 'ReducedCoordinates'
        fractional_origin = np.array([0.5, 0.5, 0.5])
        positions = np.asarray(atoms.get_scaled_positions()) - fractional_origin
    else:
        key = 'Coordinates'
        positions = np.asarray(atoms.get_positions()) * ang_to_bohr - origin
    n_atoms = len(species)

    # Pad with trailing whitespace, to achieve alignment when printing
    unique_species = set(species)
    max_len = len(max(unique_species))
    pad = lambda x: " " * (max_len - len(x))
    whitespace = [pad(x) for x in species]

    input_string += f"%{key}\n"
    for i in range(0, n_atoms):
        line = f"\"{species[i]}\"{whitespace[i]} | " + " ".join(f"{r:.18e} |" for r in positions[i])[:-1]
        input_string += line + '\n'
    input_string += "%\n"

    return input_string


def write_octopus_input(options: dict) -> str:
    """
    TODO(Alex) Could make this more readable and reduce the loops
    :param options:
    :return:
    """
    input = ""

    for key, value in options.items():
        if isinstance(value, list):
            input += f"%{key}\n"
            # Nested list (note, do not expect more than one level of nesting)
            if isinstance(value[0], list):
                for v in value:
                    input += " ".join(f"{s} |" for s in v)[:-1] + "\n"
            # Single list
            else:
                input += " ".join(f"{s} |" for s in value)[:-1] + "\n"
            input += "%\n"
        else:
            input += f"{key} = {value}\n"

    return input

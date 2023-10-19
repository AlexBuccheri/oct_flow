""" Convert Octopus-formatted structure input to ASE Atoms, and vice versa.
"""
import re
from typing import List, Tuple

import ase
from sympy.parsing.sympy_parser import parse_expr
import sympy


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


def parse_coordinates(input: str) -> tuple:
    """ Parse Coordinates block from Octopus input string.

    Defined as special function, but this could also be handled by `parse_block`
    and return [["Si", '0', '0', '0'], ["Si", '0.25', '0.25', '0.25']] for example.

    :param input: Octopus input file string.
    :return: species, positions: Lists of species and positions, respectively.
    """
    species = []
    positions = []
    match = re.search(r'%Coordinates(.*?)%', input, re.DOTALL)
    if match:
        # Strip whitespace and split w.r.t. line breaks
        coords_string = match.group(1).strip().replace(" ", "").split('\n')

        # Fill species and positions
        species = []
        positions = []
        for line in coords_string:
            tmp = line.split('|')
            species.append(tmp[0])
            positions.append([float(r) for r in tmp[1:]])

    return species, positions


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

    # Parsing with `parse_block` instead
    # Special structure
    # Shouldn't have this here, as coordinates are already float
    # blocks['Species'], blocks['Coordinates'] = parse_coordinates(input)

    return key_values, blocks


def eval_string(value, explicit_def=None):
    """

    :param value:
    :param no_convert:
    :return:
    """
    # State explicit conversions for sympy
    if explicit_def is None:
        explicit_def = {}

    try:
        float(value)
        return float(value)
    except (TypeError, ValueError):
        try:
            value = parse_expr(value, locals=explicit_def).evalf()
            return value
        except (TypeError, ValueError, SyntaxError):
            return value


def parse_oct_input(key_values: dict, blocks: dict) -> dict:
    """
    Do recursive substitution on the values, according to matching
    with prior keys
    Convert from strings to numbers



    :param options:
    :return:
    """

    # This DOES NOT works for values that are not lists
    def recursive_modify(lst, key: str, replace_val):
        for i, item in enumerate(lst):
            if isinstance(item, list):
                recursive_modify(item, key,replace_val)
            else:
                lst[i] = re.sub(rf'{key}', replace_val, item)

    # key-values
    for key, var_val in key_values.items():
        # blocks, which should not define variables, only use variables
        for key2, block_val in blocks.items():
            if not isinstance(block_val, list):
                blocks[key2] =  re.sub(rf'{key}', var_val, block_val)
            else:
                recursive_modify(block_val, key, var_val)

    # TODO(Alex) Split this into a separate routine
    # Unfortunately need another pass to evaluate expressions
    def recursive_eval(lst):
        for i, item in enumerate(lst):
            if isinstance(item, list):
                recursive_eval(item)
            else:
                lst[i] = eval_string(item)

    # Keys that should not be interpretted as symbolic
    no_convert={sympy.symbols('no'): 'no'}

    options = {**key_values, **blocks}

    for key in options.keys():
        if not isinstance(options[key], list):
            options[key] = eval_string(options[key], explicit_def=no_convert)
        else:
            recursive_eval(options[key])

    return options





def parse_oct_structure(options: dict) -> ase.atoms.Atoms:

    # TODOs(Alex)
    # Need to multiply lattice vectors by lattice Parameters
    # check the logic for this, and if lattice vectors are row wise (assume so)
    # Convert Bohr to Angstrom
    # Assume Coordinates in Bohr - check
    atoms = ase.atoms.Atoms(symbols= options['Species'],
                            positions=options['Coordinates'],
                            cell=options['LatticeVectors'],
                            pbc=True
                            )


    return





def ase_atoms_to_oct_structure(atoms: ase.atoms.Atoms) -> str:
    """

    :param atoms:
    :return:
    """

    # Get lattice vectors

    # Get lattice parameters from the vectors. Look like Bohr

    # 'Species', Position in Ang or bohr?

    struct_input = ""
    return struct_input
""" Convert Octopus-formatted structure input to ASE Atoms, and vice versa.
"""
import re
from typing import List, Tuple

import ase
from sympy.parsing.sympy_parser import parse_expr
import sympy

def parse_key_value_pairs(input:str) -> dict:
    """

    :param input:
    :return:
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


def parse_block(input:str, key: str) -> list:
    """
    In principle, should parse as strings,
    then do the substitution as below
    :param input:
    :param pattern:
    :return: List of strings
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
    """

    :return:
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
    for key in ['LatticeVectors', 'LatticeParameters', 'Spacing', 'KPointsGrid']:
        blocks[key] = parse_block(input, key)

    # Special structure
    # Shouldn't have this here, as coordinates are already float
    # blocks['Species'], blocks['Coordinates'] = parse_coordinates(input)

    return key_values, blocks


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
                print('element', item)
                try:
                    lst[i] = float(item)
                    print('float', item, float(item))
                except (TypeError, ValueError):
                    try:
                        lst[i] = parse_expr(item).evalf()
                    except (TypeError, ValueError, SyntaxError):
                        return


    options = {**key_values, **blocks}
    # Keys that should not be interpretted as symbolic
    no_convert={sympy.symbols('no'): 'no'}


    for key in options.keys():
        if not isinstance(options[key], list):
            try:
                options[key] = float(options[key])
            except (TypeError, ValueError):
                try:
                    # Note, this converts 'no' to a sympy object, which I don't want to do
                    options[key] = parse_expr(options[key], locals=no_convert).evalf()
                except (TypeError, ValueError, SyntaxError):
                    pass
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
"""

"""
import re
from typing import List, Tuple

from sympy.parsing.sympy_parser import parse_expr


def parse_key_value_pairs(input: str) -> dict:
    """Parse key-value blocks from Octopus input files.

    Key-values are defined as key = value.

    :param input: Octopus input file string.
    :return: Dict of key-value pairs from Octopus input.
    Values are returned as strings.
    """
    input_dict = {}

    # Grab all key = value instances
    pattern = r"([^=]+)=(.+)"

    # Search for the substring
    matches = re.findall(pattern, input)
    for match in matches:
        key = match[0].strip()
        value = match[1].strip()
        input_dict[key] = value

    return input_dict


def parse_block(input: str, key: str) -> list:
    """Parse a block from an Octopus input file string.

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
    match = re.search(rf"%{key}(.*?)%", input, re.DOTALL)
    if match:
        # Strip whitespace and split w.r.t. line breaks
        string = match.group(1).strip().replace(" ", "").split("\n")

        # Single line blocks
        if len(string) == 1:
            return [i for i in string[0].split("|")]

        # Multi-line blocks
        else:
            for line in string:
                block.append([i for i in line.split("|")])

    return block


def parse_oct_input_string(input: str) -> Tuple[dict, dict]:
    """

    This returns the input file options as strings, having not
    done any recursive substitution on them

    :param input:
    :return:
    """
    key_values = parse_key_value_pairs(input)

    # Definition of a block
    # match % followed by one or more word characters (letters, digits, or underscores)
    block_keys = re.findall(r'%(\w+)', input)
    blocks = {key:parse_block(input, key) for key in block_keys}

    # Clean up species quotations
    coordinates = []
    for entry in blocks["Coordinates"]:
        coordinates.append([x.replace('"', "") for x in entry])
    blocks["Coordinates"] = coordinates

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
                recursive_modify(item, key, replace_val)
            else:
                lst[i] = re.sub(rf"{key}", replace_val, item)

    # key-values from input
    for key, var_val in key_values.items():
        # blocks, which should not define variables, only use variables
        for key2, block_val in blocks.items():
            if not isinstance(block_val, list):
                blocks[key2] = re.sub(rf"{key}", var_val, block_val)
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
    """Top level parser routine for Octopus input file.

    Note, [units](https://www.octopus-code.org/documentation/13/variables/execution/units/units/)
    won't get substituted. For example 'Spacing': '0.2*angstrom' where angstrom is the unit.

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


def evaluate_expressions(
    options: dict, keys: str | List[str], expressions: dict
) -> dict:
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
            recursive_eval(options[key], expressions)
        else:
            options[key] = parse_expr(
                options[key], local_dict=expressions
            ).evalf()

    return options

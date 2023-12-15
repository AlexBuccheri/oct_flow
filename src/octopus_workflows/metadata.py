""" Metadata
"""
import hashlib
from typing import List


def create_hash(input_string: str):
    """Generate a unique hash from any input file string.

    :param input_string:
    :return:
    """
    # Strip all whitespace and terminating characters from the string
    stripped_input = (
        input_string.replace("\t", "").replace("\n", "").replace(" ", "")
    )
    sha256_hash = hashlib.sha256()
    sha256_hash.update(stripped_input.encode("utf-8"))
    # hexadecimal representation of the hash value
    hashed_string = sha256_hash.hexdigest()
    return hashed_string


def create_hashes(input_strings: List[str]):
    return [create_hash(input_str) for input_str in input_strings]


def generate_config_data(options_dicts: List[dict], inputs: List[str]) -> dict:
    """

    Generate a file index and also a set of unique settings, and a hash.
    This will a) make it easier when parsing data for plotting and
    b) avoid having to create some directory naming convention based on the
    unique input options, like:

    eig-rmm_eig_1e-7_file-1AL

    1:
      -  Eigensolver: rmmdiis
      -  EigensolverTolerance: 1e-7
      -  File: 1ALA
      -  input_hash: ojj9uotrreji
    2:
      -  Eigensolver: rmmdiis
      -  EigensolverTolerance: 1e-7
      -  File: 2ALA
      -  input_hash: 3u84jfio4390
    ...

    :param options_dicts:
    :return:
    """
    assert len(options_dicts) == len(inputs)
    config = {}

    for i, options in enumerate(options_dicts):
        config[i] = options
        config[i].update({"input_hash": create_hash(inputs[i])})

    return config

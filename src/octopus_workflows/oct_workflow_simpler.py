""" Octopus workflow without ASE

Once working, move out the functions
"""
import copy
from typing import Callable, Dict, List

from octopus_workflows.components import expand_input_dictionary


def substitute_specific_settings(inputs: List[dict], meta_value_ops: Dict[str, Callable], meta_key: str):
    """

    Operation should be a function that returns a dict of valid Octopus key:values
    :return:
    """
    for input in inputs:
        # Find keys that start with the meta-key
        meta_keys = [key for key in input if key.startswith(meta_key)]
        for key in meta_keys:
            operation = meta_value_ops[key]
            placeholder = input[key]
            actual_key_value: dict = operation(placeholder)
            input.pop(key)
            input.update(copy.deepcopy(actual_key_value))
    return inputs



# Second iteration, where only a meta-key tag is specified
def ground_state_calculation(matrix: dict,
                             static_options: dict,
                             meta_value_ops: dict,
                             slurm_settings: dict,
                             binary_path,
                             meta_key='^') -> dict:
    """ An Octopus Workflow.

    :return:
    """
    # Generate list of input dicts
    inputs = expand_input_dictionary(matrix, static_options)

    # Substitute specific settings
    inputs = substitute_specific_settings(inputs, meta_value_ops, meta_key)
    print(inputs[0])

    # Remove keys used for constructors
    # Should just have a list of Octopus keys, and remove anything not in that list

    # Go from dicts to strings
    # input_strings = inp_string(inputs, ase_inputs)

    # # Unique hashes
    # hashes = create_hashes(input_strings)
    #
    # # Use directory names as job ids
    # job_ids = directory_generation(matrix)
    #
    # # Submission scripts
    # sub_scripts = slurm_submission_scripts(binary_path, slurm_settings, job_ids)
    #
    # # Package information
    # jobs = package_info(job_ids, job_ids, input_strings, sub_scripts, hashes, structures=ase_inputs)

    return {}

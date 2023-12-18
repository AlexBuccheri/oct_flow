""" A more generic Octopus workflow that does not assume ASE
but can still facilitate it.
"""
import copy
from typing import Callable, Dict, List

from octopus_workflows.components import expand_input_dictionary, directory_generation, slurm_submission_scripts
from octopus_workflows.metadata import create_hashes
from octopus_workflows.oct_write import write_octopus_input


def substitute_specific_settings(inputs: List[dict], meta_value_ops: Dict[str, Callable], meta_key: str):
    """
    TODO(Alex) Move this routine
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


def ground_state_calculation(matrix: dict,
                             static_options: dict,
                             meta_key: str,
                             meta_value_ops: dict,
                             slurm_settings: dict,
                             binary_path
                             ) -> dict:
    """ An Octopus Workflow.

     Meta keys are keys with values that require substitution with some specified behaviour
     and then should be removed from the dict following this

    Want to define the substitution behaviour for each meta-key value, to make the workflow more generic
    i.e. could work with ASE or file substitution

    matrix:
    static_options
    : meta_key:
    :return:
    """
    # Generate list of input dicts
    inputs = expand_input_dictionary(matrix, static_options)

    # Substitute specific settings
    inputs = substitute_specific_settings(inputs, meta_value_ops, meta_key)
    print(inputs[0]['Species'])

    # Go from dicts to strings
    input_strings = [write_octopus_input(input) for input in inputs]

    # Note location of any file dependencies
    # TODO ADD ME
    file_dependencies = [None] * len(inputs)

    # Unique hashes
    hashes = create_hashes(input_strings)

    # Use directory names as job ids
    job_ids = directory_generation(matrix)

    # Submission scripts
    sub_scripts = slurm_submission_scripts(binary_path, slurm_settings, job_ids)

    # Package information
    jobs = {}
    for i, id in enumerate(job_ids):
        jobs[id] = {
            "directory": id,
            "inp": input_strings[i],
            "slurm.sh": sub_scripts[i],
            "hash": hashes[i],
            "depends-on": file_dependencies[i]
        }

    return jobs

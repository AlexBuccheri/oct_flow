""" workflow

TODO(Alex) Generalise this workflow
"""
from typing import List

from components import (expand_input_dictionary, ase_bulk_structure_constructor, inp_string,
                        directory_generation, slurm_submission_scripts, package_info, remove_non_octopus_keys,
                        substitute_specific_settings)
from metadata import create_hashes


def ground_state_calculation(matrix: dict,
                             static_options: dict,
                             specific_options: dict,
                             meta_keys: List[str],
                             slurm_settings: dict,
                             binary_path) -> dict:
    """ An Octopus Workflow.

    :return:
    """
    # Generate list of input dicts
    inputs = expand_input_dictionary(matrix, static_options)

    # Substitute specific settings
    inputs = substitute_specific_settings(inputs, specific_options, meta_keys)

    # Pass ASE constructor dict to ASE constructor
    ase_inputs = ase_bulk_structure_constructor(inputs)

    # Remove keys used for constructors
    # Should just have a list of Octopus keys, and remove anything not in that list
    inputs = remove_non_octopus_keys(inputs, meta_keys)

    # Go from dicts to strings
    input_strings = inp_string(inputs, ase_inputs)

    # Unique hashes
    hashes = create_hashes(input_strings)

    # Use directory names as job ids
    job_ids = directory_generation(matrix)

    # Submission scripts
    sub_scripts = slurm_submission_scripts(binary_path, slurm_settings, job_ids)

    # Package information
    jobs = package_info(job_ids, job_ids, input_strings, sub_scripts, hashes, structures=ase_inputs)

    return jobs

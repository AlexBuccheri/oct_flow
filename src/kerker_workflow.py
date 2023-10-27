"""
workflow
TODO(Alex) Workflow should be defined with a plugin system

"""
from components import (expand_input_dictionary, ase_bulk_structure_constructor, inp_string,
                        directory_generation, slurm_submission_scripts, package_info)
from metadata import create_hashes


def ground_state_calculation(matrix: dict,
                             static_options: dict,
                             material_definitions: dict,
                             slurm_settings: dict,
                             binary_path) -> dict:
    """ An Octopus Workflow.

    :return:
    """
    # Generate list of input dicts
    inputs = expand_input_dictionary(matrix, static_options)

    # Pass structure settings to ase constructor
    # Also removes 'material' and 'supercell' keys from inputs
    ase_inputs = ase_bulk_structure_constructor(inputs, material_definitions)

    # Go from dicts to strings
    input_strings = inp_string(inputs, ase_inputs)

    # Unique hashes
    hashes = create_hashes(input_strings)

    # Use directory names as job ids
    job_ids = directory_generation(matrix)

    # Submission scripts
    sub_scripts = slurm_submission_scripts(binary_path, slurm_settings, job_ids)

    # Package information
    jobs = package_info(job_ids, job_ids, input_strings, sub_scripts, hashes)

    return jobs


if __name__ == "__main__":
    from kerker_settings import (matrix, static_options, material_definitions, default_ada_gpu,
                                 kerker_options)

    # Jobs without kerker
    jobs = ground_state_calculation(matrix, static_options, material_definitions, default_ada_gpu, 'path/2/oct')
    print(jobs['Al_cubic_111']['inp'])

    # Jobs with kerker
    # jobs = ground_state_calculation(matrix, {**static_options, **kerker_options} , material_definitions, default_ada_gpu, 'path/2/oct')
    # print(jobs['Al_cubic_111']['inp'])
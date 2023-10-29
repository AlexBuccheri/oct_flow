""" workflow

TODO(Alex) Generalise this workflow
"""
from pathlib import Path

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

    use_kerker = False
    root = 'no_kerker'
    oct_root_ada = '/u/abuc/packages/octopus/_build_kerker/installed'

    if use_kerker:
        root = root.split('_')[-1]
        static_options.update(kerker_options)

    jobs = ground_state_calculation(matrix, static_options, material_definitions, default_ada_gpu, oct_root_ada)

    # Write jobs to file
    for job in jobs.values():
        subdir = Path(root, job['directory'])
        Path.mkdir(subdir, parents=True)

        for file_type, file_name in [('hash', 'metadata.txt'), ('inp', 'inp'), ('submission', 'run.sh')]:
            with open(subdir / file_name, 'w') as fid:
                fid.write(job[file_type])





"""
workflow
TODO(Alex) Workflow should be defined with a plugin system - I.e. it just composes the steps above.

"""
import copy
import datetime
from typing import List

import ase
import simple_slurm

from utils import cartesian_product
from structure import write_octopus_input, ase_atoms_to_oct_structure
from metadata import create_hash


def input_dictionary(matrix: dict, fixed_settings: dict) -> List[dict]:
    """
    Generate an input directory of all option permutations.

    :return:
    """
    permutation_options = cartesian_product(matrix)
    all_options = [{**opt, **fixed_settings} for opt in permutation_options]
    return all_options


def ase_bulk_structure_constructor(inputs: List[dict], material_definitions: dict) -> List[ase.atoms.Atoms]:
    """
    Pass structure dict to appropriate constructor
    :param input:
    :return:
    """
    from ase.build import bulk
    ase_inputs = []
    for system in inputs:
        key = system.pop('material')

        # Bulk cell
        struct_settings = copy.deepcopy(material_definitions[key])
        name = struct_settings.pop('name')
        ase_unit_cell = bulk(name, **struct_settings)

        # Supercell
        supercell = system.pop('supercell')
        scell_integers = [[supercell[0], 0, 0], [0, supercell[1], 0], [0, 0, supercell[2]]]
        ase_supercell = ase.build.make_supercell(ase_unit_cell, scell_integers)

        ase_inputs.append(ase_supercell)

    return ase_inputs


def inp_string(inputs: List[dict], ase_inputs: List[ase.atoms.Atoms]=None) -> List[str]:
    """
    Generate an Octopus input string
    :param input:
    :return:
    """
    if ase_inputs is None:
        struct_strings = [''] * len(inputs)
    else:
        struct_strings = [ase_atoms_to_oct_structure(input) for input in ase_inputs]

    # input_strings = []
    # for input, struct_string in zip(inputs, struct_strings):
    #     input_strings = [write_octopus_input(input) + '\n' + struct_string]

    input_strings = map(lambda x, y: write_octopus_input(x) + '\n' + y, inputs, struct_strings)

    return list(input_strings)




def directory_generation(matrix: dict, prefix='', suffix='') -> List[str]:
    """
    Attach a directory name to each input
    Should use permuted variables to generate a directory name
    - will also be used as the job_id

    :param matrix:
    :param prefix:
    :param suffix:
    :return:
    """
    options = cartesian_product(matrix)
    if prefix != '':
        prefix += '_'
    if suffix != '':
        suffix = f'_{suffix}'

    ids = []
    for opt in options:
        id = ''
        for key, value in opt.items():
            if isinstance(value, str):
                id += value + '_'
            if isinstance(value, float):
                id += str(value) + '_'
            if isinstance(value, list):
                id += "".join(str(s) for s in value)

        if id[:-1] == '_':
            id = id[:-1]
        id = f"{prefix}{id}{suffix}"
        ids.append(id)
    return ids





def slurm_submission_script(oct_root: str, options: dict) -> str:
    """ Default Slurm settings for running converged ground states on ADA

    Note, need double-quotes to allow variable expansion.

    :return: Slurm input file string.
    """
    slurm = simple_slurm.Slurm(**options)

    slurm_str = slurm.__str__()
    modules = "module load gcc/11 openmpi/4 cuda/11.4 openmpi_gpu/4"

    vars = f'export PATH="{oct_root}/bin:${{PATH}}" \n'
    vars += "export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}"
    vars += "export OMP_PLACES=cores"

    srun = "cd ${SLURM_SUBMIT_DIR}\n"
    srun += 'srun octopus > std.out'
    return "\n".join(cmd for cmd in [slurm_str, modules, vars, srun])

def package_info(job_ids: List[str],
                 directories: List[str],
                 inputs: List[str],
                 sub_scripts: List[str],
                 hashes: List[str]):
    """

    :param job_ids:
    :param directories:
    :param inputs:
    :param sub_scripts:
    :param hashes:
    :return:
    """
    jobs = {}
    for i in range(0, len(job_ids)):
        id = job_ids[i]
        jobs[id] = {'directory': directories[i],
                    'inp': inputs[i],
                    'submission': sub_scripts[i],
                    'hash': hashes[i]}

    return jobs


if __name__ == "__main__":
    from kerker_settings import matrix, static_options, kerker_options, material_definitions

    # Generate list of input dicts
    inputs: List[dict] = input_dictionary(matrix, static_options)

    # Pass structure settings to ase constructor
    # Also removes 'material' key from inputs
    ase_inputs: List[ase.atoms.Atoms] = ase_bulk_structure_constructor(inputs, material_definitions)

    # Go from dicts to strings
    input_strings = inp_string(inputs, ase_inputs)

    # Unique hashes
    hashes = [create_hash(inp) for inp in input_strings]

    # Use directory names as job ids
    job_ids = directory_generation(matrix)

    default_ada_gpu = {'nodes': 1,
                       'ntasks_per_node': 4,
                       'cpus_per_task': 18,
                       'partition': 'p.ada',
                       'gres': ['gpu:a100:4'],
                       'ignore_pbs': True,
                       'job_name': 'octopus',
                       'time': datetime.timedelta(days=0, hours=4, minutes=0, seconds=0),
                       'mem': '100G',  # Cluster max: 1000G
                       'mail_type': 'none'}

    # Submission scripts
    sub_scripts = [slurm_submission_script('path/2/octopus',  {**default_ada_gpu, 'job_name': 'oct_{id}'}) for id in job_ids]

    # Package information
    jobs = package_info(job_ids, job_ids, input_strings, sub_scripts, hashes)
    print(jobs['Al_cubic_111']['inp'])


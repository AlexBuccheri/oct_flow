""" Units or components of work that are composed to form a workflow
"""
import copy
from typing import List

import ase
import simple_slurm

from oct_ase import ase_atoms_to_oct_structure
from oct_write import write_octopus_input
from utils import cartesian_product


def expand_input_dictionary(matrix: dict, fixed_settings: dict) -> List[dict]:
    """ Generate an input dict of all option permutations.

    :return:
    """
    permutation_options = cartesian_product(matrix)
    all_options = [{**opt, **fixed_settings} for opt in permutation_options]
    return all_options


def ase_bulk_structure_constructor(inputs: List[dict], material_definitions: dict) -> List[ase.atoms.Atoms]:
    """ Given ASE Atom settings, return a list of Atom instances.

    TODO. Consider splitting loop from single use of constructor

    :param inputs:
    :param material_definitions:
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
    """ Generate a list of Octopus input strings

    :param input:
    :return:
    """
    if ase_inputs is None:
        struct_strings = [''] * len(inputs)
    else:
        struct_strings = [ase_atoms_to_oct_structure(input) for input in ase_inputs]

    input_strings = map(lambda x, y: write_octopus_input(x) + '\n' + y, inputs, struct_strings)

    return list(input_strings)


def directory_generation(matrix: dict, prefix='', suffix='') -> List[str]:
    """Generate a directory name for each input, based on the variables that
    are varied.

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


def slurm_submission_scripts(oct_root: str, options: dict, job_ids: List[str]):
    return [slurm_submission_script(oct_root,  {**options, 'job_name': f'oct_{id}'}) for id in job_ids]


def package_info(job_ids: List[str],
                 directories: List[str],
                 inputs: List[str],
                 sub_scripts: List[str],
                 hashes: List[str]) -> dict:
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
""" A more generic Octopus workflow that does not assume ASE
but can still facilitate it.
"""
import copy
import shutil
from pathlib import Path
from typing import Callable, Dict, List

from octopus_workflows.components import (
    directory_generation,
    expand_input_dictionary,
    set_job_file_dependencies,
    slurm_submission_scripts,
)
from octopus_workflows.metadata import create_hashes
from octopus_workflows.oct_write import write_octopus_input


def substitute_specific_settings(
    inputs: List[dict], meta_value_ops: Dict[str, Callable], meta_key: str
):
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


# TODO(Alex) Move this class
class OctopusJob:
    def __init__(self, directory, inp, slurm, hash, depends_on: dict):
        self.directory = directory
        self.inp = inp
        self.slurm = slurm
        self.hash = hash
        self.depends_on = depends_on

    def write(self, root="", parents=True, exist_ok=False):
        """
        :return:
        """
        # Make directory
        subdir = Path(root, self.directory)
        Path.mkdir(subdir, parents=parents, exist_ok=exist_ok)

        # Write out files
        for fname, attr in [
            ("inp", "inp"),
            ("slurm.sh", "slurm"),
            ("hash.txt", "hash"),
        ]:
            with open(Path(subdir, fname), "w") as fid:
                fid.write(self.__dict__[attr])

        # Copy dependencies
        for file in self.depends_on.values():
            shutil.copyfile(file["source"], Path(root, file["dest"]))


def ground_state_calculation(
    matrix: dict,
    static_options: dict,
    meta_key: str = "^",
    meta_value_ops: dict = None,
    file_rules=None,
    slurm_settings: dict = None,
    binary_path: str = "",
) -> Dict[str, OctopusJob]:
    """An Octopus Workflow.

     Meta keys are keys with values that require substitution with some specified behaviour
     and then should be removed from the dict following this

    Want to define the substitution behaviour for each meta-key value, to make the workflow more generic
    i.e. could work with ASE or file substitution

    matrix:
    static_options
    : meta_key:
    :return:
    """
    # Defaults
    if meta_value_ops is None:
        meta_value_ops = {}
    if file_rules is None:
        file_rules = []
    if slurm_settings is None:
        slurm_settings = {}

    # Generate list of input dicts
    inputs = expand_input_dictionary(matrix, static_options)

    # Substitute specific settings
    inputs = substitute_specific_settings(inputs, meta_value_ops, meta_key)

    # Go from dicts to strings
    input_strings = [write_octopus_input(input) for input in inputs]

    # Unique hashes
    hashes = create_hashes(input_strings)

    # Use directory names as job ids
    job_ids = directory_generation(matrix)

    # Note location of any file dependencies
    file_dependencies = []
    for i, inp in enumerate(input_strings):
        file_dependencies.append(
            set_job_file_dependencies(inp, job_ids[i], file_rules)
        )

    # Submission scripts
    sub_scripts = slurm_submission_scripts(
        binary_path, slurm_settings, job_ids
    )

    # Package information
    jobs = {}
    for i, id in enumerate(job_ids):
        jobs[id] = OctopusJob(
            id,
            input_strings[i],
            sub_scripts[i],
            hashes[i],
            file_dependencies[i],
        )

    return jobs

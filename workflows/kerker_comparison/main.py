""" Workflow for comparing the Kerker preconditioning to the non-preconditioned mixing schemes

* linear mixing. No preconditioning
* linear mixing. Kerker preconditioning
* Broyden mixing. No preconditioning
* Broyden mixing. Kerker preconditioning

"""
import datetime
from pathlib import Path
from typing import Dict

from octopus_workflows.simple_oct_workflow import ground_state_calculation, OctopusJob

from settings import fixed_options, matrix, meta_value_ops, file_rules, kerker_options


def no_kerker_jobs() -> dict:
    """
    No preconditioning
    :return:
    """
    oct_root_ada = '/u/abuc/packages/octopus/_build_main_gpu/installed'

    default_ada_gpu = {'nodes': 1,
                       'ntasks_per_node': 4,
                       'cpus_per_task': 18,
                       'partition': 'p.ada',
                       'gres': ['gpu:a100:4'],
                       'ignore_pbs': True,
                       'job_name': 'octopus_testset',
                       'time': datetime.timedelta(days=0, hours=4, minutes=0, seconds=0),
                       'mem': '100G',  # Cluster max: 1000G
                       'mail_type': 'none'}

    return ground_state_calculation(matrix,
                                    fixed_options,
                                    meta_value_ops=meta_value_ops,
                                    file_rules=file_rules,
                                    slurm_settings=default_ada_gpu,
                                    binary_path=oct_root_ada
                                    )


def kerker_jobs() -> dict:
    """
    Preconditioning
    :return:
    """
    oct_root_ada = '/u/abuc/packages/octopus/_build_kerker/installed'

    default_ada_gpu = {'nodes': 1,
                       'ntasks_per_node': 4,
                       'cpus_per_task': 18,
                       'partition': 'p.ada',
                       'gres': ['gpu:a100:4'],
                       'ignore_pbs': True,
                       'job_name': 'octopus_testset',
                       'time': datetime.timedelta(days=0, hours=4, minutes=0, seconds=0),
                       'mem': '100G',  # Cluster max: 1000G
                       'mail_type': 'none'}

    return ground_state_calculation(matrix,
                                    {**fixed_options, **kerker_options},
                                    meta_value_ops=meta_value_ops,
                                    file_rules=file_rules,
                                    slurm_settings=default_ada_gpu,
                                    binary_path=oct_root_ada
                                    )


if __name__ == '__main__':

    # Jobs with no preconditioning
    jobs: Dict[str, OctopusJob] = no_kerker_jobs()
    for job in jobs.values():
        job.write(root='jobs/kerker_comparison/no_preconditioning', exist_ok=True)

    # Jobs with preconditioning
    jobs: Dict[str, OctopusJob] = kerker_jobs()
    for job in jobs.values():
        job.write(root='jobs/kerker_comparison/preconditioning', exist_ok=True)

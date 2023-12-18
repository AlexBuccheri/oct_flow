""" Workflow for comparing the Kerker preconditioning to the non-preconditioned mixing schemes

* linear mixing. No preconditioning
* linear mixing. Kerker preconditioning
* Broyden mixing. No preconditioning
* Broyden mixing. Kerker preconditioning

"""
import datetime
from pathlib import Path

from octopus_workflows.simple_oct_workflow import ground_state_calculation

# Job root
root = Path('jobs/kerker_comparison')


def no_kerker_jobs() -> dict:
    """
    No preconditioning
    :return:
    """
    from settings import fixed_options, matrix, meta_key, meta_value_ops
    oct_root_ada = '/u/abuc/packages/octopus/_build_main/installed'
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
    return ground_state_calculation(matrix, fixed_options, meta_key, meta_value_ops, default_ada_gpu, oct_root_ada)


def kerker_jobs() -> dict:
    """
    Preconditioning
    :return:
    """
    oct_root = '/u/abuc/packages/octopus/_build_kerker/installed'
    return {}


jobs = no_kerker_jobs()
# for job in jobs.values():
#     print(job['inp'])

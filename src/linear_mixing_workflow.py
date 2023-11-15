"""Linear Mixing Workflow
"""
import datetime
from pathlib import Path

from oct_workflow import ground_state_calculation


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


specific_options = {'Al_cubic':
                        {'ase_constructor': {'name': 'Al', 'crystalstructure': 'fcc', 'a': 4.04, 'cubic': True},
                         'Species': ['"Al"', 'species_pseudo', 'set', 'hgh_lda']
                         },
                    'Fe_cubic':
                        {'ase_constructor': {'name': 'Fe', 'crystalstructure': 'fcc', 'a': 2.86, 'cubic': True},
                         'Species': ['"Fe"', 'species_pseudo', 'set', 'hgh_lda']
                         },
                    'Cu_cubic':
                        {'ase_constructor': {'name': 'Cu', 'crystalstructure': 'fcc', 'a': 3.58, 'cubic': True},
                         'Species': ['"Cu"', 'species_pseudo', 'set', 'hgh_lda']
                         }
                    }

static_options = {'CalculationMode': 'gs',
                  'ExperimentalFeatures': 'yes',
                  'RestartWrite': 'No',
                  'ProfilingMode': 'prof_time',
                  # Metalic, so include
                  'Smearing': 0.01,
                  'SmearingFunction': 'fermi_dirac',
                  # Solver
                  'MaximumIter': 200,
                  'Eigensolver': 'chebyshev_filter',
                  'EigensolverTolerance': 1.e-7,
                  'ChebyshevFilterDegree': 30,
                  'ExtraStatesInPercent': 25,
                  # Grid
                  'PeriodicDimensions': 3,
                  'BoxShape': 'parallelepiped',
                  'Spacing': 0.2,
                  'MixingScheme': 'linear',
                  # k-points
                  'KPointsUseSymmetries': 'No',
                  'KPointsGrid': [2, 2, 2]
                  }

# Job permutations
matrix = {'material': ['Al_cubic', 'Fe_cubic', 'Cu_cubic'],
          'supercell': [[1, 1, 1]],
          'Mixing': [0.3]}

# Meta-keys that should be a. generated for all permutations,  b. be subbed with specific definitions above,
# c. removed
meta_keys = ['material']


if __name__ == "__main__":
    root = 'jobs/linear_mixing'
    oct_root_ada = '/u/abuc/packages/octopus/_build_kerker/installed'
    jobs = ground_state_calculation(matrix, static_options, specific_options, meta_keys, default_ada_gpu, oct_root_ada)

    # Write jobs to file
    for job in jobs.values():
        subdir = Path(root, job['directory'])
        Path.mkdir(subdir, parents=True, exist_ok=True)

        for file_type, file_name in [('hash', 'metadata.txt'), ('inp', 'inp'), ('submission', 'run.sh')]:
            with open(subdir / file_name, 'w') as fid:
                fid.write(job[file_type])

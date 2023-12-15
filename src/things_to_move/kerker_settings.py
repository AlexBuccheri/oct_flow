"""
Settings for Kerker Calculations
"""
import datetime

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

# Looking at the ASE source, if I select cubic, I should be passing the conventional lattice constant
# in Angstrom
# Al 4.04 Å https://next-gen.materialsproject.org/materials/mp-134
# Fe 2.86 Å https://next-gen.materialsproject.org/materials/mp-13
# Cu 3.58 Å https://next-gen.materialsproject.org/materials/mp-30
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
                  'Spacing': 0.2
                  }

# Kerker mixing
kerker_options = {'MixField': 'density',
                  'MixingKerker': 'yes',
                  'MixingKerkerFactor': '1.0',  # Default
                  'Mixing': '0.8'}

# Job permutations
matrix = {'material': ['Al_cubic', 'Fe_cubic', 'Cu_cubic'],
          'supercell': [[1, 1, 1], [2, 2, 2]]}

# Meta-keys that should be a. generated for all permutations,  b. be subbed with specific definitions above,
# c. removed
meta_keys = ['material']

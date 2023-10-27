"""
Settings for Kerker Calculations
"""

material_definitions = {'Al_cubic': {'name': 'Al', 'crystalstructure': 'fcc', 'a': 4.04, 'cubic': True},
             'Fe_cubic': {'name': 'Fe', 'crystalstructure': 'fcc', 'a': 4.00 , 'cubic': True},
             'Cu_cubic': {'name': 'Cu', 'crystalstructure': 'fcc', 'a': 4.00 , 'cubic': True}
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

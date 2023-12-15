import itertools


def cartesian_product(matrix: dict):
    """Create all combinations of options, where the dict
    keys define the options and the values define the
    specific values that the optionals should take.

    Expects a dict of the form:

    {'Eigensolver': ['rmmdiis', 'chebyshev_filter'],
     'EigensolverTolerance':'1e-7'}

    with no nesting of containers in values.

    :param matrix:
    :return:
    """
    # Get all possible combinations
    combinations = list(itertools.product(*matrix.values()))

    # Create a list of dictionaries by pairing each key with its corresponding value from the combinations
    all_option_permutations = [
        {key: value for key, value in zip(matrix.keys(), combination)}
        for combination in combinations
    ]

    return all_option_permutations

""" Convert dictionary to octopus input file string.
"""


def write_octopus_input(options: dict) -> str:
    """
    TODO(Alex) Could make this more readable and reduce the loops
    :param options:
    :return:
    """
    input = ""

    for key, value in options.items():
        if isinstance(value, list):
            input += f"%{key}\n"
            # Nested list (note, do not expect more than one level of nesting)
            if isinstance(value[0], list):
                for v in value:
                    input += " ".join(f"{s} |" for s in v)[:-1] + "\n"
            # Single list
            else:
                input += " ".join(f"{s} |" for s in value)[:-1] + "\n"
            input += "%\n"
        else:
            input += f"{key} = {value}\n"

    return input

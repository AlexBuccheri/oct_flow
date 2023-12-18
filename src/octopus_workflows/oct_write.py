""" Convert dictionary to octopus input file string.
"""
import ase
import numpy as np


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


def write_extended_xyz(xyz_file, atoms: ase.atoms.Atoms):
    """
    NOTE ALEX. This ref format does not appear to get picked up by vesta
    https://open-babel.readthedocs.io/en/latest/FileFormats/Extended_XYZ_cartesian_coordinates_format.html

    :param xyz_file:
    :param atoms:
    :return:
    """
    with open(xyz_file, "w") as f:
        f.write(f"{len(atoms)}\n")
        f.write("%PBC\n")

        for symbol, position in zip(
            atoms.get_chemical_symbols(), atoms.get_positions()
        ):
            f.write(
                f"{symbol} {position[0]:.6f} {position[1]:.6f} {position[2]:.6f}\n"
            )

        f.write("\n")
        lattice = atoms.get_cell().array
        n_vectors, n_components = len(lattice), len(lattice[0])

        for i in range(n_vectors):
            f.write(
                f"Vector{i + 1}   "
                + " ".join(f"{r:.9f}" for r in lattice[i, :])
                + "\n"
            )

        origin = np.zeros(shape=n_components)
        f.write("Offset    " + " ".join(f"{r:.9f}" for r in origin))

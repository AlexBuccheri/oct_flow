""" Convert Octopus-formatted structure input to ASE Atoms, and vice versa.
"""
import ase
import numpy as np
import scipy.linalg


bohr_to_ang = 0.52917721092
ang_to_bohr = 1. / bohr_to_ang


def unit_vector(a):
    return np.asarray(a) / scipy.linalg.norm(a)


def parse_oct_structure_to_atoms(options: dict) -> ase.atoms.Atoms:
    """

    Lattice vectors stored rowwise.

    :param options:
    :return:
    """

    # Get cell angles from the lattice vectors
    lattice_vectors = options['LatticeVectors']
    n_dim = len(lattice_vectors)

    assert n_dim == 3, "Calculation of angles between lattice vectors only coded for 3D systems"

    lattice_angles = []
    for i in range(0, n_dim):
        j = (i + 1) % n_dim
        angle = np.arccos(np.dot(unit_vector(lattice_vectors[i]), unit_vector(lattice_vectors[j])))
        lattice_angles.append(np.degrees(angle))

    lattice_parameters = [x * bohr_to_ang for x in options['LatticeParameters']]

    # TODO(Alex) No idea what convention they're using
    # Multiply each lattice parameter by norm of each lattice vector
    for i in range(0, n_dim):
        lattice_parameters[i] *= scipy.linalg.norm(lattice_vectors[i])

    # TODO(Alex) User can specify input units - would need to check for those.
    #  Yes/No can be appended to the end of a Coordinate line - would need to check for that too
    # Convert units
    positions = []
    #  Need shift the atomic positions. Is this a problem for Octopus?
    origin = np.array([r * bohr_to_ang for r in options['Coordinates'][0][1:]])
    for entry in options['Coordinates']:
        positions.append(np.array([r * bohr_to_ang for r in entry[1:]]) - origin)

    atoms = ase.atoms.Atoms(symbols=[entry[0] for entry in options['Coordinates']],
                            positions=positions,
                            pbc=True
                            )

    # If cell is six numbers, assume three lengths, then three angles.
    atoms.set_cell(lattice_parameters + lattice_angles, scale_atoms=False)

    return atoms


def ase_atoms_to_oct_structure(atoms: ase.atoms.Atoms, fractional=True) -> str:
    """ Convert ASE Atoms instance to Octopus input substring for:
    LatticeVectors and Coordinates, noting that LatticeParameters
    are absorbed in the LatticeVectors.

    :param atoms: Atoms instance.
    :param fractional:
    :return: input_string: Structure substring
    """
    input_string = ""

    # LatticeParameters
    constants_and_angles = atoms.cell.cellpar()
    constants = np.asarray(constants_and_angles[0:3]) * ang_to_bohr
    input_string += "%LatticeParameters\n"
    input_string += " ".join(f"{constant} |" for constant in constants[0:3])[:-1] + '\n'
    input_string += "%\n"

    # LatticeVectors (row-wise in ASE, and Octopus input)
    lattice = atoms.get_cell().array * ang_to_bohr
    n_vectors, n_components = len(lattice), len(lattice[0])

    # Define origin before dividing through by lattice constants
    origin = np.zeros(shape=n_components)
    for i in range(0, n_vectors):
        origin[:] += 0.5 * np.asarray(lattice[i, :])

    # Divide lattice vectors by respective parameters
    lattice = [v / constants[i] for i, v in enumerate(lattice)]

    input_string += "%LatticeVectors\n"
    for vector in lattice:
        input_string += " ".join(f"{r:.9f} |" for r in vector)[:-1] + '\n'
    input_string += "%\n"

    # Coordinates
    species = atoms.get_chemical_symbols()

    # Note that in Octopus the origin of coordinates is in the center of the cell,
    if fractional:
        # The coordinates inside the cell are in the range [-0.5, 0.5)
        key = 'ReducedCoordinates'
        fractional_origin = np.array([0.5, 0.5, 0.5])
        positions = np.asarray(atoms.get_scaled_positions()) - fractional_origin
    else:
        key = 'Coordinates'
        positions = np.asarray(atoms.get_positions()) * ang_to_bohr - origin
    n_atoms = len(species)

    # Pad with trailing whitespace, to achieve alignment when printing
    unique_species = set(species)
    max_len = len(max(unique_species))
    pad = lambda x: " " * (max_len - len(x))
    whitespace = [pad(x) for x in species]

    input_string += f"%{key}\n"
    for i in range(0, n_atoms):
        line = f"\"{species[i]}\"{whitespace[i]} | " + " ".join(f"{r:.18e} |" for r in positions[i])[:-1]
        input_string += line + '\n'
    input_string += "%\n"

    return input_string

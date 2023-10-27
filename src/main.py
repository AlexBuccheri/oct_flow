""" Produce Au and Pb surfaces

ASE
------
Visualisation: https://wiki.fysik.dtu.dk/ase/ase/visualize/visualize.html
Surfaces: https://wiki.fysik.dtu.dk/ase/ase/build/surface.html

References
------------
* Note this exciting paper as a ref: https://iopscience.iop.org/article/10.1088/2516-1075/ababde
 - 111 Pd surface
 - 5L-(2 × 2) Au(111) with a vacancy

*  Yoshinori Shiihara et al 2008 Modelling Simul. Mater. Sci. Eng. 16 035004
  - Used bulk fcc aluminium of 100-300 atoms
  - |G|_min -> smaller as L_box -> larger, so supercells exhibit larger charge sloshing


Materials
------------
* Pd primitive: Cubic. No225. al = 2.77 ang
  - https://next-gen.materialsproject.org/materials/mp-2
  - Pd slab, vacuum above and below, noting that Octopus can disable periodicity in z.
  - Note, it should not matter where the vacuum is

* Au primitive: Cubic. No225. al = 2.95 ang
  - https://next-gen.materialsproject.org/materials/mp-81

* 200 atom bulk Al
* https://next-gen.materialsproject.org/materials/mp-134

"""
import ase
from ase.build import fcc111, bulk
from ase.visualize import view

from structure import ase_atoms_to_oct_structure


def al_bulk_cubic() -> ase.atoms.Atoms:
    # Bulk Al supercell
    al_bulk = bulk('Al', 'fcc', a=4.04, cubic=True)
    # This gives 256 atoms
    al_supercell = ase.build.make_supercell(al_bulk, [[4, 0, 0], [0, 4, 0], [0, 0, 4]])
    return al_supercell


def pd_111_surface():
    # Pd(111) slab
    pd_slab = fcc111('Pd', a=2.77, size=(1, 1, 5), periodic=True, vacuum=10)
    return pd_slab


def au_111_surface_w_vacancy():
    # 5L-(2 × 2) Au(111) with a vacancy
    gold_slab_with_vacancy = fcc111('Au', a=2.95, size=(1, 1, 5), periodic=True, vacuum=15)
    # Check, what's the difference between using size and expanding using the supercell method
    gold_super_slab = ase.build.make_supercell(gold_slab_with_vacancy, [[2, 0, 0], [0, 2, 0], [0, 0, 1]])
    # Create a vacancy
    del gold_super_slab[4]
    return gold_super_slab


if __name__ == "__main__":
    system = {'al_bulk_cubic': al_bulk_cubic,
              'pd_111_surface': pd_111_surface,
              'au_111_surface_w_vacancy': au_111_surface_w_vacancy}

    cell = system['al_bulk_cubic']()
    view(cell)
    struct_inp = ase_atoms_to_oct_structure(cell)
    print(struct_inp)

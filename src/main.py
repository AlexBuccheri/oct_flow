""" Produce Au and Pb surfaces

ASE
------
Visualisation: https://wiki.fysik.dtu.dk/ase/ase/visualize/visualize.html
Surfaces: https://wiki.fysik.dtu.dk/ase/ase/build/surface.html

Materials
------------
Pd primitive: Cubic. No225. al = 2.77 ang
https://next-gen.materialsproject.org/materials/mp-2
"""
from ase.build import fcc111
from ase.visualize import view


slab = fcc111('Pd', a=2.77, size=(2, 2, 5), periodic=True)
view(slab)

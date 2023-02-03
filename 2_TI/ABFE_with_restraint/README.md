# Absolute binding free energy calculation with restraint

## Theory

The DDM to compute absolute binding free energies was outlined in the Introduction. Its key element isa hypothetical intermediate state in which the interactions between receptor and ligand have been turned off alchemically but where restraints keep the ligand in a position and orientation that resembles the native bound state.
See more details in [Absolute Binding Free Energies: A Quantitative Approach for Their Calculation](https://pubs.acs.org/doi/10.1021/jp0217839)

## TI with restraint

We can use `VB_generate.py` to generate the restraint you need for Amber like below:
```bash
python VB_generate.py --complex complex.pdb --ligand ligand_name
```

Here, the complex.pdb is the complex structure of your system and the ligand_name is the resname of your ligand in structure. The outputs of that command are two txt file: `rst` and `dG_cor`. 
`rst` stores the restraint commands for AMBER, and you can copy it into the `ti.in` file for your stimuation. `dG_cor` shows the free energy cost of cross-linking two molecules in the harmonic approximation.


# Basic molecular dynamics simulation protocol based on AMBER: the protein-ligand complex in water

Here is my protocol of the simulation for the protein-ligand complex in water.
- [Basic molecular dynamics simulation protocol based on AMBER: the protein-ligand complex in water](#basic-molecular-dynamics-simulation-protocol-based-on-amber-the-protein-ligand-complex-in-water)
  - [System prepare](#system-prepare)
    - [1, parametrizing ligands](#1-parametrizing-ligands)
    - [2, prepare the protein](#2-prepare-the-protein)
    - [3, construct the system](#3-construct-the-system)
  - [Simulation of system: min, heat, press](#simulation-of-system-min-heat-press)
  - [Anaylsis](#anaylsis)

## System prepare

Before the simulation, we need to construct a protein-ligand complex in water box system. We can use three step to generate it.

### 1, parametrizing ligands

There are often any force field parameters that are needed for the ligands but not supplied by the force field (.dat) file, so we need to parametrize the ligands to generate force field modification (.frcmod) file. We can use antechamber and parmchk2 to realise this step. 

```bash
antechamber -i ${lig}.mol2 -fi mol2 -o ${lig}_bcc.mol2 -fo mol2 -c bcc -pf y
parmchk2 -i ${lig}_bcc.mol2 -f mol2 -o ${lig}.frcmod
```

Here we use the charge model is the am1bcc model. If you want use other charge model, like resp, you can use the output of gaussion for the charge calculation, just like below:
```
antechamber -i ${lig}.log -fi gout -o ${lig}_resp.mol2 -fo mol2 -c resp -pf y
```

Then, we can use the tleap to convert the .frcmod file to .lib file for the .frcmod file is just the supplied the parameters not in gaff. 

```bash
source leaprc.gaff
${lig}=loadmol2 ${lig}_bcc.mol2
loadamberparams ${lig}.frcmod
saveoff ${lig} ${lig}.lib
saveamberparm ${lig} ${lig}.prmtop ${lig}.inpcrd
```

If you have a ligand in mol2 format, like A04.mol2, you can use the [genlib.sh]() in the dir with the same name, A04, and generate the A04.lib and a refined A04.pdb file, which are all tleap need for a ligand.

### 2, prepare the protein

Refine protein pdb files for amber's tleap.  
Usage:
```bash
pdb4amber -i input.pdb -o refined.pdb
```
This step is not necessary but useful for some pdb files. 

### 3, construct the system
Use tleap to combine the ligand and the protein, and create a water box for solution.

```bash
source leaprc.protein.ff19SB
source leaprc.gaff
source leaprc.water.tip3p

loadoff A04.lib

# load the coordinates and create the complex
ligands = loadpdb A04.pdb
complex = loadpdb refined.pdb
complex = combine {ligands complex}

# create complex in solution for vdw+bonded transformation
solvatebox complex TIP3PBOX 12.0 0.75
addions complex Cl- 0
savepdb complex complex_vdw_bonded.pdb
saveamberparm complex complex_vdw_bonded.parm7 complex_vdw_bonded.rst7

quit
```
Now, we have the system for simulation.

## Simulation of system: min, heat, press

Use the [sub.sh](https://github.com/jgxs/TI_Amber/blob/main/1_protein_light_in_water/simulation/sub.sh):
```bash
qsub sub.sh
```

The sub.sh is:
```
#!/bin/bash
#$ -pe ampere 1
#$ -cwd
#$ -q ampere
#$ -l gpu=1
#$ -N q_ampere
mdrun=/pubhome/soft/amber/amber20_21/bin/pmemd.cuda
prmtop=complex_vdw_bonded.parm7


echo "Minimising..."
mdrun -i min.in -p $prmtop -c complex_vdw_bonded.rst7 -ref complex_vdw_bonded.rst7 -O -o min.out -e min.en -inf min.info -r min.rst7 -l min.log

echo "Heating..."
$mdrun -i heat.in -p $prmtop -c min.rst7 -ref min.rst7 -O -o heat.out -e heat.en -inf heat.info -r heat.rst7 -x heat.nc -l heat.log

echo "Pressurising..."
$mdrun -i press.in -p $prmtop -c heat.rst7 -O -o press.out -e press.en -inf press.info -r press.rst7 -x press.nc -l press.log
```

There *.ins are the control file for the pmemd.cuda

## Anaylsis
test




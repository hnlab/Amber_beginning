# Basic modules in Amber
- [Basic modules in Amber](#basic-modules-in-amber)
  - [Necessary modules for complex simulation](#necessary-modules-for-complex-simulation)
    - [antechamber and parmchk2](#antechamber-and-parmchk2)
    - [tleap](#tleap)
    - [pmemd and pmemd.cuda](#pmemd-and-pmemdcuda)
    - [cpptraj](#cpptraj)
  - [Useful modules for complex simulation](#useful-modules-for-complex-simulation)
    - [pdb4amber](#pdb4amber)
    - [ambpdb](#ambpdb)


Set PATH as below for any command you want use:
```bash 
PATH=/pubhome/soft/amber/amber20_21/bin:$PATH
```
## Necessary modules for complex simulation

### antechamber and parmchk2  
A set of tools to parametrizing organic molecules and some metal centers in proteins.
Usage:
```bash
# convert pdb to mol2 with partical charge
antechamber -i ${lig}.pdb -fi pdb -o ${lig}.mol2 -fo mol2 -c bcc -nc 1 -pf y

# convert a struct file to the input of gaussion
antechamber -i ${lig}.mol2 -fi mol2 -o ${lig}.gjf -fo gcrt -pf y -gn "%nproc=8" 

# use gaussian outfile as input
antechamber -i ${lig}.log -fi gout -o ${lig}_resp.mol2 -fo mol2 -c resp -pf y

# check if all of the needed force field parameters and writes a force field modification(frcmod)
parmchk2 -i ${lig}_resp.mol2 -f mol2 -o ${lig}.frcmod
# frcmod file containing any force field parameters that are needed for the molecule but not supplied by the force field (*.dat) file.  
```
-  -i   input file
-  -fi  input file format
-  -o   output file
-  -fo  output file format 
-  -c   charge method
-  -nc  net charge (int)
-  -pf  remove the intermediate files: can be yes (y) and no (n, default)
-  -gn  settings in gaussion input

### tleap  
The tleap module is basic tool to construct force field files for other amber modules, like pmemd. The tleap can be interactive or read file, like leap.in, as input.  
Usage:
```bash
tleap -f leap.in 
```
Here is some inputs:  
Example 1
```bash
# leap.in to convert frcmod files to .lib files 

# load force field parameters
source leaprc.gaff
${lig}=loadmol2 ${lig}_resp.mol2
loadamberparams ${lig}.frcmod
saveoff ${lig} ${lig}.lib
saveamberparm ${lig} ${lig}.prmtop ${lig}.inpcrd
quit
```
Example 2
```bash
# leap.in to construct complex system

source leaprc.protein.ff19SB
source leaprc.gaff
source leaprc.water.tip4pew

# load force field parameters for ligands
loadoff ${lig}.lib

# load the coordinates and create the complex
ligands = loadpdb ${lig}.pdb
complex = loadpdb ${pro}.pdb
complex = combine {ligands complex}

# create complex in solution for vdw+bonded transformation
solvatebox complex TIP4PEWBOX 12.0 0.75
addions complex Cl- 0
savepdb complex complex_vdw_bonded.pdb
saveamberparm complex complex_vdw_bonded.parm7 complex_vdw_bonded.rst7

quit
```
Example 3
```bash
# leap.in to deal with glycam

source leaprc.protein.ff19SB
source leaprc.gaff

# for glycam
source leaprc.GLYCAM_06j-1
source leaprc.water.tip3p

# load the pdb
wild = loadpdb wildre.amber.pdb

# bond the 0YAs and the NLNs
bond wild.599.C1 wild.304.ND2
bond wild.598.C1 wild.72.ND2 
bond wild.597.C1 wild.35.ND2
bond wild.796.C1 wild.611.ND2
```

### pmemd and pmemd.cuda
PMEMD (Particle Mesh Ewald Molecular Dynamics) is the primary molecular dynamics engine within the AMBER Software suite. The pmemed.MPI is the parallel version of pmemd. The pmemed.cuda is the gpu accelerated pmemd. 
Usage:
```bash
pmemd -i step.in -p complex.prmtop -c complex.inpcrd -ref complex.inpcrd -r complex.inpcrd -o step.out -e step.en -inf step.info -x step.nc -O 
```  
- -O   overwrite files if they have alreadly existed; -A append files.
- -i   contril file  
- -p   topol files
- -c   starting coordinates and velcities file
- -ref restrain the structure
- -r   result coordinates and velcities file
- -e   the energy of simulation
- -inf the information of simulation
- -x   the trajectory file


### cpptraj

Cpptraj (the successor toptraj) is the main program in Amber for processing coordinate trajectories and data files. It is interactive, but you can use `_EOF` to read a input file. 

Usage:
```bash 
cpptraj -p ti.parm7 < commands
```
commands examples
Example 1
```bash
# generate RMSD
# load trajectory
trajin ti001.nc
#Automatically center and image (by molecule) a trajectory with periodic boundaries. 
autoimage 
rms ToFirstComplex :1-99999&!@H&!:WAT= first out rmsd_complex.agr mass
run
``` 
  
Example 2
```bash
# modify the structure

#load structure
trajin ${s}_prepare/press.rst7
# remove residue 1,2
strip ":1,2"
# output the structure
outtraj ${s}_solvated.pdb onlyframes 1
```

## Useful modules for complex simulation

### pdb4amber

A python2.7 script refining pdb files for amber's tleap.  
Usage:
```bash
pdb4amber -i input.pdb [-o output.pdb -l pdb.log] 
```

### ambpdb 
To generate a pdb file from prmtop and inpcrd files, just like:
```bash
ambpdb -p example.prmtop -c example.inpcrd > example.pdb
```
#!/bin/bash
PATH=/pubhome/soft/amber/amber20_21/bin:$PATH
lig3dpath="ligs"

gmxdir=$1
python /pubhome/yjcheng02/FEP/wangqing/systems_for_FEP/pdb2amber.py --gmx_dir ${gmxdir}  
env=`pwd`
mkdir ligs
for lig in LCH LPN
    do
    mkdir ligs/${lig}
    mv ${lig}* ligs/${lig}
    cd ligs/${lig}
    parmchk2 -i ${lig}_bcc.mol2 -f mol2 -o ${lig}.frcmod
    echo "source leaprc.protein.ff19SB
source leaprc.gaff
${lig}=loadmol2 ${lig}_bcc.mol2
loadamberparams ${lig}.frcmod
saveoff ${lig} ${lig}.lib
saveamberparm ${lig} ${lig}.prmtop ${lig}.inpcrd
quit" > leap.in 
    tleap -f leap.in 

    grep ATOM ${lig}.pdb >${lig}V.pdb
    sed -i "s/ATOM  /HETATM/g" ${lig}V.pdb
    echo TER >>${lig}V.pdb 
    cd ${env}
    done

cat ligs/LCH/LCHV.pdb > LCH_LPN.pdb 
cat ligs/LPN/LPNV.pdb >> LCH_LPN.pdb
echo END >> LCH_LPN.pdb
delta_atom=`python /pubhome/yjcheng02/FEP/ikke/tool/diff.py LCH_LPN.pdb`
atom1=${delta_atom%_*}
atom2=${delta_atom##*_}

echo "source leaprc.protein.ff19SB
source leaprc.gaff
source leaprc.water.tip4pew

# load force field parameters for ligands
loadoff ligs/LCH/LCH.lib
loadamberparams ligs/LCH/LCH.frcmod
loadoff ligs/LPN/LPN.lib
loadamberparams ligs/LPN/LPN.frcmod

# load the coordinates and create the complex
ligands = loadpdb LCH_LPN.pdb
complex = loadpdb complex.pdb
complex = combine {ligands complex}

# create ligands in solution for vdw+bonded transformation
solvatebox ligands TIP4PEWBOX 15.0 0.75
addions ligands Cl- 0
savepdb ligands ligands_vdw_bonded.pdb
saveamberparm ligands ligands_vdw_bonded.parm7 ligands_vdw_bonded.rst7

# create complex in solution for vdw+bonded transformation
solvatebox complex TIP4PEWBOX 12.0 0.75
addions complex Cl- 0
savepdb complex complex_vdw_bonded.pdb
saveamberparm complex complex_vdw_bonded.parm7 complex_vdw_bonded.rst7

quit" > gencomplex.leap.in 
tleap -f gencomplex.leap.in 

cp -r /pubhome/yjcheng02/FEP/wangqing/systems_for_FEP/template/*prepare .

mkdir free_energy
for system in ligands complex; do
    pwd
    cd ${system}_prepare
    sed -i "s/:LIGAND1@ATOMS/:LCH@${atom1}/g" *in
    sed -i "s/:LIGAND1/:LCH/g" *in
    sed -i "s/:LIGAND2@ATOMS/:LPN@${atom2}/g" *in
    sed -i "s/:LIGAND2/:LPN/g" *in
    sed -i "s/-N q_ampere/-N LCH_LPN_${system}/g" sub.sh
    qsub sub.sh
    cd ..
done
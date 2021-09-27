#!/bin/bash
PATH=/pubhome/soft/amber/amber20_21/bin:$PATH
lig3dpath="/pubhome/yjcheng02/FEP/ikke/ligs"

env=`pwd`
env=${env##*/}
lig1=${env%%_*}
lig2=${env##*_}

delta_atom=`python /pubhome/yjcheng02/FEP/ikke/tool/diff.py ${lig1}_${lig2}.pdb`
atom1=${delta_atom%_*}
atom2=${delta_atom##*_}

ln -sf $lig3dpath/$lig1/${lig1}.lib .
ln -sf $lig3dpath/$lig2/${lig2}.lib .
ln -sf /pubhome/yjcheng02/FEP/ikke/alpha_ikke.pdb .

echo "source leaprc.protein.ff19SB
source leaprc.gaff
source leaprc.water.tip4pew

# load force field parameters for ligands
loadoff ${lig1}.lib
loadoff ${lig2}.lib

# load the coordinates and create the complex
ligands = loadpdb ${lig1}_${lig2}.pdb
complex = loadpdb alpha_ikke.pdb
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

#tleap -f gencomplex.leap.in 

echo "# load the AMBER force fields
source leaprc.protein.ff19SB
source leaprc.gaff
source leaprc.water.tip3p

# load force field parameters for a38 and c99
loadoff ${lig1}.lib
loadoff ${lig2}.lib

# coordinates for solvated ligands as created previously by MD
lsolv = loadpdb ligands_solvated.pdb
la38 = loadpdb ligands_a38.pdb
lc99 = loadpdb ligands_c99.pdb

# coordinates for complex as created previously by MD
csolv = loadpdb complex_solvated.pdb
ca38 = loadpdb complex_a38.pdb
cc99 = loadpdb complex_c99.pdb

# decharge transformation
decharge = combine {la38 la38 lsolv}
setbox decharge vdw
savepdb decharge ligands_decharge.pdb
saveamberparm decharge ligands_decharge.parm7 ligands_decharge.rst7

decharge = combine {ca38 ca38 csolv}
setbox decharge vdw
savepdb decharge complex_decharge.pdb
saveamberparm decharge complex_decharge.parm7 complex_decharge.rst7

# recharge transformation
recharge = combine {lc99 lc99 lsolv}
setbox recharge vdw
savepdb recharge ligands_recharge.pdb
saveamberparm recharge ligands_recharge.parm7 ligands_recharge.rst7

recharge = combine {cc99 cc99 csolv}
setbox recharge vdw
savepdb recharge complex_recharge.pdb
saveamberparm recharge complex_recharge.parm7 complex_recharge.rst7

quit" > strip_charge.in


cp -r /pubhome/yjcheng02/FEP/ikke/template/*prepare .

for system in ligands complex; do
    pwd
    cd ${system}_prepare
    sed -i "s/:LIGAND1@ATOMS/:${lig1}@${atom1}/g" *in
    sed -i "s/:LIGAND1/:${lig1}/g" *in
    sed -i "s/:LIGAND2@ATOMS/:${lig2}@${atom2}/g" *in
    sed -i "s/:LIGAND2/:${lig2}/g" *in
    qsub sub.sh
    cd ..
done


#!/bin/bash
PATH=/pubhome/soft/amber/amber20_21/bin:$PATH
env=`pwd`
lig=${env##*/}

sed -i "2d" ${lig}.mol2
sed -i "1a${lig}" ${lig}.mol2
sed  -i "s/UNK/${lig}/g" ${lig}.mol2

antechamber -i ${lig}.mol2 -fi mol2 -o ${lig}_bcc.mol2 -fo mol2 -c bcc -pf y
parmchk2 -i ${lig}_bcc.mol2 -f mol2 -o ${lig}.frcmod

echo "source leaprc.protein.ff19SB
source leaprc.gaff

${lig}=loadmol2 ${lig}_bcc.mol2
loadamberparams ${lig}.frcmod
saveoff ${lig} ${lig}.lib
saveamberparm ${lig} ${lig}.prmtop ${lig}.inpcrd

quit" > leap.in 
tleap -f leap.in 
sed -i "s/UNK/${lig}/g" ${lig}.lib

obabel -imol2 ${lig}.mol2 -opdb > ${lig}.pdb
grep ATOM ${lig}.pdb >${lig}V.pdb
sed -i "s/ATOM  /HETATM/g" ${lig}V.pdb
sed -i "s/UNK A   1/${lig} A 718/g" ${lig}V.pdb
echo TER >>${lig}V.pdb 

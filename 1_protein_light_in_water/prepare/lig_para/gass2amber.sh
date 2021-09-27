#!/bin/bash
PATH=/pubhome/soft/amber/amber20_21/bin:$PATH
antechamber -i ligand.mol2 -fi mol2 -o ligand.gjf -fo gcrt -pf y -gn "%nproc=8" 

antechamber -i ${lig}.log -fi gout -o ${lig}_resp.mol2 -fo mol2 -c resp -pf y
sed -i "s/MOL /${lig} /" ${lig}_resp.mol2
parmchk2 -i ${lig}_resp.mol2 -f mol2 -o ${lig}.frcmod
echo "source leaprc.protein.ff19SB
source leaprc.gaff

${lig}=loadmol2 ${lig}_resp.mol2
loadamberparams ${lig}.frcmod
saveoff ${lig} ${lig}.lib
saveamberparm ${lig} ${lig}.prmtop ${lig}.inpcrd

quit" > leap.in 
tleap -f leap.in
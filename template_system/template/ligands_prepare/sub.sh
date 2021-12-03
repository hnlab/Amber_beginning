#!/bin/bash
#$ -pe ampere 1
#$ -cwd
#$ -q ampere
#$ -l gpu=1
#$ -N q_ampere
mdrun=/pubhome/soft/amber/amber20_21/bin/pmemd.cuda
prmtop=../ligands_vdw_bonded.parm7
source /usr/bin/startcuda.sh

echo "Minimising..."
$mdrun -i min.in -p $prmtop -c ../ligands_vdw_bonded.rst7 -ref ../ligands_vdw_bonded.rst7 -O -o min.out -e min.en -inf min.info -r min.rst7 -l min.log

echo "Heating..."
$mdrun -i heat.in -p $prmtop -c min.rst7 -ref ../ligands_vdw_bonded.rst7 -O -o heat.out -e heat.en -inf heat.info -r heat.rst7 -x heat.nc -l heat.log

$mdrun -i press_5.in -p $prmtop -c heat.rst7 -ref heat.rst7 -O -o press_5.out -e press_5.en -inf press_5.info -r press_5.rst7 -x press_5.nc -l press_5.log

j=5
for i in `seq 1 4|tac` 
do
$mdrun -i press_${i}.in -p $prmtop -c press_${j}.rst7 -ref press_${j}.rst7 -O -o press_${i}.out -e press_${i}.en -inf press_${i}.info -r press_${i}.rst7 -x press_${i}.nc -l press_.log
j=$i
done

echo "Pressurising..."
$mdrun -i press.in -p $prmtop -c press_1.rst7 -ref press_1.rst7 -O -o press.out -e press.en -inf press.info -r press.rst7 -x press.nc -l press.log
source /usr/bin/end_cuda.sh

mkdir ligands
cd ligands
ln -sf ../../ligands_vdw_bonded.parm7 .
ln -sf ../press.rst7 ligands_vdw_bonded.rst7
delta_atom=`python /pubhome/yjcheng02/FEP/ikke/tool/diff.py ../../LCH_LPN.pdb`

atom1=${delta_atom%_*}
atom2=${delta_atom##*_}
vdw_bonded="ifsc=1, scmask1='@$atom1', scmask2='@$atom2',"
for w in 0.00922 0.04794 0.11505 0.20634 0.31608 0.43738 0.56262 0.68392 0.79366 0.88495 0.95206 0.99078; do
      if [ \! -d $w ]; then
        mkdir $w
      fi
      #sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/FEP/ikke/template/free_gti_sc2/min.tmpl > $w/min.in
      sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/FEP/ikke/template/free_gti_sc2/heat.tmpl > $w/heat.in
      sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/FEP/ikke/template/free_gti_sc2/prod.tmpl > $w/ti.in

      cd $w
      ln -sf ../ligands_vdw_bonded.parm7 ti.parm7
      ln -sf ../ligands_vdw_bonded.rst7  ti.rst7
      cp /pubhome/yjcheng02/FEP/ikke/tool/qsub_ligands.sh .
      sed -i "s/-N name/-N LCH_LPN_ligands/g" qsub_ligands.sh
      qsub qsub_ligands.sh
      cd ..
  done
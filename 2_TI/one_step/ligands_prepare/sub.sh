#!/bin/bash
#$ -pe ampere 1
#$ -cwd
#$ -q ampere
#$ -l gpu=1
#$ -N q_ampere
mdrun=/pubhome/soft/amber/amber20_21/bin/pmemd.cuda
prmtop=../ligands_vdw_bonded.parm7


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

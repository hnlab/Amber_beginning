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


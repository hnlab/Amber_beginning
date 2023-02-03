#!/bin/bash
#$ -pe ampere 18
#$ -cwd
#$ -q ampere
#$ -N q_ampere

mdrun=/pubhome/soft/amber/amber20_21/bin/pmemd.MPI
mpirun -np 18 $mdrun -i min.in -p ti.parm7 -c ti.rst7 -ref ti.rst7 -O -o min.out -e min.en -inf min.info -r min.rst7 -l min.log
mpirun -np 18 $mdrun -i heat.in -c ti.rst7 -ref ti.rst7 -p ti.parm7 \
  -O -o heat.out -inf heat.info -e heat.en -r heat.rst7 -x heat.nc -l heat.log
mpirun -np 18 $mdrun -i ti.in -c heat.rst7 -p ti.parm7 \
  -O -o ti001.out -inf ti001.info -e ti001.en -r ti001.rst7 -x ti001.nc \
     -l ti001.log
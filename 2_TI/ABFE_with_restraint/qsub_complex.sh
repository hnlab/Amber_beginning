#!/bin/bash
#$ -pe ampere 1
#$ -cwd
#$ -q ampere
#$ -l gpu=1
#$ -N name
source /usr/bin/startcuda.sh

mdrun=/pubhome/soft/amber/amber20_21/bin/pmemd.cuda

$mdrun -i min.in -p ti.parm7 -c ti.rst7 -ref ti.rst7 -O -o min.out -e min.en -inf min.info -r min.rst7 -l min.log

$mdrun -i heat.in -c min.rst7 -ref min.rst7 -p ti.parm7 \
  -O -o heat.out -inf heat.info -e heat.en -r heat.rst7 -x heat.nc -l heat.log

$mdrun -i ti.in -p ti.parm7 -c heat.rst7 -ref heat.rst7 -O -o ti001.out -inf ti001.info -e ti001.en -r ti001.rst7 -x ti001.nc -l ti001.log

python /pubhome/yjcheng02/FEP/TI_Amber/2_TI/ABFE_with_restraint/get_cor_dvdl.py

source /usr/bin/end_cuda.sh

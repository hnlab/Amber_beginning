#!/bin/bash
PATH=/pubhome/soft/amber/amber20_21/bin:$PATH
env=`pwd`

parmfiles=`pwd`
for s in complex ligands; do
  if [ -f ${s}_prepare/press.rst7 ]; then
    cp ${s}_vdw_bonded.rst7 ${s}_vdw_bonded.rst7.leap
    cp ${s}_prepare/press.rst7 ${s}_vdw_bonded.rst7
  fi
done

mkdir free_energy_VBA
cd free_energy_VBA

ambpdb -p ../complex_vdw_bonded.parm7 -c ../complex_vdw_bonded.rst7 |grep -v WAT > com.pdb
ligand=`head -n 2 com.pdb|tail -n 1|awk '{print $4}'`
python /pubhome/yjcheng02/kinase/A397_sel/MD_tools/ABFE_restrain/VB_generate.py --complex com.pdb --ligand $ligand

vdw_bonded="ifsc=1, scmask1=':1', scmask2= '',"
vdw_bonded_re="ifsc=1, scmask1='', scmask2= ':1',"

top=$(pwd)
setup_dir=`pwd`

for system in complex; do
  if [ \! -d $system ]; then
    mkdir $system
  fi

  cd $system
  for w in 0.00922 0.04794 0.11505 0.20634 0.31608 0.43738 0.56262 0.68392 0.79366 0.88495 0.95206 0.99078; do
      if [ \! -d $w ]; then
        mkdir $w
      fi
      sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/kinase/A397_sel/MD_tools/ABFE_restrain/min.tmpl > $w/min.in
      sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/kinase/A397_sel/MD_tools/ABFE_restrain/heat.tmpl > $w/heat.in
      sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/kinase/A397_sel/MD_tools/ABFE_restrain/prod.tmpl > $w/ti.in
      sed -i "s/noshakemask = ':1,2'/noshakemask = ':1'/g" $w/*.in
      sed -i "s/timask2 = ':2'/timask2 = ''/g" $w/*.in
      sed -i "s/6000000/18000000/g" $w/ti.in

      cd $w
      cat ../../rst >> min.in 
      cat ../../rst >> heat.in
      cat ../../rst >> ti.in  
      ln -sf ${parmfiles}/${system}_vdw_bonded.parm7 ti.parm7
      ln -sf ${parmfiles}/${system}_vdw_bonded.rst7  ti.rst7
      cp /pubhome/yjcheng02/kinase/A397_sel/MD_tools/ABFE_restrain/qsub_complex.sh .
      sed -i "s/name/abfe_com/g" qsub_complex.sh
      # sed -i "s/ampere/cuda/g" qsub_complex.sh
      qsub -l hostname=!"(k228|k230)" qsub_complex.sh
      cd ..
  done
  cd $top
done

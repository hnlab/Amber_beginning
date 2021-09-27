#!/bin/bash
#
# Setup for the free energy simulations: creates and links to the input file as
# necessary.  Two alternative for the de- and recharging step can be used.
#
env=`pwd`
env=${env##*/}
lig1=${env%%_*}
lig2=${env##*_}
delta_atom=`python /pubhome/yjcheng02/FEP/ikke/tool/diff.py ${lig1}_${lig2}.pdb`
atom1=${delta_atom%_*}
atom2=${delta_atom##*_}

if [ -d free_energy ]; then 
   rm -r free_energy
fi
mkdir free_energy
cd free_energy
# partial removal/addition of charges: softcore atoms only
decharge_crg=":1@${atom1}"
vdw_crg=":1@${atom1} |:2@${atom2}"
recharge_crg=":2@${atom2}"

vdw_bonded="ifsc=1, scmask1='$decharge_crg', scmask2='$recharge_crg',"

top=$(pwd)
setup_dir=${top%/*}

for system in ligands complex; do
  if [ \! -d $system ]; then
    mkdir $system
  fi

  cd $system
  for w in 0.00922 0.04794 0.11505 0.20634 0.31608 0.43738 0.56262 0.68392 0.79366 0.88495 0.95206 0.99078; do
      if [ \! -d $w ]; then
        mkdir $w
      fi
      #sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/FEP/ikke/template/free_gti_sc2/min.tmpl > $w/min.in
      sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/FEP/ikke/template/free_gti_sc2/heat.tmpl > $w/heat.in
      sed -e "s/%L%/$w/" -e "s/%FE%/$vdw_bonded/" /pubhome/yjcheng02/FEP/ikke/template/free_gti_sc2/prod.tmpl > $w/ti.in

      cd $w
      ln -sf $setup_dir/${system}_vdw_bonded.parm7 ti.parm7
      ln -sf $setup_dir/${system}_vdw_bonded.rst7  ti.rst7
      cd ..
  done
  cd $top
done


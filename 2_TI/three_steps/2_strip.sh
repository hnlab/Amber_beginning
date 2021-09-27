PATH=/pubhome/soft/amber/amber20_21/bin:$PATH
cpptraj=$AMBERHOME/bin/cpptraj

for s in ligands complex; do
  if [ -f ${s}_prepare/press.rst7 ]; then
    cp ${s}_vdw_bonded.rst7 ${s}_vdw_bonded.rst7.leap
    cp ${s}_prepare/press.rst7 ${s}_vdw_bonded.rst7
  fi

  $cpptraj -p ${s}_vdw_bonded.parm7 <<_EOF
trajin ${s}_prepare/press.rst7

# remove the two ligands and keep the rest
strip ":1,2"
outtraj ${s}_solvated.pdb onlyframes 1

# extract the first ligand
unstrip
strip ":2-999999"
outtraj ${s}_a38.pdb onlyframes 1

# extract the second ligand
unstrip
strip ":1,3-999999"
outtraj ${s}_c99.pdb onlyframes 1
_EOF
done

tleap -f strip_charge.in
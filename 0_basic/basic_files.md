# Basic files in Amber

## files about force fields  

.dat, .frcmod and .lib

prmtop/prm7, inpcrd/rst7

## control file  

```Fortran
!the first of the .in file is its title, which is necessary but has no effect on the simulation.
Minimization

!from "&cntrl" to "/" is a group of variables that control this minimazation. 
!All variables is in a namelist statement with the namelist identifier &cntrl.cmmu, which is a standard feature of Fortran 90.
!Note that the first character on each line of a namelist block must be a blank.
 &cntrl

  ! imin is general flag describing the calculation. 
  ! imin=0 means a molecular dynamics; imin=1 means a minimization; imin=5 means it will read in a trajectory.
   imin = 1, 

  ! ntmin define the method of minimization. = 2 Only the steepest descent method is used
   ntmin = 2,

  ! maxcyc define the maximum number of line minimization steps 
   maxcyc = 1000,

  ! define the output. every ntpr steps output the tem;every ntwe output the restrt structure. 
   ntpr = 200, ntwe = 200,

  ! ntb define the whether or not periodic boundaries are imposed on the system. ntb = 0 means no periodicity and PME is off. = 1 constant volume; = 2 constant pressure
   ntb = 1,

  ! ntr define the restrain. if ntr > 0. The restrained atoms are determined by the restraintmask string will be restain with restraint_wt kcal/(mol*A^2)
   ntr = 1, restraint_wt = 5.00,
   restraintmask='!:WAT & !@H=',
 /
``` 
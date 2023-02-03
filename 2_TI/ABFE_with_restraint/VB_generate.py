import argparse
from math import acos,degrees,pi, sin, radians,log

class Atom:
    # parse a line in pdb file and generate a Atom contain information of it.
    def __init__(self,atomline):
        atominfo = atomline.split()
        self.id = atominfo[1]
        self.name = atominfo[2]
        self.element = atominfo[2][0]
        self.xyz = [
            float(atomline[30:38]),
            float(atomline[38:46]),
            float(atomline[46:54]),
        ]

def get_dist(atom_i,atom_j):
    return sum([(atom_i.xyz[i]-atom_j.xyz[i])**2 for i in range(3)])**0.5

def get_angle(atom_i,atom_j,atom_k):
    vec_ij = [atom_i.xyz[i]-atom_j.xyz[i] for i in range(3)]
    vec_kj = [atom_k.xyz[i]-atom_j.xyz[i] for i in range(3)]
    # dot 
    res_dot = sum(vec_ij[i]*vec_kj[i] for i in range(3))
    length_ij = sum([(vec_ij[i])**2 for i in range(3)])**0.5
    length_kj = sum([(vec_kj[i])**2 for i in range(3)])**0.5
    angle = degrees(acos(res_dot/(length_ij*length_kj)))
    return angle

def get_n_vec(atom_i,atom_j,atom_k):
    # 获得由三点决定平面的法向量
    vec_ij = [atom_i.xyz[i]-atom_j.xyz[i] for i in range(3)]
    vec_kj = [atom_k.xyz[i]-atom_j.xyz[i] for i in range(3)]
    vec_n_ijk = [
        vec_ij[1]*vec_kj[2]-vec_kj[1]*vec_ij[2],
        vec_ij[2]*vec_kj[0]-vec_kj[2]*vec_ij[0],
        vec_ij[0]*vec_kj[1]-vec_kj[0]*vec_ij[1]
        ]
    return vec_n_ijk

def get_torsion(atom_i,atom_j,atom_k,atom_l):
    n_ijk = get_n_vec(atom_i,atom_j,atom_k)
    n_jkl = get_n_vec(atom_j,atom_k,atom_l)
    res_dot = sum(n_ijk[i]*n_jkl[i] for i in range(3))
    length_ijk = sum([(n_ijk[i])**2 for i in range(3)])**0.5
    length_jkl = sum([(n_jkl[i])**2 for i in range(3)])**0.5
    angle = degrees(acos(res_dot/(length_ijk*length_jkl)))
    return angle

def get_closest_two_atoms(refatom, atoms):
    dist_array = [(item,get_dist(refatom,item)) for item in atoms]
    return sorted(dist_array, key= lambda x:x[1])


parser = argparse.ArgumentParser(description="Virtual Bond Generation")
parser.add_argument(
    "--complex",
    dest='complex',
    )

parser.add_argument(
    "--ligand",
    dest='ligand',
    )

complex_pdb = parser.parse_args().complex
ligand = parser.parse_args().ligand

ligand_atoms = []
receptor_CNs = {}

with open(complex_pdb) as info:
    for line in info:
        if line[0:4] == "ATOM":
            if ligand in line:
                if line[-4] != "H":
                    ligand_atoms.append(Atom(line))
            else:
                res_id = int(line.split()[4])
                if res_id in receptor_CNs:
                    pass 
                else:
                    receptor_CNs[res_id] = []
                pro_atom = Atom(line)
                if pro_atom.name in ['N','CA','C','O']:
                    receptor_CNs[res_id].append(pro_atom)

closest_atompair = []
closest_dist = 8.0
for res in receptor_CNs:
    for atom_rec in receptor_CNs[res]:
        for atom_lig in ligand_atoms:
            if get_dist(atom_rec,atom_lig) < closest_dist:
                close_res = res
                closest_rec_atom = atom_rec
                closest_lig_atom = atom_lig
                closest_dist = get_dist(atom_rec,atom_lig)

rec_atoms = get_closest_two_atoms(closest_rec_atom,receptor_CNs[close_res])[0:3]
lig_atoms = get_closest_two_atoms(closest_lig_atom,ligand_atoms)[0:3]

dist_restrain = f"""
 &rst iat = {rec_atoms[0][0].id}, {lig_atoms[0][0].id}, 
 ialtd = 1,
 r1 = 0.0, r2 = {closest_dist:.1f}, r3 = {closest_dist:.1f}, r4 = 20.0, 
 rk2 = 5.0, rk3 = 5.0 
 /
 """

angle_1 = get_angle(rec_atoms[1][0], rec_atoms[0][0], lig_atoms[0][0])
angle_2 = get_angle(lig_atoms[1][0], lig_atoms[0][0], rec_atoms[0][0])
angle_restain = f"""
 &rst iat = {rec_atoms[1][0].id},{rec_atoms[0][0].id}, {lig_atoms[0][0].id},
 ialtd = 1,
 r1 = -360.0, r2 = {angle_1:.1f}, r3 = {angle_1:.1f}, r4 = 360.0, 
 rk2 = 20.0, rk3 = 20.0 
 /
 &rst iat = {lig_atoms[1][0].id},{lig_atoms[0][0].id}, {rec_atoms[0][0].id},
 ialtd = 1,
 r1 = -360.0, r2 = {angle_2:.1f}, r3 = {angle_2:.1f}, r4 = 360.0, 
 rk2 = 20.0, rk3 = 20.0 
 /
 """

torsion_1 = get_torsion(lig_atoms[2][0],lig_atoms[1][0], lig_atoms[0][0], rec_atoms[0][0])
torsion_2 = get_torsion(rec_atoms[2][0],rec_atoms[1][0], rec_atoms[0][0], lig_atoms[0][0])
torsion_3 = get_torsion(rec_atoms[1][0],rec_atoms[0][0], lig_atoms[0][0], lig_atoms[1][0])
torsion_restain = f"""
 &rst 
 iat = {lig_atoms[2][0].id},{lig_atoms[1][0].id}, {lig_atoms[0][0].id}, {rec_atoms[0][0].id},
 ialtd = 1,
 r1 = -360.0, r2 = {torsion_1:.1f}, r3 = {torsion_1:.1f}, r4 = 360.0, 
 rk2 = 20.0, rk3 = 20.0 
 / 
 &rst 
 iat = {rec_atoms[2][0].id},{rec_atoms[1][0].id}, {rec_atoms[0][0].id}, {lig_atoms[0][0].id},
 ialtd = 1,
 r1 = -360.0, r2 = {torsion_2:.1f}, r3 = {torsion_2:.1f}, r4 = 360.0, 
 rk2 = 20.0, rk3 = 20.0 
 /
  &rst 
 iat = {rec_atoms[1][0].id},{rec_atoms[0][0].id}, {lig_atoms[0][0].id}, {lig_atoms[1][0].id},
 ialtd = 1,
 r1 = -360.0, r2 = {torsion_3:.1f}, r3 = {torsion_3:.1f}, r4 = 360.0, 
 rk2 = 20.0, rk3 = 20.0 
 /
 """

with open("rst","w") as out:
    out.write(dist_restrain)
    out.write(angle_restain)
    out.write(torsion_restain)

dG_cor = - (0.1987*3.0) * log((1661*(5*20*20*20*20*20))/((closest_dist**2)* sin(radians(angle_1))*sin(radians(angle_2))* pi*(0.1987*3.0)**3))
with open("dG_cor","w") as out:
    out.write(f"{dG_cor:.4f}\n")
from pathlib import Path
import argparse

class Atom:
    # parse a line in pdb file and generate a Atom contain information of it.
    def __init__(self,atomline):
        atominfo = atomline.split()
        self.name = atominfo[2]
        self.element = atominfo[2][0]
        self.xyz = [float(atominfo[i]) for i in [6,7,8]]

    def get_dist(self,atom):
        return sum([(self.xyz[i]-atom.xyz[i])**2 for i in range(3)])

class Ligand:
    def __init__(self,lig):
        self.lines = []
        self.atoms={}
        self.Hs = []
        i = 0
        for line in lig:
            #delete LP1 
            if "LP" not in line:
                self.lines.append(line)
                self.atoms[i] = Atom(line)
                if self.atoms[i].element == "H":
                    self.Hs.append(Atom(line))
                i += 1
        self.number = i
        self.delta_atoms = []
    
    def compare(self,ligand):
        for atom_index in range(self.number):
            if self.atoms[atom_index].element != ligand.atoms[atom_index].element:
                delta_atom = self.atoms[atom_index]
                delta_atom2 = ligand.atoms[atom_index]
                dists = sorted(self.Hs,key = lambda y:y.get_dist(delta_atom))
                self.delta_atoms = [delta_atom.name,dists[0].name,delta_atom2.name]
                return self.delta_atoms

    def output_LCH(self,path):
        with open(f"{path}/LCH.pdb","w") as outfile:
            for line in self.lines:
                outfile.write(f"{line[0:17]}LCH{line[20:]}")
    
    def output_LPN(self,path):
        with open(f"{path}/LPN.pdb","w") as outfile:
            for line in self.lines:
                if self.delta_atoms[0] not in line and self.delta_atoms[1] not in line:
                    outfile.write(f"{line[0:17]}LPN{line[20:]}")
                elif self.delta_atoms[0] in line:
                    outfile.write(f"{line[0:12]} {self.delta_atoms[2]:<3} LPN{line[20:]}")

class Amino:
    def __init__(self,amino) -> None:
        self.lines = amino
        # change HSE/HSD to HIE/HID
        if amino[0].split()[3] == "HSE":
            self.name = "HIE"
        elif amino[0].split()[3] == "HSD":
            self.name = "HID"
        else:
            self.name = amino[0].split()[3]
        # deal with the info of atoms
        self.atoms = {}
        i = 0
        for line in amino:
            self.atoms[i] = Atom(line)
            i += 1
        # get the count of the atoms, to decide if the amino is the N-terminal or the C-terminal
        self.atom_count = len([self.atoms[key].name for key in self.atoms.keys()])

class System:
    def __init__(self,pdb):
        self.protein_line = []
        self.ligands_line = []
        self.aminos = {}
        with open(pdb) as pdb_info:
            for line in pdb_info:
                if "ATOM" in line or "HETATM" in line:
                    if "LIG" in line:
                        if "LP" not in line:
                            self.ligands_line.append(line)
                    else:
                        self.protein_line.append(line)
        self.ligand = Ligand(self.ligands_line)     
    
    def get_aminos(self,):
        amino_th = [self.protein_line[0]]
        for i in range(len(self.protein_line)-1):
            if i < len(self.protein_line)-2:
                # if the order does not change, the atoms of two lines belong to one amino.
                if self.protein_line[i][22:32] == self.protein_line[i+1][22:32]:
                    #print(self.protein_line[i+1])
                    amino_th.append(self.protein_line[i+1])
                else:
                    #when the amino order change, the amino_th array contain the all atoms of last amino
                    # use the amino order as the key, amino class as the value
                    self.aminos[int(amino_th[0][23:32])] = Amino(amino_th)
                    amino_th = []
                    amino_th.append(self.protein_line[i+1])
            else:
                # ensure the last one 
                amino_th.append(self.protein_line[i+1])
                self.aminos[int(amino_th[0][23:32])] = Amino(amino_th)

    def output_pro_amber(self,path,ref):
        with open(f"{path}/complex.pdb","w") as outfile:
            for key in self.aminos.keys():
                # basic length is the atom count in chain, N terminal has 2 atoms more; C termial has 1 more.
                basic_length = len(ref[self.aminos[key].name][0])
                atoms_re_name = ref[self.aminos[key].name][self.aminos[key].atom_count-basic_length]
                for line, atomname in zip(self.aminos[key].lines,atoms_re_name):
                    if len(atomname) < 4:
                        outfile.write(f"{line[0:12]} {atomname:<4}{self.aminos[key].name} {line[21:]}")
                    else:
                        outfile.write(f"{line[0:11]} {atomname:<4} {self.aminos[key].name} {line[21:]}")
                if self.aminos[key].atom_count-basic_length == 1:
                    # when there is a C terminal, add the TER line
                    outfile.write("TER\n")

def parse_ref(ref):
    info = []
    with open(ref) as infile:
        amino_atoms = infile.read()
    info = amino_atoms.split("\n\n")
    amino_re_atoms = {}
    for inf in info:
        inf = inf.split("\n")
        amino_name = inf[0]
        atoms_in_amino = {}
        for i in range(3):
            atoms_in_amino[i] = inf[i+1][1:-1].replace("\'"," ").replace(","," ").split()
        amino_re_atoms[amino_name] = atoms_in_amino
    return amino_re_atoms
# text.ref has the atom names used in amber.
chain = parse_ref("text.ref")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="gmx dir")
    parser.add_argument(
        "--gmx_dir",
        dest='gmx_dir',
        )
    
    gmx_dir = Path(parser.parse_args().gmx_dir)
    systems = sorted([System(path) for path in gmx_dir.glob("CHEMBL*/em.pdb")],key = lambda y: y.ligand.number, reverse=True)
    delta_atoms = systems[0].ligand.compare(systems[1].ligand)
    systems[0].ligand.output_LCH(".")
    systems[0].ligand.output_LPN(".")
    systems[0].get_aminos()
    systems[0].output_pro_amber(".",chain)



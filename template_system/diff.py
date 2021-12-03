import sys 

class atom:
    def __init__(self,line):
        info = line.split()
        self.name = info[2]
        self.x = float(info[6])
        self.y = float(info[7])
        self.z = float(info[8])
        self.cor=(self.x,self.y,self.z)
        self.type = self.name[0]
    def getdist(self,atom):
        return (atom.x-self.x)**2+(atom.y-self.y)**2+(atom.z-self.z)**2 


lig=[{}]
with open(sys.argv[1]) as ligspdb:
    for line in ligspdb:
        if line[0:6] == "HETATM": 
            lig[-1][atom(line).cor] = atom(line)
        else:
            lig.append({})

diff=[[],[]]
for item in lig[0]:
    if item in lig[1] and lig[0][item].type==lig[1][item].type:
        pass
    else:
        diff[0].append(lig[0][item].name)
for item in lig[1]:
    if item in lig[0] and lig[0][item].type==lig[1][item].type:
        pass
    else:
        diff[1].append(lig[1][item].name)

print(str(diff[0])[2:-2].replace("', '",",")+"_"+str(diff[1])[2:-2].replace("'",""))

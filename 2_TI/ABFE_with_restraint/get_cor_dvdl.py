with open("ti001.out") as infos:
    info = infos.read().split("A V E R A G E S   O V E R ")[1].split("\n")

DVDL = [float(item.split("=")[1]) for item in info if 'DV/DL' in item ]
dVDl = [float(item.split("=")[1]) for item in info if 'dV/Dl' in item ]

with open("ti.res","w") as out:
    out.write(f"{DVDL[0]-dVDl[0]:.4f}\n") 

print(f"{DVDL[0]-dVDl[0]:.4f}\n")
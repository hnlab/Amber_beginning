import math 
import numpy as np 
import os
from pathlib import Path
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import argparse

lig_desolvation = 56.56

def extrap_polyfit(x,y):
    coeffs = np.polyfit(x, y, 6)
    if 0.0 not in x:
        x.insert(0, 0.0)
        y.insert(0, coeffs[-1])
    if 1.0 not in x:
        x.append(1.0)
        y.append(sum(coeffs))
    return (x,y)

def TI_plot(x,y,err,outpath):
    plt.title("TI plot ")
    plt.xlabel('lambda',labelpad = -30,loc = 'right') 
    plt.ylabel("<dU/dlambda>")
    ax = plt.subplots()[-1]
    ax.spines['right'].set_color('none') 
    ax.spines['top'].set_color('none')         # 将右边 上边的两条边颜色设置为空 其实就相当于抹掉这两条
    ax.xaxis.set_ticks_position('bottom')   
    ax.yaxis.set_ticks_position('left')          # 指定下边的边作为 x 轴   指定左边的边为 y 轴
    ax.spines['bottom'].set_position(('data', 0))   #指定 data  设置的bottom(也就是指定的x轴)绑定到y轴的0这个点上
    ax.spines['left'].set_position(('data', 0))
    plt.errorbar(x,y,yerr=err,fmt='o:',ecolor='red',elinewidth=3,ms=5,mfc='wheat',mec='salmon',capsize=3)
    ix=np.array(x)
    iy=np.array(y)
    ixy=list(zip(ix,iy))
    ixy=[(0.0,0.0)]+ixy+[(1.0,0.0)]
    poly=mpatches.Polygon(ixy,facecolor='0.8',edgecolor='0.1')
    ax.add_patch(poly)
    plt.savefig(outpath)
    return(f"The TI figure is {str(outpath)}")

parser = argparse.ArgumentParser(description="Plot TI figure")
parser.add_argument(
    "--data",
    dest='data',
)
info = parser.parse_args().data
p=Path(info)
#name_of_cal=f"{str(p.parts[5])}_{str(p.parts[6])}_{str(p.parts[7])}_{str(p.parts[8])}"
windows = list(p.glob("**/ti001.en"))
dvdl=p/"dvdl_re.dat"

data = OrderedDict()
for window in windows:
    step_lambda = window.parts[-2]
    density = np.array([])
    dVdl_np= np.array([])
    step_dVdl=np.array([])
    ln = 0
    with window.open() as en:
        for line in en:
            ln += 1
            if line[0:2]=="L9" and not 'dV/dlambda' in line:
                dVdl_np = np.append(dVdl_np,float(line.split()[5]))
    try:
        #print(dVdl_np.size)
        mean=np.mean(dVdl_np)
        std_np=math.sqrt(((dVdl_np-np.mean(dVdl_np))**2).sum())/(dVdl_np.size-1)
        data[float(step_lambda)]=(mean, std_np, dVdl_np.size)
    except:
        print(f"There is some errors in {window}")
        os._exit(0)

    
x = list(data.keys())
x.sort()
y = [data[l][0] for l in x]

arr = [i for i in range(len(x)) if x[i] != 0.00922 and x[i] != 0.99078 ]
x_m = [x[i] for i in arr]
y_m = [y[i] for i in arr]

x,y=extrap_polyfit(x,y)
x_m,y_m = extrap_polyfit(x_m,y_m)

rmse_tot = 0.0
for i in range(1,len(x)-1):
    rmse_tot += 0.5*(x[i+1]-x[i-1])*data[x[i]][1]

outpath=p/f"TI_plot2.png"

with open(dvdl,"w") as out:
    for a, b in zip(x, y):
        if a in data:
            v = data[a]
            out.write(f"{a}\t{v[0]:> 10.4f}\t{v[1]:> 10.4f}\t{v[2]}\n")
        else:
            out.write(f"{a:0<7}\t{b:> 10.4f}\t{0.0:> 10.4f}\t{0:4}\n")
    out.write(f"#   dG = {np.trapz(y, x):> 8.4f}\n# RMSE = {rmse_tot:> 8.4f}\n")

with open("dG_cor") as res:
    dG_cor = float(res.read().split("\n")[0])

res_with_end = np.trapz(y, x)-lig_desolvation + dG_cor
res_without_end = np.trapz(y_m, x_m)-lig_desolvation + dG_cor
print(f"dG = {res_with_end:.2f}\ndG without end is {res_without_end:.2f}, the difference is {res_with_end-res_without_end:.2f}")
x,y,err=[],[],[]
with dvdl.open() as dat:
    for line in dat:
        if line[0] != "#":
            line = line.split()
            x.append(float(line[0]))
            y.append(float(line[1]))
            try:
                err.append(float(line[2]))
            except:
                 err.append(float(0))
        else:
            dG = float(line.split()[-1]) 
print(TI_plot(x,y,err,outpath))
# print(err)

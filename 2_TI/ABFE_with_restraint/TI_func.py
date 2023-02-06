import math 
import numpy as np 
import os
from pathlib import Path
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import argparse

def ens_parser(en_files):
    data = OrderedDict()
    for window in en_files:
        step_lambda = window.parts[-2]
        dVdl_np= np.array([])
        ln = 0
        with window.open() as en:
            for line in en:
                ln += 1
                if line[0:2]=="L9" and not 'dV/dlambda' in line:
                    dVdl_np = np.append(dVdl_np,float(line.split()[5]))
        try:
            mean=np.mean(dVdl_np)
            std_np=math.sqrt(((dVdl_np-np.mean(dVdl_np))**2).sum())/(dVdl_np.size-1)
            data[float(step_lambda)]=(mean, std_np, dVdl_np.size)
        except:
            print(f"There is some errors in {window}")
            os._exit(0)
    if len(data.keys()) < 12:
        print(f"only {data.keys()}")
        os._exit(0)
    return data

def out_parser(out_files):
    data = OrderedDict()
    for out in out_files:
        step_lambda = out.parts[-2]
        dVdl_np= np.array([])
        with out.open() as infos:
            try:
                info = infos.read().split("A V E R A G E S   O V E R ")[1].split("\n")
                DVDL = [float(item.split("=")[1]) for item in info if 'DV/DL' in item ]
                dVDl = [float(item.split("=")[1]) for item in info if 'dV/Dl' in item ]
                data[float(step_lambda)]=(DVDL[0]-dVDl[0], 0.0, 18)
            except:
                print(f"There is some errors in {step_lambda}")
                os._exit(0)
    return data

def extrap_polyfit(x,y):
    coeffs = np.polyfit(x, y, 6)
    if 0.0 not in x:
        x.insert(0, 0.0)
        y.insert(0, coeffs[-1])
    if 1.0 not in x:
        x.append(1.0)
        y.append(sum(coeffs))
    return (x,y)

def data_calculate(data):
    x = list(data.keys())
    x.sort()
    y = [data[l][0] for l in x]
    x,y=extrap_polyfit(x,y)
    rmse_tot = 0.0
    for i in range(1,len(x)-1):
        rmse_tot += 0.5*(x[i+1]-x[i-1])*data[x[i]][1]
    return (x,y,rmse_tot)

def res_output(outpath,data,x,y,rmse_tot):
    with open(outpath,"w") as out:
        for a, b in zip(x, y):
            if a in data:
                v = data[a]
                out.write(f"{a}\t{v[0]:> 10.4f}\t{v[1]:> 10.4f}\t{v[2]}\n")
            else:
                out.write(f"{a:0<7}\t{b:> 10.4f}\t{0.0:> 10.4f}\t{0:4}\n")
        out.write(f"#   dG = {np.trapz(y, x):> 8.4f}\n# RMSE = {rmse_tot:> 8.4f}\n")
    print(f"dG = {np.trapz(y, x):.2f}")

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

def dvdl_draw(dvdl,pngpath):
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
    print(TI_plot(x,y,err,pngpath))
    return True

def get_dG(target_dir,ifcon):
    windows = list(target_dir.glob("**/ti001.en"))
    data = ens_parser(windows)
    x,y,rmse_tot = data_calculate(data)
    x_con,y_con = x[2:-2],y[2:-2]
    x_con,y_con = extrap_polyfit(x_con,y_con)
    dvdl_dat=target_dir/"dvdl_re.dat"
    res_output(dvdl_dat,data,x,y,rmse_tot)
    pngpath=target_dir/f"TI_plot2.png"
    dvdl_draw(dvdl_dat,pngpath)
    dG_all = np.trapz(y,x)
    dG_con = np.trapz(y_con, x_con)
    if ifcon:
        # outs = list(target_dir.glob("**/ti001.out"))
        # data_out = out_parser(outs)
        # x_out,y_out,rmse_tot = data_calculate(data_out)
        # x_con,y_con = x[2:-2],y[2:-2]
        # x_con,y_con = extrap_polyfit(x_con,y_con)
        # dG_all_res = np.trapz(y_out, x_out)
        # dG_con_res = np.trapz(y_con, x_con)
        # return (dG_all,dG_con,dG_all_res,dG_con_res,rmse_tot)
        return (dG_all,dG_con,rmse_tot)
    else:
        return (dG_all, rmse_tot)

def get_ddG(path):
    ligand_res = get_dG(path/"free_energy/ligands",False)
    complex_res = get_dG(path/"free_energy_VBA_2/complex",True)
    with open(str(path/"free_energy_VBA_2/dG_cor")) as cor:
        dG_cor = float(cor.read().split()[0])
    rmse = math.sqrt(ligand_res[-1]**2+complex_res[-1]**2)
    ddG_all = complex_res[0]+dG_cor-ligand_res[0]
    ddG_con = complex_res[1]+dG_cor-ligand_res[0]
    # ddG_all_res = complex_res[2]+dG_cor-ligand_res[0]
    # ddG_all_con = complex_res[3]+dG_cor-ligand_res[0]

    data_bio = {}
    with open("/pubhome/yjcheng02/clr_abfe/ABFE/bio.res") as bio:
        for line in bio:
            ligand, bio_info = line.split()
            data_bio[ligand] = (0.1987*3.0) * math.log(float(bio_info)*10**(-9))
    
    name = f"A{path.absolute().name[-2:]}"
    # info=f"{data_bio[name]:.2f}\n{ddG_all:.2f}\n{ddG_con:.2f}\n{ddG_all_res:.2f}\n{ddG_all_con:.2f}\n{rmse:.2f}\n"
    info=f"{data_bio[name]:.2f}\n{ddG_all:.2f}\n{ddG_con:.2f}\n{rmse:.2f}\n"
    with open(f"{str(path)}/VBA_res",'w') as VBA:
        VBA.write(info)
    print(info)
    return True

parser = argparse.ArgumentParser(description="Plot TI figure")
parser.add_argument(
    "--data",
    dest='data',
)

info = parser.parse_args().data
p=Path(info)
get_ddG(p)


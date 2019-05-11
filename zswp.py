#!/home/miniconda3/bin/python
# -*- coding: utf-8 -*-
import os,sys,json
import numpy as np

from  datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from matplotlib.path import Path
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.patch import geos_to_path
from cartopy.io.shapereader import natural_earth, Reader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import utils

# 日志文件
LOG_FILENAME = './logs/zswp.log'  # 日志文件名
log = utils.Logger(logname=LOG_FILENAME, loglevel=2, logger="main").getlog()




def mask_region( olon, olat, path ):
    # lon,lat : grid data lon lat , 1e-10
    points = np.array((olon.flatten(), olat.flatten())).T
    # print(points)
    mask = path.contains_points(points).reshape(olon.shape)
    return mask

def cal_region_of_rain(subfname,path, pre_ll, olat, olon):
    shape_records = Reader(subfname).records()
    region_list = []
    for country in shape_records:
        pre_mask = pre_ll.copy()
        name = country.attributes['NAME']
        geoms = [ country.geometry ]
        path = Path.make_compound_path(*geos_to_path(geoms))
        mask = mask_region(olon, olat, path)
        pre_mask[ mask == False] = 0
        pre_mask = np.where(pre_mask >=20, 20, 0)
        pre_count = np.count_nonzero(pre_mask)
        print(name)
        print(pre_count)
        if pre_count >=1:
            region_list.append(name)


    return region_list


if __name__ == '__main__':
    cnfont = {'fontname':'simhei'}
    timeref = datetime(2010,1,1) 
    # 取最近的10min
    now_minutes = (datetime.utcnow() - timeref).total_seconds()//600 * 10
    time = ( timeref + timedelta(minutes=now_minutes) ).strftime('%Y%m%d%H%M%S')
    time = '20190424150000'
    print(time)
    lon_s, lat_s, olon, olat, pre_ll = cimissapi.getPRE1hr(time)
    pre_ll = pre_ll * 10

    print("plot figure")
    fname = r"./boundary/city.shp"#u'Province.shp'
    subfname = r"./boundary/town.shp" #u'cnmap/City.shp'
    subsubfname = r"./boundary/village.shp"
    plt.figure(figsize=(12,9),dpi=100)
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax.background_patch.set_facecolor('0.95') 
    ax.add_geometries(Reader(subsubfname).geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='black',linewidth=0.2,alpha=0.3,zorder=10)
    ax.add_geometries(Reader(subfname).geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='black',linewidth=0.5,alpha=0.3,zorder=10)
    ax.add_geometries(Reader(fname).geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='gray',linewidth=1.2,alpha=1, zorder=10)
    colors = np.array( [ [255,255,255],[166,242,143], [61,186,61], [97,184,255], [0,0,225] ] ,dtype='f4')
    # cmap = matplotlib.colors.ListedColormap(colors/255., name='rain_cmap')
    levels =np.array([20,30,50,80],dtype='i')
    cmap , norm = mpl.colors.from_levels_and_colors(levels, colors/255, extend='both' ) # extend='both'
    
    im = ax.contourf(olon, olat, pre_ll, levels=levels,cmap=cmap, norm=norm, extend='both' ,transform=ccrs.PlateCarree())
    # im = ax.pcolormesh(olon, olat, pre_ll ,cmap='jet', transform=ccrs.PlateCarree())
    clb = plt.colorbar(im,  cax=inset_axes(ax, width="2%", height="30%",loc=4,borderpad=2), extend='both',extendfrac='auto',extendrect=True )  # orientation='horizontal',
    clb.ax.tick_params(axis='y', length=0., width=0.3,direction='in',labelsize=6)
    # clb.ax.set_title(r'$\rm ug/m^2$',fontsize=12,position=(1.2, 1),)

    ax.set_xticks( np.arange(112.75, 114.5, 0.25), crs=ccrs.PlateCarree())
    ax.set_yticks( np.arange(34,     35.5,   0.25), crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.set_xlim(112.68, 114.28)
    ax.set_ylim(34.1, 35.3)

    ax.text(0.5, 0.85,'郑州市1小时降水实况(mm) 2019-04-24 23:00:00',verticalalignment='bottom',horizontalalignment='center',transform=ax.transAxes,color='k', fontsize=18, **cnfont)


    # 白化区域    
    shape_records = Reader(subfname).records()
    geoms = []
    for country in shape_records:
        geoms += country.geometry
    path = Path.make_compound_path(*geos_to_path(geoms))
    for collection in im.collections:
        collection.set_clip_path(path, ccrs.PlateCarree()._as_mpl_transform(ax))

    # 计算极大值中心
    # mask 数组
    mask = mask_region(olon, olat, path)
    print(mask.shape)
    pre_ll[ mask == False] = 0
    idx = np.unravel_index(np.nanargmax(pre_ll), pre_ll.shape)
    lon_max, lat_max = olon[idx[0],idx[1]],olat[idx[0],idx[1]]
    print(lon_max)
    print(lat_max)
    ax.text(lon_max, lat_max, "{:.1f}".format(pre_ll[idx[0],idx[1]]) ,bbox=dict(boxstyle="round,pad=0.3",ec='none',fc='white',alpha=0.7), withdash=True,verticalalignment='bottom',horizontalalignment='center',transform=ccrs.PlateCarree(),color='k', fontsize=10)
    ax.scatter(lon_max, lat_max, label=u'降水中心',c='black',s=20,marker='x', transform=ccrs.PlateCarree(),zorder=100)
    ax.legend(bbox_to_anchor=(0.95, 0), loc=4, borderaxespad=2,prop={'family':'simhei'})
    
    plt.savefig("rain_sample.png" ,bbox_inches='tight')
    plt.close()

    # 计算降水区域
    region_list = cal_region_of_rain(subfname,path, pre_ll, olat, olon)
    print(region_list)
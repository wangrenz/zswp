# -*- coding: utf-8 -*-

import logging
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.mpl.patch import geos_to_path

class Logger():

    def __init__(self, logname, loglevel, logger):
        '''
           指定保存日志的文件路径，日志级别，以及调用文件
           将日志存入到指定的文件中
        '''
        logDict = {
            1: logging.DEBUG,
            2: logging.INFO
        }
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(logname)
        fh.setLevel(logDict[int(loglevel)])
        
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
    
    def getlog(self):
        return self.logger



def add_shp(ax,region:str):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shapefile')
    flist = [os.path.join(root, i) for i in ['city', 'town', 'village']]
    shps = [Reader(i).geometries() for i in flist]
    if region == 'city':
        ax.add_geometries(shps[2].geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='black',linewidth=0.2,alpha=0.3,zorder=10)
        ax.add_geometries(shps[1].geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='black',linewidth=0.5,alpha=0.3,zorder=10)
        ax.add_geometries(shps[0].geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='gray',linewidth=1.2,alpha=1, zorder=10)
    elif region == 'town':
        ax.add_geometries(shps[2].geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='black',linewidth=0.5,alpha=0.3,zorder=10)
        ax.add_geometries(shps[1].geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='gray',linewidth=1.2,alpha=1, zorder=10)
    else:
        pass

def mask_region( olon, olat, path ):
    # lon,lat : grid data lon lat , 1e-10
    points = np.array((olon.flatten(), olat.flatten())).T
    # print(points)
    mask = path.contains_points(points).reshape(olon.shape)
    return mask

def cal_region_of_rain(region, pre_ll, olat, olon):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shapefile')
    fname = os.path.join(root, 'town' if region == 'city' else 'village')
    shape_records = Reader(fname).records()
    
    region_list = []
    for country in shape_records:
        pre_mask = pre_ll.copy()
        name = country.attributes['NAME'] if region == 'city' else country.attributes['RNAME']
        geoms = [ country.geometry ]
        path = Path.make_compound_path(*geos_to_path(geoms))
        mask = mask_region(olon, olat, path)
        pre_mask[ mask == False] = 0
        pre_mask = np.where(pre_mask >=20, 20, 0)
        pre_count = np.count_nonzero(pre_mask)
        log.info(name)
        log.info(pre_count)
        if pre_count >=1:
            region_list.append(name)
    return region_list


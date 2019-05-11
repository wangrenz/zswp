# -*- coding: utf-8 -*-
import os
import utils
from utils import (setup_plot, add_shp ,save, setup_axes, setup_plot,)
import numpy as np
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
from datetime import datetime, timedelta

class PRE(object):
    r'''
    Create a figure plotting plan position indicator
    Attributes
    ----------
    data: grid data
    settings: dict
        settings extracted from __init__ function
    geoax: cartopy.mpl.geoaxes.GeoAxes
        cartopy axes plotting georeferenced data
    fig: matplotlib.figure.Figure
    '''
    # mode: obs_1hr, foc_1hr, foc_2hr
    _mode   = {'obs_1hr': u'1小时降水实况(mm) ','foc_1hr':u'1小时降水预报(mm)','foc_2hr':u'2小时降水预报(mm)'}
    _extent = {'city':[112.75, 114.5, 34, 35.5], 'town':[113.3, 113.9, 34.5, 35.2]}
    def __init__(self, time:str, olon, olat, data, figsize:tuple=(12, 9), dpi:int=100,mode:str, region:str,add_city_names:bool=False, plot_labels:bool=True, **kwargs):
        self.time = time
        self.olon = olon
        self.olat = olat
        self.data = data
        self.settings = {'mode':_mode[mode],'name': u'郑州市' if region=='city' else u'郑州市中心' , 'region':region, 'add_city_names':add_city_names }
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self._plot(**kwargs)

    def _plot(self, **kwargs):
        _cnfont = {'fontname':'simhei'}
        self.geoax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())

        colors = np.array( [ [255,255,255],[166,242,143], [61,186,61], [97,184,255], [0,0,225] ] ,dtype='f4')
        levels =np.array([20,30,50,80],dtype='i')
        cmap , norm = mpl.colors.from_levels_and_colors(levels, colors/255, extend='both' )

        self.im = self.geoax.contourf(self.olon, self.olat, self.data, levels=levels,cmap=cmap, norm=norm, extend='both' ,transform=ccrs.PlateCarree())
        self.clb = plt.colorbar(self.im,  cax=inset_axes(ax, width="2%", height="30%",loc=4,borderpad=2), extend='both',extendfrac='auto',extendrect=True ) 
        self.clb.ax.tick_params(axis='y', length=0., width=0.3,direction='in',labelsize=6)
        self.geoax.set_xticks( np.arange(113, 115, 0.25), crs=ccrs.PlateCarree())
        self.geoax.set_yticks( np.arange(34,   36, 0.25), crs=ccrs.PlateCarree())
        self.geoax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
        self.geoax.yaxis.set_major_formatter(LatitudeFormatter())
        add_shp(self.geoax, region=self.settings['region'] )
        add_title(self.geoax, region=self.settings['region'])

        self.geoax.text(0.5, 0.85, datetime.strptime(self.time,'%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S') + self.settings['name'] + self.settings['mode'], \
            verticalalignment='bottom',horizontalalignment='center',transform=ax.transAxes,color='k', fontsize=18, **_cnfont)
        _minlon, _maxlon, _minlat, _maxlat =  _extent[ self.settings['region'] ]
        self.geoax.set_extent(_minlon, _maxlon, _minlat, _maxlat, ccrs.PlateCarree())
        fpath = time + '.png'
        plt.savefig(fpath, bbox_inches='tight', pad_inches=0)
        plt.close('all')

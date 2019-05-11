# -*- coding: utf-8 -*-
import os,sys,json
import utils
import numpy as np
import pandas as pd
import urllib.request as urllib2
import naturalneighbor
from  datetime import datetime, timedelta

class cimissapi:
    #  time， string, YYYYMMDDHHMISS
    def __init__(self,):
        self.baseUrl = 'http://10.69.89.55/cimiss-web/api?&userId=BEZZ_BFZZ_zzqxj&pwd=66812246'
        self.dataFormat = 'json'
        #self.interfaceId = 'getSurfEleInRectByTime'
        self.minLat = '32'
        self.minLon = '110'
        self.maxLat = '37'
        self.maxLon = '118'
        self._url = self.baseUrl + '&dataFormat=' + self.dataFormat
        self._url += '&minLat=' + self.minLat
        self._url += '&minLon=' + self.minLon
        self._url += '&maxLat=' + self.maxLat
        self._url += '&maxLon=' + self.maxLon
    # 获取数据
    @staticmethod
    def checkStationExistData(url):
        _req = urllib2.Request(url)
        _response = urllib2.urlopen(_req)
        _root = json.loads(_response.read())
        return _root['returnCode']
    @staticmethod
    def getStationData(url):
        _req = urllib2.Request(url)
        _response = urllib2.urlopen(_req)
        _root = json.loads(_response.read())
        _data = pd.DataFrame(_root['DS'])
        return 	_data
    @staticmethod
    def intrp2grid(lon, lat, zvalue):
        _res    = 0.01
        _minLon = 112.2
        _minLat = 33.7
        _maxLon = 114.6
        _maxLat = 35.4
        _step   = 0.01
        olon = np.linspace(_minLon,_maxLon, int( (_maxLon - _minLon)/ _res + 0.1) +1 )
        olat = np.linspace(_minLat,_maxLat, int( (_maxLat - _minLat)/ _res + 0.1) +1 )
        olon,olat = np.meshgrid(olon,olat)
        # 站点插值到格点
        lon_lat = np.vstack((lon,lat,np.ones(lon.shape[0])))
        zvalue_new = naturalneighbor.griddata(lon_lat.T, zvalue, [[_minLon,_maxLon+_step, _step],[_minLat,_maxLat+_step,_step],[0 ,1 ,1]])
        zvalue_new = zvalue_new[:,:,0].T
        return olon, olat, zvalue_new,_step

    @staticmethod
    def getPRE1hr(time):
        _time_1hr = (datetime.strptime(time,'%Y%m%d%H%M%S') - timedelta(hours=1) ).strftime('%Y%m%d%H%M%S')
        r_cimiss = cimissapi()
        url = r_cimiss._url + '&interfaceId=getSurfEleInRectByTimeRange'
        url+= '&datacode=SURF_CHN_PRE_MIN'
        url+= '&timeRange=(' + _time_1hr + ',' + time + ']'
        url+= '&elements=Datetime,Station_Id_C,Lon,Lat,PRE'
        io_err = r_cimiss.checkStationExistData(url)
        if io_err != '0':
            return io_err
        pre = r_cimiss.getStationData(url)
        log.info('时间：' +time + ', 降水自动站个数：' + str(len(pre)))
        if len(pre) < 700:
            log.info('站数过少，程序退出')
            exit()

        pre[['Lon','Lat','PRE']] = pre[['Lon','Lat','PRE']].astype('f') 
        pre = pre[pre['PRE'] != 999999]
        pre = pre.sort_values(by='Station_Id_C',ascending=True)

        lon_lat = pre.drop_duplicates(['Station_Id_C'])
        pre_p = pre.set_index(['Station_Id_C','Datetime']).sum(level='Station_Id_C')
        log.info('站点插值到格点')
        olon, olat, pre_ll, step = r_cimiss.intrp2grid(lon_lat['Lon'].values, lon_lat['Lat'].values, pre_p['PRE'].values)
        log.info('插值完毕')
        pre_ll = np.around(pre_ll, decimals=1)
        return olon, olat, pre_ll
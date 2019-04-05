#!/usr/bin/python2
# -*- coding: utf-8 -*-

from numpy import  *
from  urllib2 import urlopen
import shutil
import os


def golem_data(shot, diagn):
    """
     Simple interface for GOLEM database
      Use:
	obj = golem_data(10011, 'loop_voltage')
	plot(obj.tvec, obj.data)

	d - object containing all availible informations
	d.tvec  - time vector Nx1
	d.data - data matrix  NxM

      Example:
      from golem_data import golem_data
      from matplotlib.pyplot import *
      obj1 = golem_data(10689 , 'electron_temperature')
      obj2 = golem_data(10689 , 'spectrometr:temperature')
      plot(obj1.tvec,obj1.data,  label=obj1.labels)  %
      errorbar(obj2.tvec, obj2.data, xerr=obj2.tvec_err, yerr=[obj2.data_err[:,0], obj2.data_err[:,1]],  label=obj2.labels )
      xlabel(obj2.ax_labels[0])
      ylabel(obj2.ax_labels[1])
      legend([obj1.name, obj2.name])
      axis([obj1.plasma_start, obj1.plasma_end, 0, None])
      title(obj1.info)
      show()
    """

    remote_file = "http://golem.fjfi.cvut.cz/utils/data/"+str(shot)+"/"+diagn+'.npz'

    gfile = DataSource().open(remote_file)  # remote file
    print(gfile)

    try:
        d =  dict(load(gfile))
    except IOError:
        raise IOError('Missing diagnostic ' + str(diagn) + ' in shot ' + str(shot))

    if not 'tvec' in d and 't_start' in d:
        d['tvec'] = linspace( d.pop('t_start'), d.pop('t_end'), len(d['data']) )

    try:
        if 'scale' in d:
            d['data'] = double(d['data']) * d.pop('scale')  # rescale data
    except:
        pass
    return Data( **d )


class Data(object):
    """ Simple data handling object"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
	    return "Data object, keys:\n" + str(self.__dict__.keys())
    def __getitem__(self, key):
        return getattr(self, key)

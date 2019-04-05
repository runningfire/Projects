import requests
from numpy import *


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
  show() #need to use a wormhole between python and matlab... keep working
"""


def ResponseSite(shot=30228,diagn='loop_voltage'):
    file = open(r'C:\projects\inform.npz', 'wb')
    rspns = requests.get("http://golem.fjfi.cvut.cz/utils/data/"+str(shot)+"/"+diagn+'.npz')
    file.write(rspns.content)
    file.close()
    try:
        d =  dict(load('C:\projects\inform.npz'))
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
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "Data object, keys:\n" + str(self.__dict__.keys())
    def __getitem__(self, key):
        return getattr(self, key)


data = ResponseSite()
print((len(data.data)))

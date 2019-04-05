from numpy import *
import re, os #for contents_regexp()
import ConfigParser #for dynamically updating the data*_types dictionaries
import sys, cStringIO
import time, socket
from copy import copy, deepcopy
from utilities import *
from Data import *
from collections import OrderedDict
from sql import load_value
from tags import *

__all__ = ['Shot', 'Data',  'loadconst', 'load_adv',
	    'saveconst', 'save_adv', 'save_adv_par','get_current_shot', 'base_path' ]


data_config = 'data_configuration.cfg' #file to sue with ConfigParser
das_config = "das_configuration.cfg"

# load default_path => either vshots or shots
default_path = ""
if 'SHOT_PATH' in os.environ:
    default_path = os.environ['SHOT_PATH']

if default_path == "" :
    #print " os.environ SHOT_PATH could not be loaded "
    default_path  = "shots"

base_path = "/srv/www/svoboda/golem/"+default_path

def get_current_shot():
    #return  int(open("/srv/www/svoboda/golem/root/ActualShotNo").read())
    try:
	return int(open(base_path+'/0/ShotNo').read())
    except:
	return 11500  # in case of serios failure



def save_adv_par(*args, **kwargs):
    #print "!!!! SAVING IN PARALEL!!!"
    import multiprocessing
    multiprocessing.Process(target=save_adv, args=args, kwargs=kwargs).start()



def save_adv(fname, tvec, data = None, scale = 1, tvec_err = None, data_err = None, axis = None,  filetype='npz' ):
    """ Save data in a very efficient way to compressed binary single / integers
    param str fname:  Name of saved file
    param array tvec:  time vector for 1-th dimension of data array
    param str data: data array
    param float scale: scale used to renormalize `data` (ie. if `data` are saved
    as integers
    param array data_err: Errorbars in data vector
    param list axis: ticks of 2th to n-th axis
    """

    if data is None and type(tvec) is Data: # only one argument was used
	data = tvec
	tvec = data.tvec

    if asarray(data).dtype == float and data.ndim > 0:  # not for integers and scalars
	data = single(data)

    data_all = { 'data':array(data), 'scale':scale }

    if type(data) is Data:
	for attr in data_attributes :
	    if attr not in ['tvec', 'signal', 'axis']:
		data_all.update( {attr: getattr(data, attr, None)} )

    else:
	if type(tvec_err) is list: tvec_err = array(tvec_err).T
	if type(data_err) is list: data_err = array(data_err).T
	data_all.update( {'tvec_err':array(tvec_err), 'data_err': data_err, 'axis':axis } )
    if not any(isnone(tvec)):
	dt = mean(diff(tvec))
	if all(abs(diff(tvec) - dt) <  dt * 1e-3):  # equidistant time vector
	    data_all['t_start'] = tvec[0]
	    data_all['t_end'] = tvec[-1]
	else:
	    data_all['tvec'] = single(tvec)
    if filetype == 'npz':
	savez_compressed(fname,  **data_all )  # in cas eof nonequidistant time vector !!
    elif filetype == 'mat':
	from scipy.io import savemat
	for i in data_all.keys():
	    if any(isnone(data_all[i])):   # remove None
		data_all[i] = []
	savemat(fname , data_all, do_compression=True )
    else:
	raise NotImplementedError('Use npz or mat filetype')
    return data_all



def load_adv(fname_0, testRun = False):
    """
    Universal loader of data from saved files
    Supported filetypes: npz, npy, csv, txt, '', lvm
    param str fname:  Name of saved file
    param bool testRun: use only dry run to test existance of the data

    """
    if not os.path.exists(fname_0):
	fname = find_data(fname_0)
    else:
	fname = fname_0

    if not fname:
	raise IOError, "Missing file: "+fname_0

     # npz prefered effecient format !!!
    load_list = [
	    #"imread('"+fname+ ".png')", \    # needs to load pyplot => slow !!
	    "load('"+fname+"')", \
	    "loadtxt('"+fname+"')", \
	    "loadtxt('"+fname+ "', delimiter=';')", \
	    ]

    for f in load_list:
	try:
	    data_0 = eval(f)
	except: # IOError or ValueError:
	    pass

    if not 'data_0' in locals():
	raise IOError, "Corrupted file: "+fname_0

    if size(data_0) == 0:
	raise IOError('Empty file: '  + fname_0)

    if type(data_0) is Data:
	tvec = Data.tvec
	sig = Data
    elif type(data_0) is ndarray:   # data saved ar ordinary array
	if data_0.dtype == "object":
	    return None, data_0.item()   #  for example datetime object
	#print 'Warning: saving to binary: ',fname
	assert size(data_0) != 1, 'Use loadconst function'
	if ndim(data_0) == 1:
	  tvec = None
	  sig = Data(data_0[:,1:])
	else:
	  tvec = data_0[:,0]
	  sig = Data(data_0[:,1:], tvec = tvec)
	try:
	    save_adv(re.sub('(.+)\.(.+)', r'\1', fname), sig) # save as compressed binary file
	except:
	    pass
    else:
	##  time vector
	if 't_start' in data_0 and 't_end' in data_0:  # data saved without time vector
	    tvec = linspace(data_0['t_start'], data_0['t_end'], len(data_0['data']))
	elif 'tvec' in data_0:
	    tvec = double(data_0['tvec'])
	else:
	    raise NotImplementedError

	# data
	if 'data' in data_0 and 'scale' in data_0:
	    data =  data_0['data'] * data_0['scale']
	elif  'data' in data_0:  # the most ordinary case
	    data = data_0['data']
	else:
	    raise NotImplementedError

	args = {'tvec':tvec}
	##########!!!  errorbars   !!!
	try:
	    args.update( {'tvec_err':data_0['tvec_err'], 'data_err':data_0['data_err'] } )
	except:
	    pass # missing errorbars

	if 'axis' in data_0 and any( ~ isnone(data_0['axis']) ):
	     args['axis'] = data_0['axis']   # make a list from all the axis (including tvec
	sig = Data(data, **args)

    return tvec, sig




class Shot(object):
    def __init__(self,shot_num = None):
	if shot_num is None:
	    shot_num = self._get_shot_number()
	if shot_num <= 0:
	   shot_num =  get_current_shot() + shot_num
	self.shot_num = shot_num
	self.data_config = read_config(base_path+'/'+str(shot_num)+'/', data_config)
	#self.data_config = check_data_config(self.data_config)
	self.das_config =  read_config(base_path+'/'+str(shot_num)+'/', das_config)
	self.diags = sorted(self.data_config.keys())

	try:
	    self.session = str(self['session_name'])
	    self.date = self['date']
	    self.time = self['time']
	except:
	    pass

    def __getitem__(self, name):
	"""Use dictionary like parameter passing
	param str name: Name of diagnostics / analysis / DAS to be returned
	param tuple name: Name of DAS to be returned and number of channel
	"""
	if type(name) is tuple:
	    name, channel = name
	else:
	    channel = None
	return self.get_data(name, channel)

    def get_details(self, name):
	"""
	Return basic details about das or diagnostics
	"""
	if name in self.data_config.keys() and name not in self.das_config.keys():
	    try:
		info = self.data_config[name] # is not case sensitive and remove problem with backslash
		path = base_path + '/' + str(self.shot_num) + '/'+ info['datadir'] + '/'+ info['identifier']
	    except Exception, e:
		raise NameError('Problem during loading of info '+name + " error:" + str(e))
	    info['diagn_type'] = 'data'
	elif name in self.das_config.keys():
	    info = self.das_config[name]
	    info.update( {'name':name, 'xlabel':'Time [s]', 'ylabel': 'U [V]'} )
	    path = base_path + '/' + str(self.shot_num) + '/'+ info['datapath']
	    info['diagn_type'] = 'das'

	elif name in  self._get_all_das_channels().keys():
	    info = self.das_config[ self._get_all_das_channels()[name] ]
	    info.update( {'name':name, 'xlabel':'Time [s]', 'ylabel': 'U [V]'} )
	    path = base_path + '/' + str(self.shot_num) + '/'+ info['datapath']
	    info['diagn_type'] = 'das'
	else:
	    #print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	    #print self._get_all_das_channels().keys(), name, name in self._get_all_das_channels().keys()
	    raise NameError('Missing name in database: ' + name )
	info['path'] = self.get_path(path)
	info['units'] =get_units(info['ylabel'])

	return info

    def _get_all_das_channels(self):
	max_channels = 100
	channels = OrderedDict()
	for das_name in self.das_config.keys():
	    das = self.das_config[das_name]
	    for i in range(max_channels):
		key = self.channel_name(das_name, i)
		if key is not None:
		    channels[key] = das_name
	return channels



    def get_data(self, name, channel = None, testRun  = False,
		return_channel = False, testScalar = False, return_path = False, return_raw_data = False):
	"""
	!!! TODO: predelat aby to bralo return_value = "data"/"path"/"existence",.... !!!!!!!!!!
	Main function that load/prepare/return the requested data
	param str name: Name of diagnostics / analysis / DAS to be returned
	param list channel: NUmber of channel in DAS
	param bool testRun: use only dry run to test existance of the data
    	param bool return_channel: do not return data but only location (name + channel) of the requested data
    	param bool return_raw_data: return unprocessed data non converted to Data class (speed up )
    	"""
	name =  self._fix_key(name)  # problems with backslash

	# firstly try to load data from SQL if it fails, try to dig deeper and slower  !!
	#try:  # !! je to desne pomale .. .
	    #assert socket.gethostname() != "buon.fjfi.cvut.cz"  # skip if host name == buon !!
	    #data =  load_value(name, self.shot_num)
	    #if data is not None:
		#return data
	#except:
	    #pass

	if name not in self.data_config:
	    if name == "any" and type(channel) is str:
		for key in self.das_config.keys():
		    if channel.lower() in self.das_config[key]:
			break
		name  = key
	    all_channels = self._get_all_das_channels()
	    if name in all_channels:
		channel = name
		name = all_channels[channel]
	    if name not in self.data_config and name not in self.das_config:
		raise NameError( "Missing name " + name + " in database ")
	    if type(channel) is str:   # expect that channel is always number => named channels are used only in DAS
		channel_num = int_(self.das_config[name][self._fix_key(channel)])
	    elif type(channel) is int or type(channel) is ndarray or type(channel) is list:  # number
		channel_num = int_(channel)
		channel = name + " " + str(channel)

	info = self.get_details(name)
	path = info['path']

	if return_channel:
	    return name, channel_num

	if channel:
	    path = path.format(channel_num)  # for papouch data

	if testScalar:   # check if the number is scalar
	  try:
	    return type(loadconst(path)) is float  # it can be also string !!
	  except:
	    return False

	if return_path :
	    return path

	if testRun:
	    return find_data(path)    # proc to nefunguje jako return path ??
	    #return path
	#if not :
	def load_array():
	    tvec, data = load_adv(path)
	    if type(data) is Data:
		data.set_details( ** self.get_metadata(name, info) )
	    if channel and ndim(data) == 2:
		data = data[:,channel_num]
		data.info = channel
	    try:
		return double(tvec), double(squeeze(data))
	    except:
		return data if tvec is None else [tvec, data]

	if info['diagn_type'] == "das":
	    return load_array()

	elif 'type' not in info:
	    raise NameError("Missing attribute 'type' in data_configuration.cfg for key: "+ name)
	elif info['type'] == 'list':
	    tags = ""
	    dirs = os.listdir(info['path'])
	    for d in dirs:
		if d != "index.php":
		    tags += "'"+d+"',"
	    if len(tags) > 0:
		return tags[:-1]
	    else:
		return None

	elif info['type'] in ['array', 'other']:
	    return load_array()

	else:
	    #if return_raw_data:
		#return loadconst(path)
	    #else:
	    return Data(loadconst(path, info['type'] == "scalar"), name = name, info = info['name'], ax_labels = info['ylabel'] )
	    #return data

    def exist(self, name):
	"""
	Check existence of diagn called "name"
	"""
	valid = self._is_valid_name(name)
	if not valid: return False

	try:
	    return self.get_data(name, testRun = True)
	except Exception, e:
	    return False

    def get_metadata(self, name, info):
	metadata = dict( name = name, info = info['name'])
	xlabel = info['xlabel'] if 'xlabel' in info else "???"
	ylabel = info['ylabel'] if 'ylabel' in info else "???"
	metadata.update( {'ax_labels':  [ xlabel, ylabel ] } )
	try:   # it is possible that stat / end does not exist
	    metadata.update( { 'plasma_start': self.get_data('plasma_start'),   'plasma_end': self.get_data('plasma_end') })
	except:
	    pass
	return metadata




    def get_nice(self, diagn, format = None, norm = 1):
	"""
	Try to load and return a float parameter in a nice way. Default is returning float but common formating can be applied to get string or  renormalization of the number. In case of failure returns N/A
	:format: None - return raw data, "auto" - use clever formating, other python formats ...
	"""

	try:
	    diagn =  self.get_data(diagn, return_raw_data = True)
	    if not isscalar(diagn) and type(diagn) is not Data:
		return str(diagn)
	    elif (type(diagn) is Data and diagn.type is str) or type(diagn) is str:
		return str(diagn)
	    diagn *= norm
	    if format is None:
		return diagn
	    elif format == "auto":
		if int(diagn) == diagn and abs(diagn) < 1e6:
		    return "%i" % diagn
		return "%.3g" % diagn
	    else:
		return format % (diagn)
	except:
	    #raise
	    return 'N/A'

    def get_path(self, path):
	"""
	If possible return real path, else return nonexisting path string
	find_data returns path with correct file ending
	param str path : possible path to data,
	"""
	path_tmp = find_data(path)
	if path_tmp:
	    return path_tmp
	else:
	    return path   # if path do not exists, return path from config



#######################################################################################################################x
    def get_pygolem_list(self, custom_keys = []):
	"""
	Creaty formated HTML list of availible signals (analysis/diagnostics/DAS) and sign missing signal (gray).
	param list custom_keys: List of signals that should be in output list. If empty return all
	"""

	table = []
	out = cStringIO.StringIO()
	all_keys = sorted(self.data_config.keys())
	if len(custom_keys) > 0:
	    if type(custom_keys) is str:
		custom_keys = [custom_keys]
	    for i in range(len(custom_keys)):
		custom_keys[i] = self._fix_key(custom_keys[i])

	    keys = array(all_keys)[in1d(all_keys, custom_keys)]
	    missing_keys = array(custom_keys)[~in1d(custom_keys, all_keys)]
	    if len(missing_keys) > 0:
	      print >> out, "<h3><font color='red'>Missing keys: " + str(missing_keys) + " </font></h3>"
	else:
	    keys =  array(all_keys)  # use all keys if there are no custom

	base_path = "/utils/data/"+str(self.shot_num)+'/'

	try:
	    for key in keys:
		details = self.get_details(key)
		if details['path']:
		    path = re.sub('/srv/www/svoboda/golem','', details['path'])
		else:
		    path = ""
		line = '<a class="diagn_name" id="'+key+'">'
		line += ("<font color='#C0C0C0'>"+key+" </font> ") if not self.exist(key) else key
		line += '</a>'

		if details['type'] == "scalar" and self.exist(key):
		    line += " (<a href='"+base_path+key+"'>"+self.get_nice(key, "auto")+"</a>&thinsp;"+details['units']+")"
		elif details['type'] == "scalar":
		    line += " (<a href='"+base_path+key+"'>txt</a>)"
		elif details['type'] == "array":
		    line += "(<a href='"+base_path+key+"'>txt</a>,<a href='"+base_path+key+".xls'>xls</a>," + \
		    "<a href='/utils/golplot?action=Plot+All&shotno_0="+str(self.shot_num)+"&diagn_0="+key+"'>img</a>," + \
		    "<a href='"+"/"+default_path+"/"+str(self.shot_num)+'/'+"About.php#pygolem_lite'>...</a>)"
		#"<a href='"+base_path+key+".png'>png</a>,"  + \

		else:
		    line += " (<a href='"+base_path+key+"'>txt</a>)"
		line += ("<a href='"+path + "'>&darr; </a> " if path else "")

		line = [line]+[ fix_str(details[id], True) for id in ['identifier', 'ylabel', 'name'] if id in details]


		table.append(line)
	except Exception, e:
	    print >> out, "<h4>Diagnostics list failed for key: " + key + " <br> Error:" + str(e) +  "</h4>"
	    raise


	print >> out, "<h3> Accessible data: [<a href='/"+default_path+"/"+str(self.shot_num)+"/data_configuration.cfg'>data_configuration.cfg</a>] \
	[<a href='/"+default_path+"/"+str(self.shot_num)+"/basicdiagn/config.py'>config.py</a>]  -  <font size='3'> (<a href='http://golem.fjfi.cvut.cz/wiki/SW/pygolem'>more details</a>, <a href='/"+default_path+"/"+str(self.shot_num)+"/Data.php#all_data'>all data</a>) </font> \
	</h3>\n <table width='100%'>\n<tr><td><h4>Identifier</h4></td>     <td><h4>File name</h4></td>  <td><h4>Units</h4></td>   <td><h4>Description</h4></td></tr>\n<tr>"
	self._pprint_table(out, (table))
	print >> out, "</tr>\n</table>"

	return  out.getvalue()


    def get_pygolem_das(self, das_names):
	"""
	Create formated HTML list of availible signals in one DAS
	param str das_name: Name of DAS to be processed
	"""

	base_path = "/utils/data/"+str(self.shot_num)+'/'
	max_channels = 100
	table = []
	out = cStringIO.StringIO()

	if type(das_names) is str:
	    das_names = [das_names]
	for i in range(len(das_names)):
	    das_names[i] = self._fix_key(das_names[i])

	def tab_append(shown_name,path, name, key):
	    table.append( [ shown_name + " (<a href="+path+">txt</a>,"\
		"<a href="+path+".xls>xls</a>,"  \
		"<a href='/utils/golplot?action=Plot+All&shotno_0="+str(self.shot_num)+"&diagn_0="+key+"'>img</a>,"  \
		"<a href='"+"/"+default_path+"/"+str(self.shot_num)+'/'+"About.php#pygolem_lite'>...</a>)\n"  , name ])

	for das_name in das_names:
	  try:
	    das = self.das_config[das_name]
	    tab_append('<b>'+das_name+'</b>',base_path+das_name, das['name']+ " all channels", das_name)
	    for i in range(max_channels):
		key = self.channel_name(das_name, i)
		if key is not None:
		  tab_append( ('&nbsp;'*8)+key,base_path+key, das[key], key)

	    if len(das_names) > 1:
		table.append(['<hr/>']*2)

	  except Exception, e:
	    return "DAS Failed !!!  " + str(e) + "<br/> channel " + str(key) if "key" in locals() else "" + " <br/>"

	print >> out, "<h3> DAS - channel setting  [<a href='/"+default_path+"/"+str(self.shot_num)+"/das_configuration.cfg'>das_configuration.cfg</a>] \
	<font size='3'> (<a href='http://golem.fjfi.cvut.cz/wiki/SW/pygolem'>more details</a>) </font>  </h3> \
	<table width='80%'>\n<tr><td><h4 >Identifier</h4></td>     <td><h4 >\tChannel</h4></td>  </tr>\n<tr>"
	self._pprint_table(out, (table))
	print >> out, "</tr>\n</table>"
	return  out.getvalue()


    def channel_name(self, das_name, channel):
	"""  Returns name of ith channel from das_config """
	das = self.das_config[self._fix_key(das_name)]
	for key in das.keys():
	    if key not in  [ "datapath", 'xlabel', 'ylabel', 'name', 'status']:  # list of ignored names
		if das[key] != str(channel):
		  continue   # skip of number of
		else:
		  return key
	return None


    def _fix_key(self,key):
	""" Ugly but  unavoidable ?? way how to fix 'spectrometr:temperature' key to 'spectrometr:temperature' key
	"""
	key = key.lower()
	#key = key.__repr__()
	#key = re.sub('\'', '', key)
	#key = re.sub('\"', '', key)
	#key = re.sub(r'\\\\', r'\\', key)
	return key

    def _get_shot_number(self):
	""" Get number of  shot where is pygolem_lite started
	"""
	#print re.sub('(.+/shots/)([0-9]+)/(.+)', r'\2',  os.getcwd())
	#print os.getcwd()
	#return int(re.sub('(.+/shots/)([0-9]+)/(.+)', r'\2',  os.getcwd()+'/'))
	path =  os.getcwd()
	while not os.path.exists('ShotNo') and os.getcwd() != "/" :
	    os.chdir("..")
	shot =  int(loadconst('ShotNo'))
	os.chdir(path)
	return shot

    def _is_valid_name(self, name):
      """ Return 1 of name is diagn and 2 if it is DAS, otherwise zero
      """

      if type(name) is not list:
	  name = [name]
      for i in range(len(name)):
	  name[i] = self._fix_key(name[i])
      out = zeros(len(name), dtype=int )
      out += in1d(name, self.data_config.keys())*1  # in data config
      out += in1d(name, self.das_config.keys())*2  # in das config
      for i in range(len(name)):
	 for das in  self.das_config.itervalues():
	    out[i] +=  (name[i] in das)*3   # is das channel name
      return out


    def _pprint_table(self, out, table):
	"""Prints out a table of data, padded for alignment
	param out: Output stream (file-like object)
	param list table: The table to print. A list of lists.
	Each row must have the same number of columns. """

	for row in table:
	    for i in range( len(row)):
		print >> out,"<td>", str(row[i]),"</td>"
	    print >> out,'</tr><tr>'

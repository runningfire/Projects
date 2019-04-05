#!/usr/bin/python2

"""Python API for the GOLEM Tokamak discharge database

Abstract
--------
This simple Python API aims to provide a simple and easy to understand access to the discharge database of the GOLEM Tokamak.
The scipy, numpy and matplotlib Python libraries are used for data analysis and plotting.

Design
------
The discharge database consists of a hierarchy of directories containing data. This API mimics this design by a hierarchy of classes.

- Each class has child elements which are accessed by the '[ .. ]' (defined as :func:`__getitem__`)  operator.
- Each class provides an iterator to loop over child elements

Hiearachy order overview, the class at the top is listed first:

:class:`Task`
    represents the task, e.g. Specials/11HTS/SundaySession/
:class:`Session`
    represents the session within a task, e.g. Specials/11HTS/SundaySession/041211_1621/
:class:`Shot`
    represents a discharge
:class:`Data`
    represents discharge data in the form of a NumPy array (it's a wrapper around the ndarray class), e.g. Uloop data

For further information about how to initialize the classes see the constructor documentation for each class.

Backends
--------
All the classes mentioned above are based on the universal :class:`Dir` class which provides a centralized I/O operations class.

There are several possible backends for the :class:`Dir` based classes to use.
The backend is set by the contents of the *backend* string variable in the namespace of the module.
By default the *backend* variable contains a string 'filesystem'.

'filesystem' : obtain data from a local or locally mounted filesystem
    this is the most versatile and fastest backend
    the discharge database can be mounted through the sshfs filesystem with -o transform_symlinks
'http' : obtain data through HTTP requests
    data is fetched from the discharge web server
    this backend doesn't support several class methods, usually those that list the contents of the directory as this is not possible over HTTP
'http-cache' : obtain data through HTTP requests and save on local filesystem
    this backend functions (and has the same limitations) as the 'http' backend, but it saves the downloaded files locally,
    so repeatedly requested data is obtained with the speed of the 'filesystem' backend

The directory for the 'filesystem' and 'http-cache' backend _must_ be specified using the :func:`change_data_root` function, otherwise it defaults to the current working directory.

Examples
--------
::

    from matplotlib.pyplot import savefig   # to save the figure
    two = Shot(6897)['NIturbo'][2]          # return data from the second channel of the NIturbo DAS recorder durong discharge no. 6897
    hts_sunday = Session('Specials/11HTS/SundaySession/041211_1621/')
    for shot in hts_sunday:                 #loops over all shots in that session
        shot['Uloop'].plot()                # plot the loop voltage data, for data in the 'basicdiagn' directory only the data identifier can be specified -- that is a shortcut
        shot['Papouch_St'][5].plot()        #plot the fifth channel of Papouch_St DAS data
        savefig('comparison_' + str(shot.number) +'.pdf') #save the figure with a name corresponidng to the shot number

"""


from matplotlib.pyplot import plot, xlabel, ylabel, savefig, axhline, legend, title
from matplotlib.pyplot import Figure as Fig # to ensure we dont override it
from numpy import loadtxt, ndarray, amin, amax, mean
from glob import glob
from time import mktime, strptime
from urllib2 import urlopen, HTTPError # for fallback to HTTP file transfer
from locale import setlocale, LC_TIME, Error #for correct timezone resolution
from StringIO import StringIO #for wrapping of urlopen
import re, os #for contents_regexp()
from shutil import copyfileobj #for http-cache backend
import ConfigParser #for dynamically updating the data*_types dictionaries

################################################################
####                GLOBAL VARIABLES                        ####
################################################################

config_file = 'data_configuration.cfg' #file to sue with ConfigParser

################ DATA ACCESS DICTIONARY MAPPING  ################

def _read_config(fileo):
    """Read data configuration from the fileobject and return it as a dictionary"""
    config = ConfigParser.RawConfigParser()
    data_types = dict()
    config.readfp(fileo)
    for data_type in config.sections():
        data_types[data_type] = dict(config.items(data_type))
    return data_types

#this global dictionary contains definitions in the form
#    'key' : { key : values, ...}
# Possible keys
# -------------
# key : str
#     key to be used in :func:`Shot.__getitem__`
# xlabel : str
# ylabel : str
# name : str
#     a string to be used by :func:`matplotlib.pyplot.title` and as data label in graphs
#     optionally contains a formatiing string '{}' which is expanded to a  data identifier (e.g. channel number) by :func:`str.format`
# datadir : str
#     key in this dictionary describing a dictionary containing a 'path_pattern' entry
#     should contian underscore, not spaces
# identifier : str
#     identifier to be used in path_pattern in the entry describing a datadir
#     this identifier is expanded into the path_pattern string using :func:`str.format`
#     basically it is substituted with '{...}' in path_pattern
# path_pattern : str
#     path relative to :class:`Shot` directory containing a formatting string (e.g. {:e}) which will be expanded to the requsted file using :func:`str.format`
#     the string template formatting substring must ALWAYS contain the expected type of argument to :func:`str.format`, e.g. {:s} for str or {:d} for int
# loading_func : function
#     function to be used to load the data
#     must accept a file-like object as the first argument and then the unpacked parameters dictionary
#     must return a ndarray
# parameters : str
#     a repr() of a dictionary to be unpacked into the loading_func after the file-like parameter

data_types = _read_config(open(os.path.dirname(__file__) + '/' + config_file, 'r'))

################ BACKEND DEFINITIONS ################

def _filesystem_open_file(path): #open everything read-only, we don't want to mess up data
    """Open file with path relative to base_path read-only"""
    return open(backend_types['filesystem'][0] + path, 'r')

def _http_open_file(path):
    """Download the file from the server specified by a path relative to the base_path (server root)

    Wrapped in a StringIO object to provide other file-like capabilities
    """
    try: #even HTTP may fail, but translate to IOError for that
        f = StringIO(urlopen(backend_types['http'][0] + path).read()) #wrap in StringIO to have file-like capabilities
        # root of web dir is defined in backend_types
        f.name = path #store it to provide a common interface
        return f
    except HTTPError:
        raise IOError(backend_types['http'][0] + path + " does not appear to be accessible on the server")


def _http_cache_open_file(path):
    """Check if file is on the disk and if not, create the directory structure and download and store it
    """
    full_path = backend_types['http-cache'][0] + path
    if not os.path.exists(full_path): #must download
        downloaded = _http_open_file(path)
        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name) #prepare the cache dir
        cache = open(full_path, 'w')
        copyfileobj(downloaded, cache) #store into cache
        cache.close() #run back to start of file to be able to read in array
    return open(full_path, 'r')


def _http_cache_npy_open_file(self, path):
    """Open the binary file or download and store in binary format and return the array"""
    full_path = backend_types['http-cache-npy'] + path
    if path.endswith('.npy'): #want a bin file to write to
        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name) #prepare the cache dir
        return open(full_path, 'w')
    else: #want a file to read from
        full_path += '.npy'
        if not os.path.exists(full_path): #must download
            return _http_open_file(path)
        else:
            return open(full_path, 'r')

# the backend_types dictionary defines the discharge database root for each backend
backend_types={'filesystem' : ['./', _filesystem_open_file] #by default the current working directory, use chdir() to change it easily
              ,'http' : ["http://golem.fjfi.cvut.cz/", _http_open_file] #the root on the web server
              ,'http-cache' : ['./', _http_cache_open_file]
              ,'http-cache-npy' : ['./', _http_cache_npy_open_file]
              } # TODO , 'ssh', 'ftp']
backend='http' #use the filesystem method by default


################################################################
####                    GLOBAL FUNCTIONS                    ####
################################################################

def normalize_str(string,start,end,endwith=True, startwith=False):
    """normalize_str(sring,start,end,[endwith[, startwith]]) -> normalized_string

    remove string start from string, but add string end to it if not present at the end
    also remove newline characters
    if endwith is True, stringe must end  with end (default)
    if endwith if False, string must _not_ end with end
    the same goes for startwith (default is False)
    """
    if startwith and not string.startswith(start): #the string is supposed to start with it
        string = start + string
    if not startwith and string.startswith(start):
        string = string.lstrip(start) #so remove it
    if endwith and not  string.endswith(end): #the string is supposed to end with it
        string += end #so add it if missing
    if not endwith and string.endswith(end):
        string = string.rstrip(end)
    return string

def change_data_root(directory):
    """change_data_root(directory)

    Change the root directory entry of the database.

    Parameters
    ----------
    directory : str
        path to the directory, absolute or relative to CWD (make sure you know the difference)

    for the filesystem backend: change the directory entry from where data si obtained
    for the http-cache(-npy) backend: change the directory in which the obtained data will be saved
    """
    if  backend == 'http': #cannot not work
        raise ValueError('http backend does not support change_data_root()')
    else:
        backend_types[backend][0] = normalize_str(directory, '', '/', True, True)

################################################################
####                 DATA ACCESS CLASSES                    ####
################################################################

class Dir:
    """Low-level class for easy access to directories and files

    The discharge database is essentially a hierarchy of directories containig files
    Therefore, this class provides a centralized IO class  for file opening, reading, data loading, etc.
    Various backends can be used for the IO tasks, e.g. filesystem, remote network filesystem (e.g. sshfs, fish) or HTTP.
    Nearly all other classes are derived from this class, because they are also directory based

    Attributes
    ----------
    name : str
        the base directory,
        specified relative to the root directory of the discharge database hierarchy
        inherited by derived classes

    Methods
    -------
    Most methods use a either file name as a parameter (a string _not_ ending with '/'),
    or a directory path (a string ending with '/', this is taken care of by normalize_str() )

    """
    def set_dir(self, *directories):
        """set_dir(*directories) -> set the base directory of the Dir object

        Each directory name in the *directories sequence is checked for slashes, it should end with a slash, but not start with one
        normalize_str() takes care of that
        after being checked,they are concatenated into the Dir.name

        Note
        ----
        This functions also initializes the cache dictionary for Dir based classs
        """
        self.name="" #initialize an empty string, will add stuff to it
        for dirname in directories: #for each directory
            self.name += normalize_str(dirname, '/', '/') #normalize the directory name
        self.cache={} #initialize cache for Dir based classes

    def __init__(self,directory):
        """construct a new Dir class with the specified directory"""
        self.set_dir(directory)

    def open_file(self, path):
        """open_file(path) -> file-like object

        the path is relative to the Dir.name base directory

        the file-like object is read-only and provides common interfaces like read(), readline(),
        but may not provide methods like seek()
        """
        loading_func = backend_types[backend][1]
        path =  self.name + normalize_str(path, '/', '/',False) #make sure the path does not start with a slash
        return loading_func(path)

    def cat_readline(self,path):
        """cat_readline(path) -> content_string

        concatenate the file  of file name = path in directory Dir.name, containing some string with info

        use mainly for small file containing some info string
        closes file after reading
        """
        f=self.open_file(path)# cannot use with open(path), because urlink does not support that
        content=f.readline()
        f.close()
        return content #return the raw string

    def cat_num(self,path):
        """cat_num(path) -> int

        return the contents of a one line file in the directory as an integer
        """
        return int(self.cat_readline(path))

    def cat_str(self,path):
        """cat_str(path) -> string

        return the contents of a one line file as a string
        """
        return self.cat_readline(path).replace('\n','') #strip the string of such cruft

    def listdir(self, path=''):
        """listdir([path]) -> dir_contents_list

        Return a list of directory contents, by defualt the Dir-based object's directory.
        Use the path relative to the current backend root

        Parameters
        ----------
        path : str
            optionally return a list of the provided subdirectory

        Note
        ----
        This is not supported by any of the http backends
        """
        if backend != 'filesystem':
            raise RuntimeError("this action is not supported by the " + backend + " backend")
        else:
            return os.listdir(backend_types[backend] + self.name + path)

    def contents_regexp(self,pattern):
        """contents_regexp(pattern) -> list_of_matches

        Returns a list of the directory contents matching a regexp pattern.
        for http-like backends it parses the index.html(or whatever the server send when requesting the directory) webpage for the *pattern*.
        """
        if backend == 'filesystem': #filesytem backend, so 'os' should work
            return [ content for content in self.listdir() if re.match(pattern, content) ] #TODO: do we always want to match from start of string with re.match ?
        else:
            index = self.open_file('') #should download index.html and wrap it in StringIO
            return [ match.group()[1:-3] for match in re.finditer('>' + pattern + '</a', index.read()) ]  #list comprehension: return al the matching patterns

    def get_elements_list(self):
        """return a list of all files in directory"""
        names=self.listdir()
        for fname in names:
            if not os.path.isfile(backend_types[backend] + self.name + name):
                names.remove(name)
        return names

    load_element=open_file #bound method alias

    def get_element(self,name):
        """get_element(name) -> element

        Return the lower level element (in the hierarchy) based on his name
        from cache and/or load it into cache if not present.
        Loads element through the method load_element(), each class defines it's own.
        """
        if not self.cache.has_key(name): #not i cache, load
            self.cache[name]=self.load_element(name) #load the element
        return self.cache[name]

    def get_elements(self,names=None):
        """get_elements([names]) -> list of elements

        Return a list of lower level elements (in the hierarchy).
        Optionally, return only the elements specified in the list 'names'
        """
        if names is None: #return all
            names=self.get_elements_list()
        return [ self.get_element(name) for name in names]

    def __iter__(self):
        """Return an Iterator object over lower hierarchy elements of this class"""
        return iter(self.get_elements())
    def __str__(self):
        """Return the base name of the containing directory"""
        return self.name
    def __del__(self):
        """Delete the lower level elements cache"""
        del self.cache

    __getitem__=get_element #alias, bound method, gets inherited

class Data(ndarray):
    """Discharge data container

    Gives access to data analysis and plotting tools
    This class is a subclass of :class:`numpy.ndarray`
    """

    def __new__(cls, source, xlabel=None, ylabel=None, name=None, columns=None):
        """Wrap the source ndarray in a new Data instance

        Only the source parameter is mandatory,

        Parameters
        ----------
        source : numpy ndaray object
            wrap around this array
        xlabel : str, optional
            label for the X-axis in graphs
        ylabel : str, optional
            label for the Y-axis in graphs
        name : str, optional
            description of the data set to be used in plot title and as label in legend
        columns : tuple of ints, optional
            defines the columns to be used, first column is no. 0
            the first (no. 0) column should be time
            the second column should be the primary data column
        """
        if not columns is None:
            if ndim(source) > 1:
                source = source[:,columns]
        wrapper = source.view(cls) # cast ndarry to our wrapper class
        wrapper.xlabel, wrapper.ylabel, wrapper.name = xlabel, ylabel, name
        return wrapper

    def __array_finalize__(self, obj):
        # based on http://docs.scipy.org/doc/numpy/user/basics.subclassing.html
        if obj is None: return
        self.xlabel = getattr(obj, 'xlabel', None)
        self.ylabel = getattr(obj, 'ylabel', None)
        self.name = getattr(obj, 'name', None)

    def time_shift(self, shift=0, column=0):
        """Shift the data in the column representing time (specified by column) by shift

        Parameters
        ----------
        shift : float
            add this value (0 by default) to the specified column
            mind the units!!!
        column : int
            index of the column representing time
            defaults to 0 -> first column
        """
        self[:,column] += tshift

    def calibrate(self, quotient=1, offset=0, column=1):
        """Calibrate the column(s) representing data (specified by column) by the specified quotient and offset

        Parameters
        ----------
        quotient : float
            multiply by this value (1 by default) the specified column
        offset : float
            add this value (0 by default) to the specified column
        column : int or tuple of int
            index of the column(s) representing data
            defaults to 1 -> second column
        """
        self[:,column] *= quotient
        self[:,column] += offset

    def plot(self, x_column=0, y_column=1, name=None, **kwargs):
        """plot([x_column [, y_column[, name[, **kwargs]]]]) - > Add the data sample into the figure

        Parameters
        ----------
        x_column : int
            the column in the data ndarray to plot on the x axis
        y_column : int
            column in ndarray data to plot on y axis
        name : str
            optional name to override the Data.name attribute
        **kwargs : keyword arguments to be passed to the standard plot() command
            this method accepts **kwargs as a standard :func:`matplotlib.pyplot.plot` function
                """
        xlabel(self.xlabel)
        ylabel(self.ylabel)
        if name is None:
            title(self.name)
        else:
            title(name)
        #axhline(color='k') #draw a blak horizontal line at y=0
        plot(self[:,x_column], self[:,y_column], label=self.name, **kwargs)

class Task(Dir):
    """Task container class

    Based on the Dir class, used for containing directories ROOT/tasks/...
    where sessions reside, therefore, it gives access to lower elemetns = Session objects
    """
    def __init__(self, task_name):
        """create a new Task instance with the specified name

        Parameters
        ----------
        task_name : str
            name of the task, e.g. Specials/11HTS/SundaySession/
        """
        self.set_dir('tasks/', task_name)

    def get_elements_list(self):
        """return a list of sessions in this task"""
        if backend == 'filesytem':
            return self.contents_regexp('\\d{6}_\\d{4}') #return all dirs matching the pattern %d%m%y_%H%M
        else: #http-like
            return self.contents_regexp('\\d{6}_\\d{4}\/') #return all dirs matching the pattern %d%m%y_%H%M/

    def load_element(self,date_time):
        """Return a new Session element based on the date_time as returned by get_elements_list()"""
        return Session(normalize_str(self.name, 'tasks/','/')+date_time) #give the self.name without 'tasks/', to make it more convenient for input


class Session(Dir):
    """Session container class

    Based on the Dir class, subdirectories are transformed into Shot objects
    """
    def get_init_time(self):
        """return the time of session start as standard UNIX time"""
        try: #first won't work on Win
            setlocale(LC_TIME, ("en_US","UTF-8")) #needed for %Z to work
        except Error: #Win needs something different
            setlocale(LC_TIME, "us")
        return mktime(strptime(self.cat_str("Komora/StartTime"), "%a %b %d %H:%M:%S %Z %Y"))

    def __init__(self, session_dir):
        """construct the Session instance

        Parameters
        ----------
        session_dir : str
            the name of the task and the session date and time,
            e.g. Specials/11HTS/SundaySession/041211_1621/
            there is no need to prepend it with 'task/',
            but the session date and time is mandatory
        """
        self.set_dir('tasks/', session_dir) #set the session dir
        self.init_time=self.get_init_time()

    def get_elements_list(self):
        """return a list of shot numbers in the session"""
        if backend == 'filesystem':
            return [ int(self.cat_str(sdir+"/ShotNo")) for sdir in self.contents_regexp('\\d{6}') ]
        else: #http-like
            return [ int(num) for num in self.contents_regexp('\\d{4}') ]

    def load_element(self,num):
        """load_element(shot_number) -> Shot object

        Return a Shot instance based on the discharge number (can be in string form too)
        """
        return Shot(int(num), session_start=self.init_time)

class Shot(Dir):
    """Discharge container class

    used for plotting and accessing discharge data
    """

    def get_plasma(self):
        """get_plasma() -> bool_plasma

        Return True if plasma was generated
        """
        try: #in old shots, the file Plasma was not created if no Plasma generated
            if (self.cat_str("basicdiagn/Plasma") == '1'):#check if plasma was generated during the discharge
                return True
            else:
                return False
        except IOError: #file does not exist, in older shots that could mean it was not generated
            return False

    def __init__(self,shot_num, shot_dir=None, session_start=None):
       """create a new Shot instance

       Parameters
       ----------
       shot_num : int
           discharge number
       shot_dir : string
           directory of the discharge
           can be passed relative to session
           otherwise it will be created based on the shot number
       session_start : int
           std. UNIX time in  seconds, should be passed from respective Session
           otherwise it will be retrieved automagicaly
       """
       self.no_errors=True #well, so far
       try: #catch non-existent files, as some discharges may have failed
           self.number = shot_num
           if shot_dir is None:
               self.set_dir('shots/'+str(shot_num)+'/')
           else:
               self.set_dir(shot_dir)
           self._session_start=session_start
           self.plasma = self.get_plasma()
       except IOError: #something is wrong
           self.no_errors=False
       self.read_config()

    ################        CONFIG PARSING          ################

    def make_config(self, fileo):
        """Write data configuration in the data_types dictionary to the specified fileobject"""
        config = ConfigParser.SafeConfigParser() #new class instance
        for data_type, configuration in self.data_types.iteritems():
            config.add_section(data_type)
            for option, value in configuration.iteritems():
                config.set(data_type, option, value)
        config.write(fileo)

    def read_config(self, filename=config_file):
        """Read data configuration from the filename relative to the Shot directory into the Shot specific data_types dictionary or fall back to the default global dictionary"""
        try:
            self.data_types = _read_config(self.open_file(filename))
        except IOError:
            self.data_types = data_types #use the global dict as fall back

    def get_init_time(self):
        try: #init_time may not be defined
            return self.init_time
        except NameError: #init_time undefined
            if self._session_start is None:
                self.init_time=Session(self.cat_str('SessionNameDate')).get_init_time()
            else: #session_time was passed on
                self.init_time = _session_start
            self.init_time +=self.cat_num("Aktual_Time")+10
            #time since session start to trigger start + 10 seconds for trigger safety
            return self.init_time
    def get_charging_limit(self, capacitor_name):
        """get_charging_limit(capacitor_name) -> charging limit

        Return the charging limit for the specified capacitor

        Parameters
        ----------
        capacitor_name : str
            name of the capacitor, lowercase, derived from the name of the respective generated field
            possible values : 'b' - toroidal magnetic field
                              'cd' - current drive electric field
                              'bd' - breakdown electric field
                              'st' - vertical stabilizing magnetic field
        Note
        ----
        These are the values set before discharge, the capacitors may have been
        charged to a slightly different voltage, but this is noticable only for low voltages (<100 V).
        """
        if capacitor_name not in ['b', 'cd', 'bd', 'st']:
            raise ValueError(capacitor_name + " is not a valid identifier. See the function docstring for possible values")
        else:
            return self.cat_num('nabijeni/U' + capacitor_name + '_limit')

    def get_time_delay(self, capacitor_name):
        """get_time_delay(capacitor_name) -> time delay

        Return the time deleay between the discharge of the toroidal magnetic fied capacitors and the specified capacitor in miliseconds.

        capacitor_name : str
            name of capacitor, lowercase, derived from the name of the respective generated field
            possible values : 'cd' - current drive electric field
                              'bd' - breakdown electric field
                              'st' - vertical stabilizing magnetic field
        """
        if capacitor_name not in ['cd', 'bd', 'st']:
            raise ValueError(capacitor_name + " is not a valid identifier. See the function docstring for possible values")
        else:
            return self.cat_num('T' + capacitor_name + '_aktual')

    def __bool__(self):
        """Return True if plasma was generated AND no errors occurred"""
        return self.plasma and self.no_errors

    def __str__(self):
        """Return the shot number as a string"""
        return str(self.number)

    def load_element(self, keys):
        """load_element(keys) -> ndarray

        Return a Data object based on the provided keys

        Parameters
        ----------
        keys : tuple of str or int
            name and identifier passed by :func:`get_element`
        """
        name, identifier = keys
        data_dict = self.data_types[name]
        if identifier is None: #want unique data, so need datadir_dict too
            datadir_dict = self.data_types[data_dict['datadir']]
            identifier = data_dict['identifier']
        else: #want some datadir file specified by identifier
            datadir_dict = data_dict
        ################ DATA TYPE SETTING ################
            #datadir specific
        path = datadir_dict['path_pattern'].format(identifier)
        loading_func = datadir_dict.get('loading_func', loadtxt)
        parameters = eval(datadir_dict.get('parameters', "{'delimiter': ' '}"))
            #data specific
        name = data_dict.get('name').format(identifier)
        ylabel = data_dict.get('ylabel') #dict.get() returns None if key not present
        xlabel = data_dict.get('xlabel')
        ################ DATA LOADING ################
        raw_file = self.open_file(path)
        if raw_file.name.endswith('.npy'): #want to read from binary format
            return Data(load(raw_file), xlabel, ylabel, name)
        else:
            data_array = loading_func(self.open_file(path), **parameters)
            if backend == 'http-cache-npy': #don't forget to save the file in bin form
                save(self.open_file(path + '.npy'), data_array)
            return Data(data_array, xlabel, ylabel, name)

    def __getitem__(self, name, identifier=None):
        """Shot[name] or Shot[name, identifier] -> ndarray

        Return a ndarray object representing the requested data.

        Parameters
        ----------
        name : str
            a valid key in the data_types dictionary
        identifier : str or int, optional
            identify a file within a data directory specified by name, based on the path_pattern string template in the data_types dictionary (for keys that provide it)
            the path_pattern string template contains a {...} substring specifying the expected type
            for reference see http://docs.python.org/library/string.html#format-string-syntax
        """
        if isinstance(name, tuple): #called with [...] notation so it contains the identifier
            return self.get_element(name)
        else:
            return self.get_element((name, identifier))

    def calculate_during_plasma(self, func, name, identifier=None, t_column=0, v_column=1):
        """Shot.calculate_during_plasma(function, name[, identifier[, t_column[, v_column]]]])

        Obtain a Data instance returned by :func:`Shot.__getitem__` using the name (and identifier) parameter(s)
        and pass a slice of the column specified by v_column representing the data measured during plasma lifespan (by using the column specified by t_column as time)
        to the function and return the result of the function

        Parameters
        ----------
        name and identifier parameters are the same like for :func:`Shot.__getitem__`
        func : function
            any function that accepts a ndarray(-like) object as first argument and returns something
            the dimension of the passed ndarray slice is given by t_column
        t_column : int
            index of column in Data instance representing time
        v_column : int or tuple of int
            index of column in Data instance representing values
        """
        data = self.__getitem__(name,identifier)
        time = data[:,t_column]
        return function(data[(time >= self.__getitem__('PlasmaStart')) & (time <= self.__getitem__('PlasmaEnd')), v_column])


    def calculate_mean(self, name, identifier=None, t_column=0, v_column=1):
        """Shot.calculate_mean(name[, identifier[, t_column[, v_column]]]]) -> float

        Return the mean of the Data specified by the name (and identifier) parameter(s)during plasma lifespan

        parameters are the same as for :func:`Shot.calculate_during_plasma`
        """
        return self.calculate_during_plasma(mean, name, identifier, t_column, v_column)

    def calculate_max(self, name, identifier=None, t_column=0, v_column=1):
        """Shot.calculate_max(name[, identifier[, t_column[, v_column]]]]) -> float

        Return the max of the Data specified by the name (and identifier) parameter(s)during plasma lifespan

        parameters are the same as for :func:`Shot.calculate_during_plasma`
        """
        return self.calculate_during_plasma(amax, name, identifier, t_column, v_column)

    def calculate_min(self, name, identifier=None, t_column=0, v_column=1):
        """Shot.calculate_min(name[, identifier[, t_column[, v_column]]]]) -> float

        Return the min of the Data specified by the name (and identifier) parameter(s)during plasma lifespan

        parameters are the same as for :func:`Shot.calculate_during_plasma`
        """
        return self.calculate_during_plasma(amin, name, identifier, t_column, v_column)

class CurrentShot(Shot):
    """Class representing the current (most recent) discharge.

    Behaves like the standard :class:`Shot` class,
    but can be updated using the :func:`CurrentShot.update` method
    which is an alias for the class initializer.
    """
    def __init__(self):
        """Initialize a new :class:`Shot`-like instance representing the most recent discharge"""
        self.no_errors=True #well, so far
        try: #catch non-existent files, as some discharges may have failed
            self.name = 'operation/currentshot/' #symlink to current discharge folder
            self.number = self.cat_num('ShotNo')
            self.set_dir('shots/' + str(self.number) + '/')
            self.plasma = self.get_plasma()
        except IOError: #something is wrong
            self.no_errors=False
        self.read_config()

    update = __init__ #bound method

class CurrentSession(Session):
    """Class representing the current (most recent) session.

    Behaves like the standard :class:`Session` class,
    but can be updated using the :func:`CurrentSession.update` method
    which is an alias for the class initializer..
    """
    def __init__(self):
        self.name = 'operation/currentsession/' #data root
        self.set_dir(self.cat_str('Komora/AktDir')) #update name, AktDir file already contains 'tasks/'
        self.init_time=self.get_init_time()

    update = __init__ #bound method

################################################################
####                  PLOTTING METHODS                      ####
################################################################

#### these methods are "injected" into the matplotlib.figure.Figure class
#### they start with an underscore to show that they are not real methods to be used directly

################ DATASET FORMAT MANIPULATION ################

def _recursive_plot(self, shot, datasets):
    """recursive_plot(shot, datasets) -> <Axes instance(s)>

    Recursively go through datasets and and call :func:`Data.plot` on them

    Parameters
    ----------
    shot : Shot
        refernece to the Shot instance used for data access
    datasets : sequence of tuples or lists
        the same format as those for :func:`_comparison`
    """
    if len(datasets) > 2: #datasets are nested
        for dataset in datasets:
            recursive_plot(shot,dataset)
    else: #dataset not nested
        return shot[dataset[0]][dataset[1]].plot()

def _comparison(self, shots, datasets, columns=1, name=None):
    """Generate a figure comparing shots

    Used to compare specific data sets accross several discharges


    Parameters
    ----------
    shots : sequence
        a sequence of shot numbers (int or str) or Shot instances
    datasets : sequence of tuples of str
        each tuple is of the form ('datadir', 'data_identifier')
        or can be nested tuples which means the nested datasets will be plotted in the same plot, e.g. (('datadir', 'data_identifier'), (('datadir', 'data_identifier'),('datadir', 'data_identifier')))
    columns : int
        optional, make plots into so many columns (defaults to 1)
    name : str
        optional name for the figure, otherwise is generated automagically
    """
    if len(cells) > 2: #seems to be nested
        cells=len(datasets)
    else: #doesn't seem to be nested
        cells=1
        datasets=[datasets] #to make the code bellow work
    rows=(cells+columns-1)/columns #must return a rounded up value (yeah, from http://stackoverflow.com/questions/17944/how-to-round-up-the-result-of-integer-division)
    try: #shots may not be iterable
        for i in xrange(len(shots)):
            if not isinstance(shots[i],Shot):
                shots[i]=Shot(str(shots[i]))
    except TypeError: #shots not interable
        if not isinstance(shots,Shot):
            shots=Shot(str(shots))
        shots=[shots] #must be iterbale for further code
    for cell, dataset in zip(range(1,cells+1), datasets) : #plot each cell, this is more resourceful than going through each shot, because than there would be an overhead of add_subplot() calls
        self.add_subplot(rows, columns, cell)
        for shot in shots: #for each shot
            if len(dataset) > 2: #seems to be nested
                for dset in dataset:
                    recursive_plot(shot,dset)
            else: #just one plot in region
                shot[dataset[0]][dataset[1]].plot()


################ PLOTTING METHODS INJECTION ################

Fig.comparison=classmethod(_comparison)
Fig.recursive_plot=classmethod(_recursive_plot)

from distutils.core import setup

our_version = '0.2'

setup(name = 'pygolem',
      version = our_version,
      description = 'Python API for the GOLEM tokamak discharge database',
      author = 'Ondrej Grover, Michal Odstrcil, Tomas Odstrcil',
      author_email = 'ondrej.grover@gmail.com',
      license = 'BSD',
      requires = [
          'numpy',
          'scipy',
          'matplotlib',
          ],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: by Industry or Sector :: Science/Research',
          'Programming Language :: Python',
          'Topic :: Software Development',
          'Topic :: Scientific/Engineering :: Physics',
          'Operating System :: Grouping and Descriptive Categories :: OS Independent (Written in an interpreted language)',
          'License :: OSI-Approved Open Source :: BSD License',
          ],
      platforms =[
          'Windows',
          'Linux',
          ],
      url = 'http://sf.net/p/pygolem',
      download_url = 'http://sf.net/projects/pygolem/files/pygolem-' + our_version + '.zip', 
      packages = ['pygolem'],
      package_data = {'pygolem': ['data_configuration.cfg']},
      )

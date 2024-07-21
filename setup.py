#!/usr/bin/env python

"""
setup.py file for pcaspy
"""
import os
import platform
import sys
import shutil
import subprocess
import filecmp

# Use setuptools to include build_sphinx, upload/sphinx commands
try:
    from setuptools import setup, Extension
    from setuptools.command.build_py import build_py as _build_py
except:
    from distutils.core import setup, Extension
    from distutils.command.build_py import build_py as _build_py


import epicscorelibs.path
import epicscorelibs.config
import swig
os.environ["PATH"] += os.pathsep + swig.BIN_DIR

# build_py runs before build_ext so that swig generated module is not copied
# See http://bugs.python.org/issue7562
# This is a workaround to run build_ext ahead of build_py
class build_py(_build_py):
    def run(self):
        self.run_command('build_ext')
        _build_py.run(self)

# python 2/3 compatible way to load module from file
def load_module(name, location):
    if sys.hexversion < 0x03050000:
        import imp
        module = imp.load_source(name, location)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, location)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module

# check wether all paths exist
def paths_exist(paths):
    for path in paths:
        if not os.path.exists(path):
            return False
    return True

# define EPICS base path and host arch
EPICSBASE = epicscorelibs.path.base_path
HOSTARCH  = epicscorelibs.config.get_config_var("EPICS_HOST_ARCH")

PRE315 = False

# check whether PCAS is part of EPICS base installation
PCAS = None
if not os.path.exists(os.path.join(epicscorelibs.path.include_path, 'casdef.h')):
    PCAS = os.environ.get('PCAS')
    if not PCAS:
        raise IOError('It looks like PCAS module is not part of EPICS base installation. '
                      'Please define PCAS environment variable to the module path.')

# common libraries to link
libraries = ['cas', 'ca', 'gdd', 'Com']
if PRE315:
    libraries.insert(0, 'asIoc')
else:
    libraries.insert(0, 'dbCore')
umacros = []
macros   = []
cflags = []
lflags = []
dlls = []
extra_objects = []
# platform dependent libraries and macros
UNAME = platform.system()
if  UNAME.find('CYGWIN') == 0:
    UNAME = "cygwin32"
    CMPL = 'gcc'
elif UNAME == 'Windows':
    UNAME = 'WIN32'
    # MSVC compiler
    static = False
    if HOSTARCH in ['win32-x86', 'windows-x64', 'win32-x86-debug', 'windows-x64-debug']:
        core_dlls = ["ca.dll", "Com.dll"]
        if PCAS is None:
            core_dlls += ['cas.dll', 'gdd.dll']
            pcas_dlls = []
        else:
            pcas_dlls = ['cas.dll', 'gdd.dll']

        if PRE315:
            core_dlls += ['dbIoc.dll', 'dbStaticIoc.dll', 'asIoc.dll']
        else:
            core_dlls += ['dbCore.dll']
        for dll in core_dlls:
            dllpath = os.path.join(epicscorelibs.path.lib_path, dll)
            if not os.path.exists(dllpath):
                static = True
                break
            dll_dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pcaspy', dll)
            if not os.path.exists(dll_dest) or not filecmp.cmp(dllpath, dll_dest):
                shutil.copy(dllpath, dll_dest)
        for dll in pcas_dlls:
            dllpath = os.path.join(PCAS, "bin", HOSTARCH, dll)
            if not os.path.exists(dllpath):
                static = True
                break
            dll_dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pcaspy', dll)
            if not os.path.exists(dll_dest) or not filecmp.cmp(dllpath, dll_dest):
                shutil.copy(dllpath, dll_dest)
        macros += [('_CRT_SECURE_NO_WARNINGS', 'None'), ('_CRT_NONSTDC_NO_DEPRECATE', 'None'), ('EPICS_CALL_DLL', '')]
        cflags += ['/Z7']
        CMPL = 'msvc'
    if HOSTARCH in ['win32-x86-static', 'windows-x64-static'] or static:
        libraries += ['ws2_32', 'user32', 'advapi32']
        macros += [('_CRT_SECURE_NO_WARNINGS', 'None'), ('_CRT_NONSTDC_NO_DEPRECATE', 'None'), ('EPICS_DLL_NO', '')]
        umacros+= ['_DLL']
        cflags += ['/EHsc', '/Z7']
        lflags += ['/LTCG']
        if HOSTARCH[-5:] == 'debug':
            libraries += ['msvcrtd']
            lflags += ['/NODEFAULTLIB:libcmtd.lib']
        else:
            libraries += ['msvcrt']
            lflags += ['/NODEFAULTLIB:libcmt.lib']
        CMPL = 'msvc'
    # GCC compiler
    if HOSTARCH in ['win32-x86-mingw', 'windows-x64-mingw']:
        macros += [('_MINGW', ''), ('EPICS_DLL_NO', '')]
        lflags += ['-static',]
        CMPL = 'gcc'
    if HOSTARCH == 'windows-x64-mingw':
        macros += [('MS_WIN64', '')]
        CMPL = 'gcc'
elif UNAME == 'Darwin':
    CMPL = 'clang'
    if not SHARED:
        extra_objects = [os.path.join(epicscorelibs.path.lib_path, 'lib%s.a'%lib) for lib in libraries]
        if paths_exist(extra_objects):
            libraries = []
        else:
            extra_objects = []
            SHARED = True
elif UNAME == 'Linux':
    if not SHARED:
        extra_objects = [os.path.join(epicscorelibs.path.lib_path, 'lib%s.a'%lib) for lib in libraries]
        if paths_exist(extra_objects):
            # necessary when EPICS is statically linked
            libraries = ['rt']
            if subprocess.call('nm -u %s | grep -q rl_' % os.path.join(epicscorelibs.path.lib_path, 'libCom.a'), shell=True) == 0:
                libraries += ['readline']
        else:
            extra_objects = []
            SHARED = True
    CMPL = 'gcc'
elif UNAME == 'SunOS':
    # OS_CLASS used by EPICS
    UNAME = 'solaris'
    CMPL = 'solStudio'
else:
    raise IOError("Unsupported OS {0}".format(UNAME))

include_dirs = [ epicscorelibs.path.include_path]

library_dirs = [ epicscorelibs.path.lib_path ]

if PCAS:
    include_dirs.append(os.path.join(PCAS, 'include'))
    library_dirs.append(os.path.join(PCAS, 'lib', HOSTARCH))

cas_module = Extension('pcaspy._cas',
                       sources  =[os.path.join('pcaspy','casdef.i'),
                                  os.path.join('pcaspy','pv.cpp'),
                                  os.path.join('pcaspy','channel.cpp'),],
                       swig_opts=['-c++','-threads','-nodefaultdtor','-I%s'% epicscorelibs.path.include_path],
                       extra_compile_args=cflags,
                       include_dirs = include_dirs,
                       library_dirs = library_dirs,
                       libraries = libraries,
                       extra_link_args = lflags,
                       extra_objects = extra_objects,
                       define_macros = macros,
                       undef_macros  = umacros,)
# use runtime library path option if linking share libraries on *NIX
if UNAME not in ['WIN32'] and SHARED:
    cas_module.runtime_library_dirs += [epicscorelibs.path.lib_path]
    if PCAS:
        cas_module.runtime_library_dirs += [epicscorelibs.path.lib_path]

long_description = open('README.rst').read()
_version = load_module('_version', 'pcaspy/_version.py')

dist = setup (name = 'pcaspy',
              version = _version.__version__,
              description = """Portable Channel Access Server in Python""",
              long_description = long_description,
              author      = "Xiaoqiang Wang",
              author_email= "xiaoqiangwang@gmail.com",
              url         = "https://pypi.python.org/pypi/pcaspy",
              ext_modules = [cas_module],
              packages    = ["pcaspy"],
              package_data={"pcaspy" : dlls},
              cmdclass    = {'build_py':build_py},
              license     = "BSD",
              platforms   = ["Windows","Linux", "Mac OS X"],
              classifiers = ['Development Status :: 4 - Beta',
                             'Environment :: Console',
                             'Intended Audience :: Developers',
                             'License :: OSI Approved :: BSD License',
                             'Programming Language :: C++',
                             'Programming Language :: Python :: 2',
                             'Programming Language :: Python :: 3',
                             ],
              install_requires = ["epicscorelibs", "swig"]
              )

# Re-run the build_py to ensure that swig generated py files are also copied
build_py = build_py(dist)
build_py.ensure_finalized()
build_py.run()

#!/usr/bin/env python

"""setup.py file for pcaspy"""

import os
import platform
import subprocess
import sys
import sysconfig

import epicscorelibs.config
import epicscorelibs.path
import epicscorelibs_pcas.path

# Use setuptools to include build_sphinx, upload/sphinx commands
try:
    from setuptools import Extension, setup
except:
    from distutils.core import Extension, setup

from distutils.command.build_py import build_py as _build_py


# build_py runs before build_ext so that swig generated module is not copied
# See http://bugs.python.org/issue7562
# This is a workaround to run build_ext ahead of build_py
class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        _build_py.run(self)


# python 2/3 compatible way to load module from file
def load_module(name, location):
    if sys.hexversion < 0x03050000:
        import imp

        module = imp.load_source(name, location)
    else:
        import importlib

        spec = importlib.util.spec_from_file_location(name, location)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


# define EPICS base path and host arch
EPICSBASE = epicscorelibs.path.base_path


HOSTARCH = epicscorelibs.config.get_config_var("EPICS_HOST_ARCH")

# common libraries to link
libraries = ["cas", "ca", "gdd", "Com", "dbCore"]
umacros = []
macros = []
cflags = []
lflags = []
dlls = []
extra_objects = []
# platform dependent libraries and macros
UNAME = platform.system()
if UNAME.find("CYGWIN") == 0:
    UNAME = "cygwin32"
    CMPL = "gcc"
elif UNAME == "Windows":
    UNAME = "WIN32"
    # MSVC compiler
    static = False
    if HOSTARCH in ["win32-x86", "windows-x64", "win32-x86-debug", "windows-x64-debug"]:
        dlls = ["cas.dll", "ca.dll", "gdd.dll", "Com.dll", "dbCore.dll"]
        macros += [
            ("_CRT_SECURE_NO_WARNINGS", "None"),
            ("_CRT_NONSTDC_NO_DEPRECATE", "None"),
            ("EPICS_CALL_DLL", ""),
        ]
        cflags += ["/Z7"]
        CMPL = "msvc"
    if HOSTARCH in ["win32-x86-static", "windows-x64-static"] or static:
        libraries += ["ws2_32", "user32", "advapi32"]
        macros += [
            ("_CRT_SECURE_NO_WARNINGS", "None"),
            ("_CRT_NONSTDC_NO_DEPRECATE", "None"),
            ("EPICS_DLL_NO", ""),
        ]
        umacros += ["_DLL"]
        cflags += ["/EHsc", "/Z7"]
        lflags += ["/LTCG"]
        if HOSTARCH[-5:] == "debug":
            libraries += ["msvcrtd"]
            lflags += ["/NODEFAULTLIB:libcmtd.lib"]
        else:
            libraries += ["msvcrt"]
            lflags += ["/NODEFAULTLIB:libcmt.lib"]
        CMPL = "msvc"
    # GCC compiler
    if HOSTARCH in ["win32-x86-mingw", "windows-x64-mingw"]:
        macros += [("_MINGW", ""), ("EPICS_DLL_NO", "")]
        lflags += [
            "-static",
        ]
        CMPL = "gcc"
    if HOSTARCH == "windows-x64-mingw":
        macros += [("MS_WIN64", "")]
        CMPL = "gcc"
elif UNAME == "Darwin":
    CMPL = "clang"
    extra_objects = [
        os.path.join(epicscorelibs.path.lib_path, "lib%s.a" % lib) for lib in libraries
    ]
    libraries = []
elif UNAME == "Linux":
    # necessary when EPICS is statically linked
    extra_objects = [
        os.path.join(epicscorelibs.path.lib_path, "lib%s.a" % lib) for lib in libraries
    ]
    libraries = ["rt"]
    if (
        subprocess.call(
            "nm -u %s | grep -q rl_" % os.path.join(epicscorelibs.path.lib_path, "libCom.a"),
            shell=True,
        )
        == 0
    ):
        libraries += ["readline"]
    CMPL = "gcc"
elif UNAME == "SunOS":
    # OS_CLASS used by EPICS
    UNAME = "solaris"
    CMPL = "solStudio"
else:
    raise IOError("Unsupported OS {0}".format(UNAME))

cas_module = Extension(
    "pcaspy._cas",
    sources=[
        os.path.join("pcaspy", "casdef.i"),
        os.path.join("pcaspy", "pv.cpp"),
        os.path.join("pcaspy", "channel.cpp"),
    ],
    swig_opts=[
        "-c++",
        "-threads",
        "-nodefaultdtor",
        "-I%s" % epicscorelibs.path.include_path,
        "-I%s" % epicscorelibs_pcas.path.include_path,
    ],
    extra_compile_args=cflags,
    include_dirs=[
        epicscorelibs.path.include_path,
        epicscorelibs_pcas.path.include_path,
    ],
    library_dirs=[
        epicscorelibs.path.lib_path,
        epicscorelibs_pcas.path.lib_path,
    ],
    libraries=libraries,
    extra_link_args=lflags,
    extra_objects=extra_objects,
    define_macros=macros,
    undef_macros=umacros,
)
# other *NIX linker has runtime library path option
if UNAME not in ["WIN32", "Darwin", "Linux"]:
    cas_module.runtime_library_dirs += (os.path.join(EPICSBASE, "lib", HOSTARCH),)

long_description = open("README.rst").read()
_version = load_module("_version", "pcaspy/_version.py")

requirements = [
    "epicscorelibs",
    "epicscorelibs_pcas @ git+https://github.com/IsisComputingGroup/epicscorelibs_pcas@main",
]

dist = setup(
    name="pcaspy",
    version=_version.__version__,
    description="""Portable Channel Access Server in Python""",
    long_description=long_description,
    author="Xiaoqiang Wang",
    author_email="xiaoqiangwang@gmail.com",
    url="https://pypi.python.org/pypi/pcaspy",
    ext_modules=[cas_module],
    packages=["pcaspy"],
    package_data={"pcaspy": dlls},
    cmdclass={"build_py": build_py},
    license="BSD",
    platforms=["Windows", "Linux", "Mac OS X"],
    install_requires=requirements,
    setup_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: C++",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)

# Re-run the build_py to ensure that swig generated py files are also copied
build_py = build_py(dist)
build_py.ensure_finalized()
build_py.run()

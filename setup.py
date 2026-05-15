#!/usr/bin/env python

"""
setup.py file for SWIG
"""

import platform
from setuptools import Extension, setup, find_packages
import sysconfig
import numpy


# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

libraries = ['fftw3f']
comp_args = ["/arch:AVX","/O2","/openmp"]
link_args = []
files2 = [  "omp.h",
            "fftw3.h",
            "fftw3f.dll",
            "fftw3f.lib",
            "libfftw3fmac.a",
            "libfftw3f_ompmac.a",
            "libfftw3fl.so",
            "libfftw3f_ompl.so",
            "libomp.a"
        ]
files = [
            "fcwt.h",
            "fcwt.cpp"
]

files = files + files2

if "macosx" in sysconfig.get_platform() or "darwin" in sysconfig.get_platform():
    libraries = ['fftw3fmac','fftw3f_ompmac','omp']
    comp_args = ["-O3","-Xpreprocessor","-fopenmp"]

    # Only Intel can use AVX.
    if platform.machine().lower() in ("x86_64", "amd64"):
        comp_args.append("-mavx")

if "linux" in sysconfig.get_platform():
    libraries = ['fftw3fl','fftw3f_ompl',"gomp"]
    comp_args = ["-mavx","-O3","-fopenmp"]
    link_args = ["-fopenmp"]


setup (ext_modules=[
            Extension('fcwt._fcwt',
                sources=[
                    'src/fcwt/fcwt.cpp',
                    'src/fcwt/fcwt_wrap.cxx'
                ],
                library_dirs = ['libs'],
                include_dirs = ['src/fcwt','src',numpy_include,'libs'],
                libraries = libraries,
                extra_compile_args = comp_args,
                extra_link_args = link_args
            )
        ],
        packages=find_packages(where='src'),
        package_dir={'fcwt': 'src/fcwt'},
        package_data={'fcwt':files}
        )

#swig -c++ -python fcwt-swig.i
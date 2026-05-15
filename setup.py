#!/usr/bin/env python

"""
setup.py file for SWIG
"""

import numpy
from pathlib import Path
import platform
from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext
import shutil
import sysconfig

ROOT = Path(__file__).parent.resolve()
LIBS = ROOT / "libs"

# Platform detection
PLATFORM = sysconfig.get_platform()
MACHINE = platform.machine().lower()

IS_MACOS = PLATFORM.startswith("macosx") or "darwin" in PLATFORM
IS_LINUX = PLATFORM.startswith("linux")
IS_WINDOWS = PLATFORM.startswith("win")
IS_X86 = MACHINE in ("x86_64", "amd64")

class BuildExt(build_ext):
    def build_extension(self, ext):
        super().build_extension(ext)

        ext_path = Path(self.get_ext_fullpath(ext.name)).resolve()
        ext_dir = ext_path.parent

        if IS_WINDOWS:
            shutil.copy2(LIBS / "fftw3f.dll", ext_dir / "fftw3f.dll")

        elif IS_LINUX:
            # Loader wants the ELF SONAME names, not this repo's custom filenames.
            shutil.copy2(LIBS / "libfftw3fl.so", ext_dir / "libfftw3f.so.3")
            shutil.copy2(LIBS / "libfftw3f_ompl.so", ext_dir / "libfftw3f_omp.so.3")


# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

include_dirs = ["src/fcwt", "src", "libs", numpy.get_include()]
library_dirs = ["libs"]
libraries = []
link_args = []
files2 = [
    "omp.h",
    "fftw3.h",
    "fftw3f.dll",
    "fftw3f.lib",
    "libfftw3fmac.a",
    "libfftw3f_ompmac.a",
    "libfftw3fl.so",
    "libfftw3f_ompl.so",
    "libomp.a",
]
files = ["fcwt.h", "fcwt.cpp"]

files = files + files2

plat = sysconfig.get_platform()
machine = platform.machine().lower()

if IS_MACOS:
    libraries = ["fftw3fmac", "fftw3f_ompmac", "omp"]
    comp_args = ["-O3", "-Xpreprocessor", "-fopenmp"]

    # Only Intel can use AVX.
    if IS_X86:
        comp_args.append("-mavx")

    omp_prefix = Path("/opt/homebrew/opt/libomp")
    if not omp_prefix.exists():
        omp_prefix = Path("/usr/local/opt/libomp")

    include_dirs.append(str(omp_prefix / "include"))
    libraries.append(str(omp_prefix / "lib"))
    link_args = [
        "-Wl,-rpath," + str(omp_prefix / "lib"),
    ]

if IS_LINUX:
    libraries = ["fftw3fl", "fftw3f_ompl", "gomp"]
    comp_args = ["-mavx", "-O3", "-fopenmp"]
    link_args = ["-fopenmp"]


if IS_WINDOWS:
    libraries = ["fftw3f"]
    comp_args = ["/arch:AVX", "/O2", "/openmp"]


setup(
    ext_modules=[
        Extension(
            "fcwt._fcwt",
            sources=["src/fcwt/fcwt.cpp", "src/fcwt/fcwt_wrap.cxx"],
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            libraries=libraries,
            extra_compile_args=comp_args,
            extra_link_args=link_args,
        )
    ],
    cmdclass={"build_ext": BuildExt},
    packages=find_packages(where="src"),
    package_dir={"fcwt": "src/fcwt"},
    package_data={"fcwt": files},
)

# swig -c++ -python fcwt-swig.i

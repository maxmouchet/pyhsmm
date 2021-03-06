import shutil
import tarfile
from pathlib import Path
from urllib.request import urlretrieve

import numpy
import requests
from setuptools import Extension, setup
from Cython.Build import cythonize


def download_eigen(deps_dir):
    deps_dir = Path(deps_dir)
    deps_dir.mkdir(exist_ok=True)

    # download Eigen if we don't have it in deps
    # TODO: Can we cleanup this?
    eigenurl = "https://gitlab.com/libeigen/eigen/-/archive/3.3.7/eigen-3.3.7.tar.gz"
    eigenpath = deps_dir.joinpath("Eigen")
    eigentarpath = deps_dir.joinpath("Eigen.tar.gz")
    if not eigenpath.exists():
        print("Downloading Eigen...")
        r = requests.get(eigenurl)
        with open(eigentarpath, 'wb') as f:
            f.write(r.content)
        with tarfile.open(eigentarpath, "r") as tar:
            tar.extractall("deps")
        thedir = next(deps_dir.glob("eigen-*"))
        shutil.move(thedir.joinpath("Eigen"), eigenpath)
        print("...done!")


def find_extensions(deps_dir):
    extensions = []
    for pyx in Path("pyhsmm").glob("**/*.pyx"):
        ext_name = ".".join(pyx.with_suffix("").parts)
        print(f"Extension {ext_name}: {pyx}")
        extensions.append(
            Extension(
                ext_name,
                sources=[str(pyx)],
                include_dirs=[deps_dir, numpy.get_include()],
                extra_compile_args=[
                    "-O3",
                    "-std=c++11",
                    "-DNDEBUG",
                    "-w",
                    "-DHMM_TEMPS_ON_HEAP",
                ],
            )
        )
    return extensions


download_eigen("deps")
extensions = find_extensions("deps")

setup(
    name="pyhsmm",
    version="0.1.6",
    description="Bayesian inference in HSMMs and HMMs",
    author="Matthew James Johnson",
    author_email="mattjj@csail.mit.edu",
    url="https://github.com/mattjj/pyhsmm",
    license="MIT",
    packages=["pyhsmm", "pyhsmm.basic", "pyhsmm.internals", "pyhsmm.util"],
    platforms="ALL",
    keywords=[
        "bayesian",
        "inference",
        "mcmc",
        "time-series",
        "monte-carlo",
        "variational inference",
        "mean field",
        "vb",
    ],
    install_requires=[
        "matplotlib",
        "numpy",
        "scipy",
        "pybasicbayes@git+https://github.com/maxmouchet/pybasicbayes.git",
    ],
    ext_modules=cythonize(extensions),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: C++",
    ],
)

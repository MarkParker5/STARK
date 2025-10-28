import glob
import os
import sys
from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

ext_modules = [
    Extension(path.replace("/", ".").replace(".pyx", ""), [path])
    for path in glob.glob("**/*.pyx", recursive=True)
]

# if force in args, cleanup
if "--force" in sys.argv:
    extensions = [".so", ".dll", ".tmp", ".c"]
    for ext in extensions:
        for file_path in glob.glob(f"**/*{ext}", recursive=True):
            os.remove(file_path)

setup(
    ext_modules=cythonize(ext_modules, compiler_directives={"boundscheck": False}),
    include_dirs=[numpy.get_include()],
)

from setuptools import setup, dist
from setuptools.extension import Extension
from codecs import open
from os import path

from Cython.Build import cythonize
import numpy
import spacy, cymem, preshed
from distutils.sysconfig import get_python_inc

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line.split("#")[0].strip() for line in lineiter if line and not line.startswith("#")]

print(parse_requirements('requirements.txt'))

def get_version():
    """Load the version from version.py, without importing it.

    This function assumes that the last line in the file contains a variable defining the
    version string with single quotes.

    """
    try:
        with open('PyRuSH/version.py', 'r') as f:
            return f.read().split('\n')[0].split('=')[-1].replace('\'', '').strip()
    except IOError:
        return "0.0.0a1"

COMPILER_DIRECTIVES = {
    "language_level": 3,
    "embedsignature": True,
    "annotation_typing": False,
}
dir_path = path.dirname(path.realpath(__file__))

include_dirs = [dir_path + "/PyRuSH", dir_path,
                numpy.get_include(),
                path.dirname(spacy.__file__),
                path.dirname(cymem.__file__),
                path.dirname(preshed.__file__)]
extensions = [
    Extension(
        'PyRuSH.StaticSentencizerFun',
        sources=['PyRuSH/StaticSentencizerFun.pyx'],
        include_dirs=include_dirs,
        language='c++',
        extra_compile_args=["-std=c++11"],
    )
]

setup(
    name='PyRuSH',
    packages=['PyRuSH'],  # this must be the same as the name above
    version=get_version(),
    description='A fast implementation of RuSH (Rule-based sentence Segmenter using Hashing).',
    author='Jianlin',
    author_email='jianlinshi.cn@gmail.com',
    url='https://github.com/jianlins/PyRuSH',  # use the URL to the github repo
    keywords=['PyFastNER', 'ner', 'regex'],
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    license='Apache License',
    zip_safe=False,
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    ext_modules=cythonize(extensions, compiler_directives=COMPILER_DIRECTIVES),
    tests_require='pytest',
    package_data={'': ['*.pyx', '*.pxd', '*.so', '*.dll', '*.lib', '*.cpp', '*.c','../conf/rush_rules.tsv','../requirements.txt']},
)

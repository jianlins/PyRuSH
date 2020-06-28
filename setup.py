from setuptools import setup
from codecs import open
from os import path
from setuptools.extension import Extension
from Cython.Build import cythonize, build_ext

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


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


dir_path = path.dirname(path.realpath(__file__))
include_dirs = [dir_path + "/PyRuSH", dir_path, dir_path + "/PyRuSH"]
extensions = [
    Extension(
        'PyRuSH.StaticSentencizerFun',
        sources=['PyRuSH/StaticSentencizerFun.pyx'],
        include_dirs=include_dirs,
    ),
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
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    license='Apache License',
    zip_safe=False,
    install_requires=[
        'PyFastNER>=1.0.8b1', 'spacy>=2.2.2'
    ],
    ext_modules=cythonize(extensions, language_level=3),
    setup_requires=[
        'PyFastNER>=1.0.8b9', 'spacy>=2.2.2'
    ],
    test_suite='nose.collector',
    tests_require='nose',
    data_files=[('demo_data', ['conf/rush_rules.tsv', 'conf/logging.ini'])],
    package_data={'': ['*.pyx', '*.pxd', '*.so', '*.dll', '*.lib', '*.cpp', '*.c']},
)

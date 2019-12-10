import platform
from setuptools import setup, find_packages

_tableausdk_hyper_system = {
    'Windows': 'https://downloads.tableau.com/tssoftware/extractapi-py-x64-2019-2-6.zip',
    'Darwin': 'https://downloads.tableau.com/tssoftware/extractapi-py-osx64-2019-2-6.tar.gz',
    'Linux': 'https://downloads.tableau.com/tssoftware/extractapi-py-linux-x86_64-2019-2-6.tar.gz'
}

_tableausdk_tde_system = {
    'Windows': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Win-64Bit-10-3-26.zip',
    'Darwin': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-OSX-64Bit-10-3-26.tar.gz',
    'Linux': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Linux-64Bit-10-3-26.tar.gz'
}


def _build_non_pypi_extra_uri(urimap):
    return 'tableausdk @ ' + urimap[platform.system()] + '#egg=tableausdk'


_hyper_dep_uri = _build_non_pypi_extra_uri(_tableausdk_hyper_system)
_tde_dep_uri = _build_non_pypi_extra_uri(_tableausdk_tde_system)

setup(name='pandleau',
      version='0.3.2-SNAPSHOT',
      packages=find_packages(exclude=['tests*']),
      license='MIT',
      description='A quick and easy way to convert a Pandas DataFrame to a Tableau extract.',
      long_description=open('README.md').read(),
      install_requires=['pandas', 'numpy', 'tqdm'],
      extras_require={
          'tde': _tde_dep_uri,
          'hyper': _hyper_dep_uri,
      },
      author='Benjamin Wiley <bewi7122@colorado.edu>, Zhirui(Jerry) Wang <zw2389@columbia.edu>,'
             'Aaron Wiegel <aawiegel@gmail.com>',
      url='https://github.com/bwiley1/pandleau',
      download_url='https://github.com/bwiley1/pandleau/dist/pandleau-0.3.1.tar.gz',
      py_modules=['pandleau'],
      keywords='tableau pandas extract tde hyper',
      classifiers=['Programming Language :: Python'])

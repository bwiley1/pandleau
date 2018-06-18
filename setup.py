from setuptools import setup, find_packages


setup(name='pandleau',
      version='0.3',
      packages=find_packages(exclude=['tests*']),
      license='MIT',
      description='A quick and easy way to convert a Pandas DataFrame to a Tableau extract.',
      long_description=open('README.md').read(),
      install_requires=['pandas','numpy','tableausdk'],
      author=['Benjamin Wiley','Zhirui(Jerry) Wang'],
      author_email=['bewi7122@colorado.edu','zw2389@columbia.edu'],
      url='https://github.com/bwiley1/pandleau',
      download_url='https://github.com/bwiley1/pandleau/dist/pandleau-0.3.tar.gz',
      py_modules=['pandleau'],
      keywords='tableau pandas extract tde hyper',
      classifiers=['Programming Language :: Python'])

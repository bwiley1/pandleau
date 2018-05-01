from setuptools import setup, find_packages


setup(name='pandleau',
      version='0.2',
      packages=find_packages(exclude=['tests*']),
      license='MIT',
      description='A quick and easy way to convert a Pandas DataFrame to a Tableau extract.',
      long_description=open('README.md').read(),
      install_requires=['pandas','numpy','tableausdk'],
      author='Benjamin Wiley',
      author_email='bewi7122@colorado.edu',
      url='https://github.com/bwiley1/pandleau',
      download_url='https://github.com/bwiley1/pandleau/dist/pandleau-0.2.tar.gz',
      py_modules=['pandleau'],
      keywords='tableau pandas extract tde',
      classifiers=['Programming Language :: Python'])

from setuptools import setup, find_packages


setup(name='andromeda',
      version='0.1.0',
      description='declarative, class-driven framework written around flask',
      author='Roy Sommer',
      url='https://www.github.com/illberoy/andromeda',
      download_url='https://github.com/illberoy/andromda/tarball/0.1.0',
      packages=find_packages(),
      include_package_data=True,
      py_modules=['andromeda'],
      install_requires=['flask==0.12.2'])

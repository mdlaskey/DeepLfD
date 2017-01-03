"""
Setup of Deep LfD python codebase
Author: Michael Laskey
"""
from setuptools import setup

setup(name='deep_lfd',
      version='0.1.dev0',
      description='Deep LfD project code',
      author='Michael Laskey',
      author_email='laskeymd@berkeley.edu',
      package_dir = {'': 'src'},
      packages=['deep_lfd', 'deep_lfd.rgbd', 'deep_lfd.control', 'deep_lfd.core', 'deep_lfd.synthetic','deep_lfd.k_pi'],
     )

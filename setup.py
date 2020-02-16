from setuptools import setup

package = 'single_use'
version = '0.1'

setup(name=package,
      version=version,
      description="description",
      url='url',
      install_requires=['pyyaml', 'argparse'],
      entry_points={
          'console_scripts': ['single-use-ssh-key = single_use.app:main']
      })

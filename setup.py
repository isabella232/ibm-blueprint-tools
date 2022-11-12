from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# # Implements parse_requirements as standalone functionality
# with open("requirements.txt") as f:
#     reqs = [l.strip('\n')
#             for l in f if l.strip('\n') and not l.startswith('#')]


setup(
    name='blueprint',
    version='1.0.0',
    description='IBM Blueprint tool that extracts insights in a yaml file which are further used in validating and analyzing the files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nishu Bharti',
    author_email='nishu.bhart1@ibm.com',
    packages=find_packages(exclude=['ez_setup', 'data', 'docs']),
    scripts=['bin/blueprint'],
    install_requires=['yamale == 4.0.4'],
    include_package_data = True
    )

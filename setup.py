# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Implements parse_requirements as standalone functionality
with open("requirements.txt") as f:
    reqs = [l.strip('\n')
            for l in f if l.strip('\n') and not l.startswith('#')]


setup(
    name='blueprint',
    version='1.0.0',
    description='Blueprint tools for IBM Cloud Schematics',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nishu Bharti',
    author_email='nishu.bhart1@ibm.com',
    packages=find_packages(include=['blueprint', 'blueprint.*']),
    scripts=['bin/blueprint'],
    install_requires=reqs,
    include_package_data = True
    )


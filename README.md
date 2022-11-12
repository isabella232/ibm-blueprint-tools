# IBM Blueprint tools

1. [About bluperint tool](#about)
2. [Installation](#installation)
3. [Usage](#usage)

## About
The IBM Blueprint tool is for analyzing and validating the Ibmcloud blueprint configurations file.


## Installation
The blueprint validator can be install as a CLI tool using the following steps.

### Prerequisite
* Must install [Python version 3.8](https://www.python.org/downloads/release/python-380/) and above.
* Setup the [CLI tool]

### Setup CLI tool

Execute following steps to setup the command line tool.
1. Download the released tgz file, or fork the [IBM Blueprint tools](https://github.com/IBM-Cloud/ibm-blueprint-tools) repository.
2. From the forked Git repository, in the terminal run `pip3 install build` and `python3 -m build` commands to create wheel file and tar file. (install the wheel package if not present on machine, run the command `pip3 install wheel` on terminal). By default, it is placed in dist/ under the current directory.
3. Run `pip3 install dist/blueprint-1.0.0-py3-none-any.whl` to fetch a wheel or a source distribution depending on your specific setup file.

## Usage

### IBMCloud blueprint validator tool

The blueprint validator can be used from your terminal, by running the following command

> blueprint --schema-validate -f [provide the absolute yaml file path]

```text 
usage: blueprint [-h] [-f input_file_with_path] [schema-validate]

Tool for analysing blueprint templates

positional arguments:
  schema-validate       terraform configuration directory

optional arguments:
  -h, --help            show this help message and exit
  -f input_file_with_path, --yaml_file input_file_with_path
                        input yaml file name (with path)
The log analyzer can be used from your terminal, by running the following command
```

## Future roadmap

Here are the list of enhancements to the tool in the future releases:
- Enhance the validator tool with more customised validators.
- add more sub-tools like concating the sub-yaml files.

## Contact

Contact the authors of the tool:

- Nishu Bharti (nishu.bharti1@ibm.com)
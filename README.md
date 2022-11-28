# Blueprint dev-tools for IBM Cloud Schematics

1. [About bluperint dev-tools](#about)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Examples](#examples)
5. [Future roadmap](#future-roadmap)

## About
The `blueprint dev-tools` is used for analyzing, validating and working with the IBM Cloud Schematics - blueprint configurations file.  

Refer to IBM Cloud Schematics docs for more information about [blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-blueprint-intro).

---

## Installation
  Install the blueprint dev-tools CLI using the following steps.

  ### Prerequisite
  * Must use [Python version 3.8](https://www.python.org/downloads/release/python-380/) and above.

  ### Setup CLI

  Steps:
  1. Download the released tgz file, or fork the [blueprint dev-tools](https://github.com/IBM-Cloud/ibm-blueprint-tools) repository.
  2. Run the following commands to create wheel and tar file
      ```sh
        pip3 install wheel
        pip3 install build
        python3 -m build
      ```
      By default, the resulting wheel or tar files are placed in `dist/` folder under the current directory.
  3. Run the following commands to fetch a wheel or a source distribution, depending on your specific setup file.
      ```sh
        pip3 install dist/blueprint-1.0.0-py3-none-any.whl
      ```
---
## Usage

  The goal of `blueprint dev-tools` is to ease the consumption of blueprint in IBM Cloud Schematics.  It includes multiple Python tools & libraries, such as following:
  * Schema validation of the blueprint configuration file (blueprint.yaml)
  * Merge or assemble the blueprint.yaml from its parts
  * Assemble the blueprint.yaml using Python libraries
  
  ### Blueprint CLI usage

  Use the `blueprint dev-tools` CLI to validate and work with the blueprint configuration files.

  > blueprint -h
      
      usage: blueprint [-h] {validate,merge} ...

      Blueprint helper tools for IBM Cloud Schematics

      positional arguments:
        {validate,merge,generate}

      optional arguments:
        -h, --help            show this help message and exit


  #### Blueprint schema validator usage

  Use the `blueprint validate` command to verify the schema of the blueprint configuration file (blueprint.yaml)

  > blueprint validate -h

      usage: blueprint validate [-h] -b BP_FILE [-w WORKING_DIR]

      optional arguments:
        -h, --help                                          Show this help message and exit
        -b BP_FILE, --bp-file BP_FILE                       Input blueprint yaml file
        -w WORKING_DIR, --working-dir WORKING_DIR           Working directory for validate command


  #### Blueprint schema merge usage

  Use the `blueprint merge` command to use a blueprint manifest (manifest.yaml file) to assemble the parts of the blueprint configuration file (blueprint.yaml)

  > blueprint merge -h

      usage: blueprint merge [-h] -m MANIFEST_FILE [-w WORKING_DIR] [-o OUT_FILE]

      optional arguments:
        -h, --help                                          Show this help message and exit
        -m MANIFEST_FILE, --manifest-file MANIFEST_FILE     Blueprint manifest file
        -w WORKING_DIR, --working-dir WORKING_DIR           Working directory for merge command
        -o OUT_FILE, --out-file OUT_FILE                    Output blueprint yaml file

### Blueprint Python library usage

  Use the `blueprint Python library` to assemble the blueprint configuration file - using Python.

  The library includes the following schema elements, that can be used to define your blueprint manifest
  * schema.blueprint.Blueprint
  * schema.module.Module
  * schema.source.Source
  * schema.source.GitSource
  * schema.source.CatalogSource
  * schema.param.Input
  * schema.param.Output
  * schema.param.Setting

  Further, the library can be used to wire the input & output parameters, using the following 
  * circuit.Bus
  * circuit.Wire

  The library has built-in validation - and emits error or warning events (lib.event.ValidationEvent).

  Refer to example Python code, in this (folder)[./examples/generate/README.md].

---
## Examples

  |   | Example             | Folder     | Description           |
  |---|---------------------|------------|-----------------------|
  | 1 | Schema validator    | `./examples/validate/app.py` | The `validate/app.py` illustrate the use of the `blueprint.schema.validate.validator.Validator` class to validate a blueprint configuration file.|
  | 2 | Schema merge        | `./examples/validate/app.py` | The `merge/app.py` illustrate the use of `blueprint.merge.load.BPLoader` class to load manifest file, to generate a blueprint configuration file. </br> The `./examples/validate/data-1/manifest.yaml` & `./examples/validate/data-2/manifest.yaml` are sample blueprint manifest file. |
  | 3 | Schema generate     | `./examples/generate/bp_basic.py` | The `generate/bp_basic.py` illustrate the use of `blueprint.schema` & `blueprint.circuit` library classes to generate a blueprint configuation file, using Python code |

---
## Future roadmap

  The roadmap for this tootset include the following:
  - blueprint-run: Support to run & test the blueprint configuration using the local Terraform CLI
  - and more.. 

---

## Contact

  Contact the author(s) of the tool:

  - Nishu Bharti (nishu.bharti1@ibm.com)

---

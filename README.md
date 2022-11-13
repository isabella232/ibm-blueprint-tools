# IBM Cloud Schematics - blueprint toolset

1. [About bluperint toolset](#about)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Future roadmap](#future-roadmap)

## About
The `blueprint toolset` is used for analyzing, validating and working with the IBM Cloud Schematics - blueprint configurations file.  

Refer to IBM Cloud Schematics docs for more information about [blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-blueprint-intro).

---

## Installation
  The blueprint toolset CLI can be install, using the following steps.

  ### Prerequisite
  * Must use [Python version 3.8](https://www.python.org/downloads/release/python-380/) and above.

  ### Setup CLI

  Steps:
  1. Download the released tgz file, or fork the [blueprint toolset](https://github.com/IBM-Cloud/ibm-blueprint-tools) repository.
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

  The goal of `blueprint toolset` is to ease the consumption of blueprint in IBM Cloud Schematics.  It includes multiple Python tools & libraries, such as following:
  * Blueprint schema validation

  ### Blueprint schema validator usage

  > blueprint --schema-validate -f [blueprint yaml file, with absolute path]

  ```text 
    usage: blueprint [-h] [schema-validate] [-f input_file_with_path]

    Work with blueprint templates

    positional arguments:
      schema-validate       validate the blueprint schema file

    optional arguments:
      -h, --help            show this help message and exit
      -f input_file_with_path, --yaml_file input_file_with_path
                            input blueprint file name (with path)
  ```

---
## Future roadmap

  The roadmap for this tootset include the following:
  - schema-validator: Add more custom validators, to the blueprint schema validation
  - schema-merge: Support to merge multiple blueprint fragments into a single blueprint file.
  - blueprint-config-inspect: Support to introspect the input & output metadata of the blueprints, and the internal modules
  - and more.. 

## Contact

  Contact the author(s) of the tool:

  - Nishu Bharti (nishu.bharti1@ibm.com)

---

# Blueprint dev-tools for IBM Cloud Schematics

1. [About bluperint dev-tools](#about)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Examples](#examples)
5. [Future roadmap](#future-roadmap)

## About
The `blueprint dev-tools` is used for analyzing, validating and working with the IBM Cloud Schematics - blueprint configurations file.  

Refer to IBM Cloud Schematics docs for more information about [blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-blueprint-intro).

> Note: 
> * These dev-tools are not supported by IBM.  It can be used on as-is basis.
> * When you find an issue, please raise a Pull-Request (with the fix).

---

## Installation
  Install the blueprint dev-tools CLI using the following steps.

### Prerequisite
  * Must use [Python version 3.9](https://www.python.org/downloads/) and above.
  * requirements.txt
    * yamale >= 4.0.4
    * PyYAML >= 6.0
    * ruamel.yaml >=  0.17.21
    * GitPython >= 3.1.29
    * python-terraform >= 0.10.1
    * git-url-parse >= 1.2.2
    * graphviz >= 0.19.0
    * diagrams >= 0.23.1
    * pygraphviz >= 1.10

> Note: Use the following command to install `pygraphviz` in your Mac OS
> 
> python3 -m pip install --global-option=build_ext --global-option="-I$(brew --prefix graphviz)/include/"  --global-option="-L$(brew --prefix graphviz)/lib/" pygraphviz
> 

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
        
        usage: blueprint [-h] {validate,draw,merge,sync,run} ...

        Blueprint helper tools for IBM Cloud Schematics

        positional arguments:
          {validate,draw,merge,sync,run}

        optional arguments:
          -h, --help            show this help message and exit


#### _Blueprint schema validator usage_

  Use the `blueprint validate` command to verify the schema of the blueprint configuration file (blueprint.yaml)

    > blueprint validate -h

        usage: blueprint validate [-h] -b BP_FILE [-w WORKING_DIR]

        optional arguments:
          -h, --help                                          show this help message and exit
          -b BP_FILE, --bp-file BP_FILE                       Input blueprint configuration yaml file
          -s SOURCE_DIR, --source-dir SOURCE_DIR              source directory for input files
          -l LOG_FILE, --log-file LOG_FILE                    log file
          -e {DEBUG,INFO,WARNING,ERROR}, 
              --log-level {DEBUG,INFO,WARNING,ERROR}          log level

  Refer to examples in the `examples/validate` folder. 

#### _Blueprint schema draw usage_

  Use the `blueprint draw` command to verify the draw a graph illustrating dependencies between modules in a blueprint configuration file (blueprint.yaml)

    > blueprint draw -h

        usage: blueprint draw [-h] -b BP_FILE [-s SOURCE_DIR] [-o OUT_FILE] [-f {png,jpg,svg,pdf,dot}] [-l LOG_FILE]
                              [-e {DEBUG,INFO,WARNING,ERROR}]

        optional arguments:
          -h, --help                                          show this help message and exit
          -b BP_FILE, --bp-file BP_FILE                       input blueprint configuration yaml file
          -s SOURCE_DIR, --source-dir SOURCE_DIR              source directory for input files
          -o OUT_FILE, --out-file OUT_FILE                    output blueprint drawing file
          -f {png,jpg,svg,pdf,dot}, --out-format              format of the blueprint drawing file ("png", "jpg", "svg", "pdf", "dot")
          -l LOG_FILE, --log-file LOG_FILE                    log file
          -e {DEBUG,INFO,WARNING,ERROR}, 
              --log-level {DEBUG,INFO,WARNING,ERROR}          log level

  Refer to examples in the `examples/draw` folder. 
  
#### _Blueprint schema merge usage_

  Use the `blueprint merge` command to assemble the parts of the blueprint configuration file (blueprint.yaml) from a blueprint manifest (manifest.yaml file).

    > blueprint merge -h

        usage: blueprint merge [-h] -m MANIFEST_FILE [-w WORKING_DIR] [-o OUT_FILE]

        optional arguments:
          -h, --help                                          show this help message and exit
          -m MANIFEST_FILE, --manifest-file MANIFEST_FILE     input Blueprint manifest file
          -s SOURCE_DIR, --source-dir SOURCE_DIR              source directory for input files
          -o OUT_FILE, --out-file OUT_FILE                    output blueprint configuration yaml file
          -l LOG_FILE, --log-file LOG_FILE                    log file
          -e {DEBUG,INFO,WARNING,ERROR}, 
              --log-level {DEBUG,INFO,WARNING,ERROR}          log level
  
  Refer to examples in the `examples/merge` data folder.

#### _Blueprint schema sync usage_

  Use the `blueprint sync` command to sychronize the module inputs & output parameters - in the blueprint configuration file (blueprint.yaml) with the corresponding definition in the Terraform template.

  Pre-req: 
  * Install (terraform-config-inspect)[https://github.com/ibm-cloud/terraform-config-inspect] in your machine
  * Set TERRAFORM_CONFIG_INSPECT_PATH to the install location of the terraform-config-inspect tool.

    > blueprint sync -h

        usage: blueprint sync [-h] -b BP_FILE [-s SOURCE_DIR] -o OUT_FILE -w WORKING_DIR [-l LOG_FILE] [-e {DEBUG,INFO,WARNING,ERROR}]

        optional arguments:
          -h, --help                                          show this help message and exit
          -b BP_FILE, --bp-file BP_FILE                       input blueprint lite configuration yaml file
          -s SOURCE_DIR, --source-dir SOURCE_DIR              source directory for input files
          -w WORKING_DIR, --working-dir WORKING_DIR           working directory for the intermediate files
          -o OUT_FILE, --out-file OUT_FILE                    output blueprint configuration yaml file
          -l LOG_FILE, --log-file LOG_FILE                    log file
          -e {DEBUG,INFO,WARNING,ERROR}, 
              --log-level {DEBUG,INFO,WARNING,ERROR}          log level setting
  
  Refer to examples in the `examples/sync` data folder.

#### _Blueprint run usage_

  Use the `blueprint run` command to run the *blueprint configuration file* (blueprint.yaml), using the input data in the local machine.  
  
  The `blueprint run` will download the templates from the Git repositories in the local file system (one folder per module, in the working directory). Further, it uses the local Terraform CLI installation to run the `blueprint run -c init`, `blueprint run -c plan`, `blueprint run -c apply` & `blueprint run -c destroy` commands for all its modules.

  The `--dry-run` option will _not_ download the template, instead it will generate a dummy Terraform template for each module (with inputs & outputs specified in the *blueprint configuration yaml* file).  You can use these dummy terraform templates to verify the data flows in the log files.

    > blueprint run -h

        usage: blueprint run [-h] -c {init,plan,apply,destroy,output} [-d] -b BP_FILE -i INPUT_FILE [-s SOURCE_DIR] [-w WORKING_DIR] [-o OUT_FILE]
                      [-l LOG_FILE] [-e {DEBUG,INFO,WARNING,ERROR}]

        optional arguments:
          -h, --help                                          show this help message and exit
          -c {init,plan,apply,destroy}, 
              --sub-command {init,plan,apply,destroy}         blueprint command
          -d, --dry-run                                       dry run the command, to preview outcome
          -b BP_FILE, --bp-file BP_FILE                       input blueprint configuration yaml file
          -i INPUT_FILE, --input-file INPUT_FILE              input blueprint data file
          -s SOURCE_DIR, --source-dir SOURCE_DIR              source directory for blueprint and input data files
          -w WORKING_DIR, --working-dir WORKING_DIR           working directory for intermediate files
          -o OUT_FILE, --out-file OUT_FILE                    output blueprint file
          -l LOG_FILE, --log-file LOG_FILE                    log file
          -e {DEBUG,INFO,WARNING,ERROR}, 
              --log-level {DEBUG,INFO,WARNING,ERROR}          log level

Refer to examples in the `examples/run` folder.

### Blueprint Python library usage

  Use the `blueprint Python library` to assemble the blueprint configuration file - using Python.

  The library includes the following schema elements, that can be used to define your blueprint manifest
  * schema.blueprint.Blueprint
  * schema.module.Module
  * schema.source.TemplateSource
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
  | 1 | Schema validator    | `./examples/validate/validate_app.py` | Illustrate the use of the `blueprint.schema.validate.validator.Validator` class to validate a blueprint configuration file.|
  | 2 | Schema draw         | `./examples/draw/draw_app.py` | Illustrate the use of the `blueprint.circuit.draw.BlueprintDraw` class to draw a graph depicting the blueprint configuration file.|
  | 3 | Schema merge        | `./examples/validate/merge_app.py` | Illustrate the use of `blueprint.merge.manifest.BlueprintManifest` class to load manifest file, to generate a blueprint configuration file. </br> The `./examples/validate/data-1/manifest.yaml` & `./examples/validate/data-2/manifest.yaml` are sample blueprint manifest file. |
  | 4 | Schema sync         | `./examples/sync/sync_app.py` | Illustrate the ability to sync the module definitions (inputs & outputs) in the blueprint configuration file, with the corresponding definition the Terraform repository. |
  | 5 | Schema generate     | `./examples/generate/bp_basic.py` | Illustrate the use of `blueprint.schema` & `blueprint.circuit` library classes to generate a blueprint configuation file, using Python code |
  | 6 | Blueprint run       | `./examples/run/run_app.py` | Illustrate the ability to run & verify the blueprint behaviour locally. |

---
## Future roadmap

  The roadmap for this tootset include the following:
  - blueprint-gen: Support to generate blueprint configuration file from a simple bill-of-material
  - blueprint-draw: Support to draw & visualize the blueprint configuration file
  - and more.. 

---

## Contact

  Contact the author(s) of the tool:

  - Albee Jhoney (albee.jhoney@in.ibm.com)
  - Nishu Bharti (nishu.bharti1@ibm.com)

---

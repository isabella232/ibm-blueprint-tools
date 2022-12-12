## How to ...


### Terminologies

| Term         | Description |
|--------------|-------------|
| **Blueprint**    |  Automate the deployment of large & complex cloud environment - comprising of multiple reusable Terraform automation code.  This builds on the IaC best practice of modular architectures. It scales the Terraform deployment model, connecting modular environments, as the layers and components of large infrastructure architectures. |
| **Blueprint configuration file** | An YAML file describing the inputs, outputs, and the assembly of modules. | 
| **Blueprint manifest file**| An YAML file with hyperlinks to multiple smaller YAML file snippets that describe the inputs, outputs, modules, etc.  It can be used to generate a larger `Blueprint configuration file` |
| **Blueprint lite file** | An YAML file that may have partial input / output definition. It can be sync'd with the corresponding input/output definition of the Terraform modules, in the Git repository |

---

### How to validate your `blueprint configuration file` ?

You can use the following CLI to validate the `blueprint configuration file`. 

> blueprint validate [-h] -b BP_FILE [-w WORKING_DIR]

It performs two levels of validation
1. YAML Schema validation - to verify whether your blueprint yaml file, is compliant to the prescribed schema
2. Advanced semantic validation - to verify whether the input / output variable definitions are used correctly, are they linked properly, etc.

The result of validation can be obtained in tabular or json format.

In addition, you can progamatically validate your `blueprint configuration file` using the following Python modules.
* blueprint.validate.schema_validator.SchemaValidator
* blueprint.validate.blueprint_validator.BlueprintValidator

As illustrated in the followint code snippet:

```python
    input_file = 'blueprint.yaml' 

    # Perform Blueprint schema validation               #
    ##=================================================##
    bsv = schema_validator.SchemaValidator(input_file)
    (msg, err) = bsv.validate()
    if err != None:
        eprint(err)
    
    # Load Blueprint yaml file, for advanced validation #
    ##=================================================##
    bp = bfile.FileHelper.load_blueprint(input_file)
    if bp == None:
        eprint("Error in loading the blueprint file")

    # Perform advanced semantic validation of Blueprint #
    ##=================================================##
    bpv = blueprint_validator.BlueprintValidator()
    err = bpv.validate_blueprint(bp)
    if err != None:
        eprint(event.format_events(err, event.Format.Table))

```

---

### How to generate `blueprint configuration file` from a `manifest file` ?

When you try to codify the automation for a large cloud environment in a `blueprint configuration file`, comprising of multiple modules, inputs & outputd sections - it can soon become very large and complex to manage.  The `blueprint manifest file` aims to simplify this experience using a simple easily consumable format, such as the following:

```yaml
name: "SAP on secure Power Virtual Servers"
schema_version: "1.0.0"
description: "Solution to deploy SAP on secure Power Virtual Servers"
type: "blueprint"
inputs:
  - name: test_ibmcloud_api_key
    type: string
    sensitive: true
    required: true
  - ${{inputs-creds.yaml}}
  - ${{./inputs-resource-meta.yaml}}
outputs:
  - ${{outputs-bp.yaml}}
modules:
  - ${{./mod-secure-infrastructure.yaml}}
  - ${{./mod-power-infrastructure.yaml}}
  - ${{./mod-sap-secure-powervs.yaml}}
```

In the above example, the `inputs-resource-meta.yaml` will be a separate yaml file, with the following content:

```yaml
inputs:
  - name: prefix
    default: secure-vpc
    description: A unique identifier for resources
    type: string
    optional: true
  - name: powervs_zone
    description: powervs zone
    type: string
    default: eu-de-1
    required: true
  - name: powervs_resource_group_name
    description: powervs resource group name
    type: string
    default: Default
    required: true
  - name: region
    default: us-east
    type: string
    description: Region where vpc will be created
    optional: true
```

You can use the `blueprint merge` command to expand the manifest file into a complete `blueprint configuration file`, on demand.  This can easily simplify the task of managing a large blueprint configuration file - by dividing them into smaller parts, and work with them independently.

> blueprint merge [-h] -m MANIFEST_FILE [-w WORKING_DIR] [-o OUT_FILE]

**Next step:**
* You can use the `blueprint validate` tool to validate the blueprint yaml file.
* You can use the `blueprint draw` tool to visualize the connections - as you edit / update the blueprint yaml file.

---

### How to prepare a `blueprint configuration file` using terraform modules sourced from git repositories ?

When you wish to prepare a `blueprint configuation file` from scratch, you will start with the Terraform modules.  You must analyze the Terraform modules to understand the input & output definitions.  Further, you must accurately transcribe these input / output variable names, type & description to the new blueprint yaml file.

What-if, you have a tool that can reads the terraform modules from the git repository, identifies the inputs & output variables and generate a skeleton blueprint configuration file, from the following blueprint lite file:
```yaml
name: "Blueprint Basic Example"
type: "blueprint"
schema_version: "1.0.0"
description: "Simple blueprint to demonstrate module linking"
git_sources:
  - git_repo_url: "https://github.com/albee-jhoney/test-tf/tree/main/cloudless"
    git_branch: main
  - git_repo_url: "https://github.com/albee-jhoney/test-tf/tree/main/local-file"
    git_branch: main
  - git_repo_url: "https://github.com/albee-jhoney/test-tf/tree/main/medium"
    git_branch: main
  - git_repo_url: "https://github.com/albee-jhoney/test-tf/tree/main/rg-tf"
    git_branch: main
  - git_repo_url: "https://github.com/albee-jhoney/test-tf/tree/main/simple"
    git_branch: main
```

Try the following `blueprint sync` command:

> blueprint sync [-h] -b BP_FILE [-s SOURCE_DIR] -o OUT_FILE -w WORKING_DIR 

The output yaml file will be prefilled with all the modules, its inputs & outputs.  You can review the content, and start wiring the output & input variables.  This tool WILL NOT do the following:
* Add input/output variables, at the blueprint level
* Add `value` to the input variables
* Add `type` to the input / output variables
* Automatically wire or connect the values of the input / output variables

**Next step:**
* You can use the `blueprint draw` tool to visualize the connections - as you edit / update the blueprint yaml file.
* You can use the `blueprint validate` tool to validate the blueprint yaml file.

---

### How to sync the input/output definitions in the `blueprint configuration file` with the corresponding vars/outputs of the terraform modules in git repositories ?

In the lifecycle of `blueprint configuration file`, the input/output definitions of the Terraform modules can go out of sync.  In other words, the Terraform module developer may change the inputs variable names, add a new output variable, or change the variable type, etc.  

The following tool can help you to sync the blueprint definition.

> blueprint sync [-h] -b BP_FILE [-s SOURCE_DIR] -o OUT_FILE -w WORKING_DIR 

The output file will have annotation to add, delete or update the input / output variables used in the module definitions.

---

### How to codify a `blueprint configuration file` in Python ?

*Docs: Work in progress*

---

### How to run the  `blueprint configuration file` using the local Terraform CLI ?

*Docs: Work in progress*

---

### How to dry-run the `blueprint configuration file` using the local Terraform CLI ?

*Docs: Work in progress*

---

### How to visualize the `blueprint configuration file` ?

*Docs: Work in progress*

---
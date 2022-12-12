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

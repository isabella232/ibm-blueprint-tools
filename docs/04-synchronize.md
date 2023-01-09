## 3. Start developing a `blueprint configuration file` using terraform modules, sourced from Git repositories

When you wish to prepare a new `blueprint configuation file` from scratch, you will start with the Terraform modules in the Git repositories or Hashicorp Registry. You must analyze the Terraform modules to understand the input and output definitions. Further, you must accurately transcribe these input and output variable names, type, and description to the new blueprint configuration file. It can be error prone.

What if, you have a tool that reads the Terraform modules from the Git repository that identifies the inputs and outputs variables, and generate a *starter* blueprint configuration file, from the following `blueprint lite file`:

```yaml
name: "Blueprint Basic Example"
type: "blueprint"
schema_version: "1.0.0"
description: "Simple blueprint configuration file"
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

Run the following `blueprint sync` command:

> blueprint sync [-h] -b BP_FILE [-s SOURCE_DIR] -o OUT_FILE -w WORKING_DIR 

The output yaml file will be prefilled with all the modules, its inputs and outputs. It is a good starting point for you to further develop the blueprint configuration. You can review the content, and start connecting the output and input variables.

The pre-requisite for the `blueprint sync` tool is [terraform-config-inspect](https://github.com/ibm-cloud/terraform-config-inspect) tool. The working directory `WORKING_DIR` is used by the `terraform-config-inspect` tool to process Terraform modules that is downloaded from the Git repositories.

NOTE: This tool WILL NOT do the following:
* Add blueprint level input or output variables (only at the module-level).
* Add `value` or `type` to the input or output variables.
* Automatically wire or connect the values of the input or output variables.

---

## 4. Incrementally add Terraform modules to the `blueprint configuration file` and synchronize

Typically, the blueprint configuration file is developed incrementally. In every step, the *blueprint developer* adds a new layer or a set of Terraform modules to validate the updated blueprint configuration. While adding a new Terraform module, the *blueprint developer* needs assistance to fetch the input or output definitions of the newly added modules in the `blueprint configuration`.

You can update the `blueprint configuration file` with the `source` snippet for the new module for example, `mod-4`.

```yaml
  - name: mod-4
    module_type: terraform
    source:
      source_type: github
      git:
        git_repo_url: "https://github.com/albee-jhoney/test-tf/tree/main/rg-tf"
        git_branch: main
```

After running the  `blueprint sync` command, the following output will be generated. Wherein the `mod-4` is expanded to add the input and output variables after introspecting the Terraform modules in the Git repository.

```yaml
- name: mod-4
  module_type: terraform
  source:
    source_type: github
    git:
      git_repo_url: https://github.com/albee-jhoney/test-tf/tree/main/rg-tf
      git_branch: main
  outputs:
  - name: resource_group_id
    type: string
    description: 'The ID of the resource group'
    # comment: 'TODO: add param'
  - name: resource_group_name
    type: string
    description: 'The Name of the resource group'
    # comment: 'TODO: add param'
```

You can notice a `# comment:` field annotated with `TODO: add param`, denoting the addition of the new input and output variable.

The next step for the _blueprint developer_ is to review all the annotations, and update the values for these input and output variables in the new module.

---

## 5. Synchronize the `blueprint configuration file` with the terraform modules in the Git repositories

During the course of Continuous Integration and Continuous Development (CI/CD) of the `Terraform modules` and the `blueprint configuration`. It is possible for the input or output definitions of the modules in `blueprint configuration` to be out-of-sync with the corresponding definitions in the Terraform modules. In other words, the *Terraform module developer* may change the inputs variable names, add a new output variable, or change the variable type, etc., while the *Blueprint developer* is not aware of the latest changes.

With a large `blueprint configuration` (spanning 1000's of lines), it would be difficult to manually find the differences, and update the module definitions.

You can use the `blueprint sync` tool to find the differences and fix them.

Use the current version of the `blueprint configuration file` as an input, to run the tool. The output file will have the annotation to add, delete or update the input or output variables used in the module definitions. A `comment` is added to the input or output variable, with the following annotation:
* `TODO: add param`: To add this new input or output variable in the blueprint module. (Reason: Found this new variable in the Terraform module source code)
* `TODO: delete param`: To remove this input or output variable from the blueprint module. (Reason: This variable was not found in the Terraform module source code)
* `TODO: update param`: To update the definition of input or output variable in the blueprint module. (Reason: This variable type, default value or description was changed in the Terraform module source code)

---

### Next steps

After generating the starter blueprint configuration file (or an annotated blueprint configuration file), from the input blueprint lite file, you can do the following
* [Visualize the blueprint configuration](./07-visualize.md) to visually inspect the new modules in the blueprint; and the related annotations.
* Incrementally modify the blueprint yaml file, [visualize the changes](./07-visualize.md), and [validate the blueprint configuration](./02-validate.md).
* [Dry-run the modified blueprint configuration](./06-run.md) to verify the data-flow with mock data.

---

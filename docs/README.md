# User guides


## Terminologies

| Term         | Description |
|--------------|-------------|
| **Blueprint**    |  Automate the deployment of large and complex cloud environment consists of multiple reusable Terraform automation codes. The code builds on the IaC best practice of modular architectures. It scales the Terraform deployment model, connecting modular environments, as the layers and components of large infrastructure architectures. |
| **Blueprint configuration file** | A YAML file describes the inputs, outputs, and the assembly of Terraform modules - in a blueprint. |
| **Blueprint manifest file**| A YAML file containing hyperlinks to multiple smaller YAML file snippets that describe the blueprint inputs, outputs, and modules. It can be assembled into a larger `Blueprint configuration file` |
| **Blueprint lite file** | A YAML file with partial or incomplete blueprint definition. It contains the information about the Terraform modules that is needed to fetch the relevant input and output definition (of the Terraform modules from the Git repository) while reconstructing a complete blueprint configuration file. |
{: caption="Terminologies" caption-side="bottom"}

---
---

## Scenarios

| Sl | Scenario  | How to... |
|----|-----------|-----------|
| 1  | I hand-coded a blueprint configuration file. </br> * Can it be validated for its correctness and completeness or syntax and semantics?  | For more information, see [validate blueprint](./02-validate.md). </br>How to validate the `blueprint configuration file`?  |
|    |           |           |
| 2  | I have a large cloud environment, with multiple Terraform modules and complex input schema. It runs into 1000+ lines of `yaml` file. I find it difficult to edit, and update a single large blueprint configuration file.</br> * Can I break the blueprint `yaml` file into multiple parts, and work with them independently? </br> * Can I combine the parts such as validate, and visualize the resulting blueprint a `yaml` file? | Use the manifest file, and use [blueprint merge](./03-manifest.md) tool to combine multiple parts of a blueprint `yaml` file. </br>You can try the `blueprint validate`, and `blueprint draw` commands to validate, and visualize the resulting blueprint `yaml` file` |
|    |           |           |
| 3  | I am preparing a blueprint configuration file from scratch. It is exhausting! I must refer to multiple Terraform modules, find the input and output variables of each module, and transcribe them into the blueprint file.</br> * Can I automatically generate a starter blueprint `yaml` file, from a collection of Git repository URLs (for Terraform modules). | See the [blueprint sync](./04-synchronize.md) tool to learn how to generate a `starter blueprint configutation` from a simple collection of Git repository URLs (`blueprint lite file`). |
|    |           |           |
| 4  | I want to incrementally add more layers or Terraform modules to an existing blueprint configuration file. </br> * Can I extend the blueprint configuration with Git repository details, and get assistance with the input and output variables for the newly added module? | The [blueprint sync](./04-synchronize.md) tool can assist you to incrementally add new Terraform modules to an existing `blueprint configutation`.|
|    |           |           |
| 5  | My blueprint configuration file is not synchronized with the current version of Terraform modules. I want to know the differences between the input and output configuration of the Terraform module (in the Git repository) and the corresponding entries in the blueprint configuration file. | Use the [blueprint sync](./04-synchronize.md) tool to find the difference and synchronize the module configuration definitions in the blueprint yaml file. |
|    |           |            |
| 6  | I am familiar with Python, and I want to program the IBM Cloud by using Python, Blueprint, and Terraform. </br> * Can I generate the blueprint configuration file by using reusable Python modules? </br> * Can I run the blueprint commands locally (such as init, plan, apply, and destroy action) by using the local Terraform CLI? | Refer to the [blueprint program](./05-program.md) tool to learn about how to program the Cloud by using Python and blueprint. </br>Further, refer to the code snippets in the [blueprint run](./06-run.md) tool to run the `blueprint init`, `blueprint plan`, `blueprint apply`, and `blueprint destroy` commands. |
|    |           |            |
| 7  | It takes numerous effort and time to test the blueprint configuration file with IBM Cloud Schematics.</br> * Can the development cycle time be reduced by running a `dry-run` of the blueprint configuration file? </br> * Can I use the local version of Terraform CLI to test the blueprint yaml, instead of using IBM Cloud Schematics? | Use the `blueprint run` tool to dry run and run the blueprint configuration file by using the local Terraform CLI. |
|    |           |            |
| 8  | My blueprint configuration file has multiple modules, and many dependencies between the module input and output variables. If the blueprint configuration file contains large (500+ lines), it is difficult to understand the dependencies between the modules.</br> * Can I visualize the dependencies between the modules, using a graph or network diagram? </br> * Can I see that the validation errors be annotated on the network diagram, for a quick visual analysis? | Refer to the [blueprint draw](./07-visualize.md) tool description to understand the different ways to display the blueprint configuration file. |
{: caption="Scenarios" caption-side="bottom"}

---

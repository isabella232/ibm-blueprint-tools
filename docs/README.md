# How to ...


## Terminologies

| Term         | Description |
|--------------|-------------|
| **Blueprint**    |  Automate the deployment of large & complex cloud environment - comprising of multiple reusable Terraform automation code.  This builds on the IaC best practice of modular architectures. It scales the Terraform deployment model, connecting modular environments, as the layers and components of large infrastructure architectures. |
| **Blueprint configuration file** | An YAML file describing the inputs, outputs, and the assembly of modules. | 
| **Blueprint manifest file**| An YAML file with hyperlinks to multiple smaller YAML file snippets that describe the inputs, outputs, modules, etc.  It can be used to generate a larger `Blueprint configuration file` |
| **Blueprint lite file** | An YAML file that may have partial input / output definition. It can be sync'd with the corresponding input/output definition of the Terraform modules, in the Git repository |

---

## Scenarios

| Sl | Scenario  | How to... |
|----|-----------|-----------|
| 1  | I have hand-coded a blueprint configuration file.  </br> * Can it be validated for its correctness and completeness (syntax and semantics) ?  | Refer to - [validate blueprint](./02-validate.md) </br>How to validate my `blueprint configuration file` ?  |
|    |           |           |
| 2  | My python code generates a blueprint configuration file.  </br> * Can I validate the schema for its correctness and completeness, before generating the final blueprint yaml file ? | Refer to the code snippet in '[validate blueprint](./02-validate.md)'. |
|    |           |           |
| 3  | I have a very large cloud environment, with multiple terraform modules and complex input schema. It runs into 1000+ lines of yaml file.   I find it difficult to edit & update a single large blueprint configuration file. </br> * Can I break the blueprint yaml file into multiple parts, and work with them independently ? </br> * Can I combine the parts - validate, and visualize the resulting blueprint yaml file ? | Use the manifest file, and use [blueprint merge](./03-manifest.md) tool to combine multiple parts of a bluepring yaml file. </br>You can also try the `blueprint validate` & `blueprint draw` commands to validate & visualize the resulting blueprint yaml file |
|    |           |           |
| 4  | I am preparing a blueprint configuration file from scratch.  It is exhausting! I have to refer to multiple Terraform modules, find the input & output variables of each module, and transcode them into my blueprint file. </br> * Can I automatically generate a starter blueprint yaml file, from a collection of Git repo URLs pointing to the Terraform modules. | Refer to the [blueprint sync](./04-synchronize.md) tool to learn how to generate a `starter blueprint file` from a simple collection of Git repo URLs. |
|    |           |           |
| 5  | My blueprint configuration file is not sync with the current version of Terraform modules.  I want to know the differences between the input/output configuration of the Terraform module (in the Git repo) and the corresponding entries in the blueprint configuration file. | Use the [blueprint sync](./04-synchronize.md) tool to find the difference and sync the module configuration definitions in the blueprint yaml file. |
|    |           |            |
| 6  | I am familiar with Python, and I want to program the IBM Cloud using Python, Blueprint and Terraform.  </br> * Can I generate the blueprint configuration file using reusable Python modules ? </br> * Can I run the blueprint commands locally (such as, init, plan, apply & destroy action) - using the local Terraform CLI ? | Refer to the [blueprint program](./05-program.md) tool to learn about - how to program the Cloud iusing Python and Blueprint.  </br>Further, refer to the code snippets in the [blueprint run](./06-run.md) tool to run the `blueprint init`, `blueprint plan`, `blueprint apply` & `blueprint destroy` commands. |
|    |           |            |
| 7  | It takes a lot of effort and time, to test the blueprint configuration file with IBM Cloud Schematics.  </br> * Can the development cycle time be reduced by performing a `dry-run` of the blueprint configuration file ? </br> * Can I use the local version of Terraform CLI to test the blueprint yaml, instead of using IBM Cloud Schematics ? | Use the `blueprint run` tool to dry-run & run the blueprint configuration file, using the local Terraform CLI |
|    |           |            |
| 8  | My blueprint configuration file has multiple modules, and there are several dependencies between the module input and output variables.  Since, my blueprint configuration file is very large (500+ lines), it is very difficult to understand the dependencies between them.  </br> * Can I visualize the dependencies between the modules, using a graph / network diagram ? </br> * Can I see the validation errors be annotated on the network diagram, for a quick visual analysis ? | Refer to the [blueprint draw](./07-visualize.md) tool description, to understand the differen ways of displaying the blueprint configuration file. |


---


## 7. How to run or dry-run the `blueprint configuration file` in the local Terraform CLI?

When developing the `blueprint configuration`, you might want to incrementally verify the content by running the blueprint commands. The blueprint command has a direct impact on the overall development cycle time and effort that is invested by the _blueprint developer_.

In addition, the _blueprint developer_ wants to diagnose all the issues in the blueprint configuration file before pushing or committing the IaC code to a Git repository. The moving parts such as blueprint configurations, Terraform modules, and the data-flows between them, it is important to be able to test the IaC code. In addition, such incremental development and testing cycles must not incur cost of the Cloud resources.

You can use the following CLI to run the `blueprint configuration file`.

> blueprint run [-h] -c {init,plan,apply,destroy,output} [-d] -b BP_FILE -i INPUT_FILE [-s SOURCE_DIR] [-w WORKING_DIR] [-o OUT_FILE]
                      [-l LOG_FILE] [-e {DEBUG,INFO,WARNING,ERROR}]

It runs the blueprint in two modes 
1. `dry-run` mode (uses -d option) - to dynamically generate multiple mock Terraform module and mock data - that can be used to verify the data-flows between the Terraform modules (as described in the blueprint configuration)
2. `run` mode - to download the Terraform modules in the local file system, and run the Terraform CLI commands in the local machine.

The prerequisite to run the Blueprint in your local machine
* [Terraform CLI (version 1.0 or higher)](https://cloud.ibm.com/docs/ibm-cloud-provider-for-terraform?topic=ibm-cloud-provider-for-terraform-setup_cli)
* Setup the environment variables with your API Keys (as needed by the respective Terraform providers)

The `BlueprintRunner` uses the `working_dir` to create multiple folders (one each for the modules in the blueprint configuration file). Further, it downloads the Terraform modules from the source (Git repositories), and prepares itself to run the Terraform command.

> When you choose to `dry_run` the blueprint module, the Terraform modules are not downloaded from the Git repositories, instead - the input or output configurations in the blueprint is used to automatically generate a set of Terraform module (with the `vars.tf` and `output.tf` along with a dummy null_resource), and are placed in the `working_dir`\folders. You can customize the values in the input or output variables to simulate data-flows between the modules in the blueprint configuration. It can be used for dynamic analysis of the blueprint configuration.

You can run the following commands
* `blueprint init`
* `blueprint plan`
* `blueprint apply`
* `blueprint destroy`

When you run these commands, the in-built orchestrator switches to the respective module-specific folders, and run the corresponding Terraform CLI command. The outputs that are produced by the Terraform Apply commands are chained (or fed as input) to the down-stream Terraform module by the orchestrator.

---
### Next steps

You can follow onboarding after running your blueprint configuration.
* (Optionally) Onboard the blueprint configuration to the IBM Cloud Schematics, to [run the blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-create-blueprint-config&interface=ui) remotely.

---


## 7. How to run / dry-run the  `blueprint configuration file` using the local Terraform CLI ?

While developing the `blueprint configuration`, you may want to incrementally verify the content - by running the blueprint commands.  These has a direct impact on the overall development cycle - time & effort invested by the _blueprint developer_.   

In addition, the _blueprint developer_ wants to diagnose all the issues in the blueprint configuration file, before pushing / committing the IaC code to a Git repository.  Since, there are several moving parts - such as blueprint configurations, terraform modules, and the data-flows between them,  it is important to be able to test the IaC code.  In addition, such incremental dev-test cycles must not incur cost of Cloud resources.

You can use the following CLI to run the `blueprint configuration file`. 

> blueprint run [-h] -c {init,plan,apply,destroy,output} [-d] -b BP_FILE -i INPUT_FILE [-s SOURCE_DIR] [-w WORKING_DIR] [-o OUT_FILE]
                      [-l LOG_FILE] [-e {DEBUG,INFO,WARNING,ERROR}]

It run the blueprint in 2 modes 
1. `dry-run` mode (using -d option) - to dynamically generate multiple mock Terraform module & mock data - that can be used to verify the data-flows between the Terraform modules (as described in the blueprint configuration)
2. `run` mode - to download the Terraform modules in the local filesystem, and run the Terraform CLI commands in the local machine.

The pre-requisite to run the Blueprint in your local machine 
* Terraform CLI (version 1.0 or higher)
* Setup the environment variables with your API Keys (as required by the respective Terraform providers)

The Blueprint Runner will use the `working_dir` to create multiple folders (one each for the modules in the Blueprint configuration file).  Further, it will download the Terraform modules from the source (Git repositories), and prepare itself to run the terraform command.

> When you choose to `dry_run` the Blueprint module, the Terraform modules are not downloaded from the Git repositories, instead - the input/output configurations in the blueprint is used to automatically generate a set of Terraform module (with the vars.tf & output.tf along with a dummy null_resource), and are placed in the `working_dir`\folders.  The values in the input/output variables can be customized to simulate data-flows between the modules in the Blueprint configuration.  It can be used for dynamic analysis of the Blueprint configuration.

You can run the following commands
* `blueprint init`
* `blueprint plan`
* `blueprint apply` 
* `blueprint destroy`

When you run these commands, the in-built orchestrator will switch to the respective module specific folders, and run the corresponding Terraform CLI command.   The outputs produced by the Terraform Apply commands are chained (or fed as input) to the down-stream terraform module - by the orchestrator .

---
### Next steps

After running your blueprint configuration, you can do the following:
* (Optionally) Onboard the blueprint configuration to IBM Cloud Schematics, to [run the blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-create-blueprint-config&interface=ui) remotely.

---

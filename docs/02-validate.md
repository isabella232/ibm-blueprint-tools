## 1. How to validate the `blueprint configuration file` ?

You can use the following CLI to validate the `blueprint configuration file`. 

> blueprint validate [-h] -b BP_FILE [-w WORKING_DIR]

It performs two levels of validation
1. YAML Schema validation - to verify whether your blueprint yaml file, is compliant to the prescribed schema
2. Advanced semantic validation - to verify whether the input / output variable definitions are used correctly, are they linked properly, etc.

The result of validation can be obtained in tabular or json format.

---
### List of advanced validation

| Sl | Validation message | Description & remmediation |
|----|--------------------|----------------------------|
| 1 | Unused input parameters declared in the blueprint | Blueprint input variable (in the `inputs` section) is not being used by any module.  </br>Review the linked-data references (eg. $blueprint.inputs.vpc_zone) in all the modules, to ensure that it is being named & used correctly. | 
| 2 | Undeclared blueprint parameters used by modules | A module is referring to an input variable that has not been declared in the `inputs` section of the blueprint. </br>Review the linked-data reference in the specified module (eg. $blueprint.inputs.vpc_zone), for any spelling mistakes or capitalization. |
| 3 | Undeclared output parameters used by modules | A module is referring to an output variable that has not been declared in the `outputs` section of another module. </br>Review the linked-data reference in the specified module (eg. $modules.mod_name.outputs.vpc_zone), for any spelling mistakes or capitalization. |
| 4 | Unused output parameters declared in the modules | A module has declared an output variable, that is not be used (or referred to) by other modules or the outputs of the blueprint.  </br>Review the linked-data references (eg. $modules.mod_name.outputs.vpc_zone) in all the modules and blueprint outputs, to ensure that it is being named & used correctly. |
| 5 | Blueprint output parameters is left hanging | The output variable that is declared in the `outputs` section of the blueprint - does not have a valid linked-data reference, to the outputs produced by a module in the blueprint. </br>Ensure that all the blueprint outputs have cross-references (or links) to the correct module output variable.|
| 6 | Found circular dependencies between modules | The links between the input and output variables in all the modules has resulted in a circular dependency.  For example, m1->m2->m3->m1.  </br>Review all the links between the input & output variables, to ensure that there is no circular dependencies between the modules. |


---
### Programmatic blueprint validation

In addition, you can progamatically validate your `blueprint configuration file` using the following Python modules.
* blueprint.validate.schema_validator.SchemaValidator
* blueprint.validate.blueprint_validator.BlueprintValidator

As illustrated in the following code snippet:

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
### Next steps

After validating your blueprint configuration (static analysis), you can do the following:
* [Visualize the blueprint configuration](./07-visualize.md), to visually inspect the connections between blueprint & modules, between modules & modules.
* [Dry-run the blueprint configuration](./06-run.md), to verify a mock data-flow (for dynamic analysis)
* (Optionally) [Run the blueprint configuration](./06-run.md) locally, using the local copy of the Terraform CLI.  
  > Warning Note: This step will incur cost of provisioning Cloud resource)
* (Optionally) Onboard the blueprint configuration to IBM Cloud Schematics, to [run the blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-create-blueprint-config&interface=ui) remotely.

---

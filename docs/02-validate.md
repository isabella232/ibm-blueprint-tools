## 1. How to validate the `blueprint configuration file` ?

You can use the following CLI to validate the `blueprint configuration file`. 

> blueprint validate [-h] -b BP_FILE [-w WORKING_DIR]

It performs two levels of validation
1. YAML Schema validation - to verify whether your blueprint yaml file, is compliant to the prescribed schema
2. Advanced semantic validation - to verify whether the input / output variable definitions are used correctly, are they linked properly, etc.

The result of validation can be obtained in tabular or json format.

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

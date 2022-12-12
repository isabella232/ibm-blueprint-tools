### How to validate the `blueprint configuration file` ?

You can use the following CLI to validate the `blueprint configuration file`. 

> blueprint validate [-h] -b BP_FILE [-w WORKING_DIR]

It performs two levels of validation
1. YAML Schema validation - to verify whether your blueprint yaml file, is compliant to the prescribed schema
2. Advanced semantic validation - to verify whether the input / output variable definitions are used correctly, are they linked properly, etc.

The result of validation can be obtained in tabular or json format.

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

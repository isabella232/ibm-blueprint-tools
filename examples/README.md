
## Examples

  |   | Example             | Folder     | Description           |
  |---|---------------------|------------|-----------------------|
  | 1 | Schema validator    | `./examples/validate/app.py` | The `validate/app.py` illustrate the use of the `blueprint.schema.validate.validator.Validator` class to validate a blueprint configuration file.|
  | 2 | Schema merge        | `./examples/validate/app.py` | The `merge/app.py` illustrate the use of `blueprint.merge.load.BPLoader` class to load manifest file, to generate a blueprint configuration file. </br> The `./examples/validate/data-1/manifest.yaml` & `./examples/validate/data-2/manifest.yaml` are sample blueprint manifest file. |
  | 3 | Schema generate     | `./examples/generate/bp_basic.py` </br></br> `./examples/generate/app.py` | The `generate/bp_basic.py` illustrate the use of `blueprint.schema` & `blueprint.circuit` library classes to generate a blueprint configuation file, using Python code. </br></br>  The `generate/app.py` illustrate the use of the following library functions: </br> * `validate()` blueprint configuration file </br> * write blueprint configuration file using `to_yaml_str()` </br> * read blueprint configuration file using`from_yaml_str()` </br> * to generate a dummy `input-file.yaml` for the blueprint configuration using `generate_input_file()`|
  | 4 | Blueprint run       | `./examples/run/app.py` | The `run/app.py` illustrate the ability to run & verify the blueprint behaviour locally. |
  
---
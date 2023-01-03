
## Examples

  |   | Example             | Folder     | Description           |
  |---|---------------------|------------|-----------------------|
  | 1 | Schema validator    | `./examples/validate/validate_app.py` | Illustrates the use of the `blueprint.schema.validate.validator.Validator` class to validate a blueprint configuration file.|
  | 2 | Schema draw         | `./examples/draw/draw_app.py` | Illustrates the use of the `blueprint.circuit.draw.BlueprintDraw` class to draw a graph depicting the blueprint configuration file.|
  | 3 | Schema merge        | `./examples/validate/merge_app.py` | Illustrate the use of `blueprint.merge.manifest.BlueprintManifest` class to load manifest file to generate a blueprint configuration file.</br> The `./examples/validate/data-1/manifest.yaml` & `./examples/validate/data-2/manifest.yaml` are sample blueprint manifest file. |
  | 4 | Schema sync         | `./examples/sync/sync_app.py` | Illustrate the ability to sync the module definitions (inputs and outputs) in the blueprint configuration file, with the corresponding definition the Terraform repository. |
  | 5 | Schema generates     | `./examples/generate/bp_basic.py` | Illustrate the use of `blueprint.schema` and `blueprint.circuit` library classes to generate a blueprint configuration file, by using Python code |
  | 6 | Blueprint run       | `./examples/run/run_app.py` | Illustrate the ability to run and verify the blueprint behavior locally.|
  {: caption="Examples" caption-side="bottom"}

---
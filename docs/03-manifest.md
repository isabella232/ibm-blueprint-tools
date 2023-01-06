## 2. How to generate `blueprint configuration file` from a `manifest file` ?

When you try to codify the automation for a large cloud environment in a `blueprint configuration file`, comprising of multiple modules, inputs & output sections - it can soon become very large and complex to manage.  

The `blueprint manifest file` aims to simplify this experience, using a simple and easily consumable format, such as the following:

```yaml
name: "SAP on secure Power Virtual Servers"
schema_version: "1.0.0"
description: "Solution to deploy SAP on secure Power Virtual Servers"
type: "blueprint"
inputs:
  - name: test_ibmcloud_api_key
    type: string
    sensitive: true
    required: true
  - ${{inputs-creds.yaml}}
  - ${{./inputs-resource-meta.yaml}}
outputs:
  - ${{outputs-bp.yaml}}
modules:
  - ${{./mod-secure-infrastructure.yaml}}
  - ${{./mod-power-infrastructure.yaml}}
  - ${{./mod-sap-secure-powervs.yaml}}
```

In the above example, the `inputs-resource-meta.yaml` would be a separate yaml file, with the following content:

```yaml
inputs:
  - name: prefix
    default: secure-vpc
    description: A unique identifier for resources
    type: string
    optional: true
  - name: powervs_zone
    description: powervs zone
    type: string
    default: eu-de-1
    required: true
  - name: powervs_resource_group_name
    description: powervs resource group name
    type: string
    default: Default
    required: true
  - name: region
    default: us-east
    type: string
    description: Region where vpc will be created
    optional: true
```

Once you have the `blueprint manifest file`, you can use the `blueprint merge` tool to expand the manifest file into a complete `blueprint configuration file`, on demand.  

This can easily simplify the task of managing a large blueprint configuration file - by dividing them into smaller parts, and work with them independently.

> blueprint merge [-h] -m MANIFEST_FILE [-w WORKING_DIR] [-o OUT_FILE]

---
### Programmatic processing a manifest file

In addition, you can programmatically process your `blueprint manifest file` using the following Python modules.
* blueprint.merge.manifest.BlueprintManifest

As illustrated in the following code snippet:

```python
    input_manifest_file = 'manifest.yaml' 

    # Load the Blueprint manifest file                  #
    ##=================================================##
    bp_manifest = manifest.BlueprintManifest.from_yaml_file(input_manifest_file)

    # Generate Blueprint config from manifest file      #
    ##=================================================##
    (bp_config, errors) = bp_manifest.generate_blueprint()
    if len(errors) > 0:
      eprint(errors)

    # Serialize Blueprint configuration file to yaml    #
    ##=================================================##
    (out_yaml_str, errors) = bp_config.to_yaml_str()
    if len(errors) > 0:
      eprint(errors)

```

---
### Next steps

After generating the blueprint configuration file, from the input manifest file, you can do the following
* [Validate the blueprint configuration](./02-validate.md), to verify the correctness & completeness of the output blueprint configuration file.
* [Visualize the blueprint configuration](./07-visualize.md), to visually inspect the connections between blueprint & modules, between modules & modules.
* [Dry-run the blueprint configuration](./06-run.md), to verify a mock data-flow (for dynamic analysis)
* (Optionally) Onboard the blueprint configuration to IBM Cloud Schematics, to [run the blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-create-blueprint-config&interface=ui) remotely.

---

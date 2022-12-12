### How to generate `blueprint configuration file` from a `manifest file` ?

When you try to codify the automation for a large cloud environment in a `blueprint configuration file`, comprising of multiple modules, inputs & outputd sections - it can soon become very large and complex to manage.  The `blueprint manifest file` aims to simplify this experience using a simple easily consumable format, such as the following:

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

In the above example, the `inputs-resource-meta.yaml` will be a separate yaml file, with the following content:

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

You can use the `blueprint merge` command to expand the manifest file into a complete `blueprint configuration file`, on demand.  This can easily simplify the task of managing a large blueprint configuration file - by dividing them into smaller parts, and work with them independently.

> blueprint merge [-h] -m MANIFEST_FILE [-w WORKING_DIR] [-o OUT_FILE]

**Next step:**
* You can use the `blueprint validate` tool to validate the blueprint yaml file.
* You can use the `blueprint draw` tool to visualize the connections - as you edit / update the blueprint yaml file.

---

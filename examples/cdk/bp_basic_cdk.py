from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.schema import param
from blueprint.schema import source
from blueprint.circuit import bus

#======================================================================
def new_blueprint():
    bp = blueprint.Blueprint(
        name        = "Blueprint Basic Example",
        description = "Simple blueprint to demonstrate module linking",
    )

    bp_storage_name = param.Input(name = "bp_storage_name")
    bp_storage_plan = param.Input(name = "bp_storage_plan")
    bp_storage_id   = param.Output(name = "bp_storage_id")
    bp_tf_settings  = param.Setting(name = "TF_VERSION", value = "1.0")
    err = []
    err += bp.set_inputs([
            bp_storage_name,
            bp_storage_plan,
        ])

    err += bp.set_outputs([
            bp_storage_id
        ])

    err += bp.set_settings([
            bp_tf_settings
        ])
    
    return (bp, err)

#======================================================================

def new_cos_module():
    cos_mod = module.Module(
        name        = "basic-cos-storage", 
        type        = module.TerraformType
    )

    cos_instance_name      = param.Input(name = "cos_instance_name")
    cos_storage_plan       = param.Input(name = "cos_storage_plan")
    cos_single_site_loc    = param.Input(name = "cos_single_site_loc", value = "ams03")
    cos_resource_group_id  = param.Input(name = "resource_group_id")
    cos_id                 = param.Output(name = "cos_id")
    cos_crn                = param.Output(name = "cos_crn")

    storage_mod_source = source.TemplateSource(
                    type = "github", 
                    git = source.GitSource(
                        repo_url = "https://github.com/Cloud-Schematics/blueprint-example-modules/tree/main/IBM-Storage",
                        branch = "main"
                    )
                )
    err = []
    err += cos_mod.set_source(storage_mod_source)
    err += cos_mod.set_inputs([
                    cos_instance_name, 
                    cos_storage_plan, 
                    cos_single_site_loc, 
                    cos_resource_group_id, 
                ])
    err += cos_mod.set_outputs([
                    cos_id,
                    cos_crn
                ])

    return (cos_mod, err)
#======================================================================

def new_rg_module():
    rg_mod = module.Module(
        name        = "basic-resource-group", 
        type        = module.TerraformType
    )
    resource_group_name       = param.Output(name = "resource_group_name")
    resource_group_id         = param.Output(name = "resource_group_id")

    rg_mod_source = source.TemplateSource(
                    type = "github", 
                    git = source.GitSource(
                        repo_url = "https://github.com/Cloud-Schematics/blueprint-example-modules/tree/main/IBM-DefaultResourceGroup",
                        branch = "main"
                    )
                )
    err = []
    err += rg_mod.set_source(rg_mod_source)
    err += rg_mod.set_outputs([
                    resource_group_name,
                    resource_group_id
                ]
            )

    return (rg_mod, err)

#======================================================================

def blueprint_manifest():
    
    errors = []
    bp, err = new_blueprint()
    errors += err

    #----------------Modules--------------------
    cos_mod, err = new_cos_module()
    bp.add_module(cos_mod)
    errors += err

    rg_mod, err = new_rg_module()
    bp.add_module(rg_mod)
    errors += err
    #----------------Modules--------------------
    
    #-------------Wiring starts-----------------
    err = []
    bp_bus = bus.WireBus(bp, cos_mod)
    err += bp_bus.add_wire('bp_storage_name', 'cos_instance_name')
    err += bp_bus.add_wire('bp_storage_plan', 'cos_storage_plan')

    mod_bus = bus.WireBus(rg_mod, cos_mod)
    err += mod_bus.add_wire('resource_group_id', 'resource_group_id')

    bp_out_bus = bus.WireBus(cos_mod, bp)
    err += bp_out_bus.add_wire('cos_id', 'bp_storage_id')
    #-------------Wiring ends-----------------

    return bp, (errors + err)

#======================================================================

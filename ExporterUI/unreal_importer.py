import json
import os


class UnrealImporter:
    def __init__(self):
        self.import_destination = "/Game/ImportedAssets"

    def generate_import_script(self, fbx_path, json_path=None):
        asset_name = os.path.splitext(os.path.basename(fbx_path))[0]

        fbx_path_unix = fbx_path.replace('\\', '/')

        expected_polygons = None
        if json_path and os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    metadata = json.load(f)
                expected_polygons = metadata.get('geometry', {}).get('polygons')
            except:
                expected_polygons = None

        if expected_polygons:
            validation_code = f"""
print(f"Validating '{asset_name}'...")
asset_path = f"{{destination_path}}/{{asset_name}}"
loaded_asset = unreal.EditorAssetLibrary.load_asset(asset_path)
if loaded_asset and isinstance(loaded_asset, unreal.StaticMesh):
    tris = loaded_asset.get_num_triangles(0)
    expected = {expected_polygons}
    print(f"3ds Max Polys: {{expected}}")
    print(f"Unreal Polys:  {{tris}}")
    if tris == expected:
        print("SUCCESS: Geometry matches exactly.")
        unreal.log("VALIDATION PASSED")
    else:
        diff = abs(tris - expected)
        print(f"WARNING: Mismatch of {{diff}} polygons.")
        unreal.log_warning("VALIDATION FAILED")
else:
    unreal.log_error(f"Could not load asset at {{asset_path}} for validation")
"""
        else:
            validation_code = "print('No metadata found for validation.')"

        script = f"""
import unreal
import os

asset_name = "{asset_name}"
fbx_path = r"{fbx_path_unix}"
destination_path = "{self.import_destination}"

task = unreal.AssetImportTask()
task.filename = fbx_path
task.destination_path = destination_path
task.automated = True
task.replace_existing = True
task.save = True

options = unreal.FbxImportUI()
options.import_mesh = True
options.import_materials = True
options.import_textures = False
options.import_as_skeletal = False

sm_options = unreal.FbxStaticMeshImportData()
sm_options.combine_meshes = True
sm_options.auto_generate_collision = True
options.static_mesh_import_data = sm_options

task.options = options

print(f"Importing {{asset_name}}...")
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

{validation_code}
"""
        return script

    def save_import_script(self, fbx_path):
        json_path = fbx_path.replace('.fbx', '.json')
        script_content = self.generate_import_script(fbx_path, json_path)
        script_path = fbx_path.replace('.fbx', '_import.py')
        with open(script_path, 'w') as f:
            f.write(script_content)
        return script_path
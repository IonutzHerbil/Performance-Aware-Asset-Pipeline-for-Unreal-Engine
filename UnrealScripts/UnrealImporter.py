import json
import os
import unreal

print("=== ASSET PIPELINE IMPORTER ===")

def import_asset_with_metadata(fbx_path):    
    print(f"Looking for: {fbx_path}")
    
    if not os.path.exists(fbx_path):
        print(f"FBX file not found: {fbx_path}")
        return
    
    json_path = fbx_path.replace('.fbx', '.json')
    if not os.path.exists(json_path):
        print(f"No metadata found for {fbx_path}")
        return
    
    with open(json_path, 'r') as f:
        metadata = json.load(f)
    
    import_task = unreal.AssetImportTask()
    import_task.set_editor_property('automated', True)
    import_task.set_editor_property('destination_path', '/Game/ImportedAssets')
    import_task.set_editor_property('filename', fbx_path)
    import_task.set_editor_property('save', True)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])

    print("ASSET IMPORTED")
    print("==============")
    print(f"Asset: {metadata['asset']}")
    print(f"Polygons: {metadata['polygons']}")
    print(f"Complexity: {metadata['complexity']}")
    print(f"Est. Objects: {metadata['estimated_objects']}")

test_path = "D:/Puoli/An3 Sem1 - UL/Graphics/exports/test1_plus_json.fbx"
import_asset_with_metadata(test_path)
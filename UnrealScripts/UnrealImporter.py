import json
import os
import sys
import unreal #type:ignore

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Core import PerformanceMeasurer, ValidationEngine

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
    import_task.set_editor_property('replace_existing', True)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])

    print("ASSET IMPORTED")
    print("==============")
    print(f"Asset: {metadata['asset']}")
    print(f"Predicted Polygons: {metadata['polygons']}")
    print(f"Predicted Complexity: {metadata['complexity']}")
    print(f"Est. Objects: {metadata['estimated_objects']}")
    
    measurer = PerformanceMeasurer()
    validator = ValidationEngine()
    
    asset_name = os.path.splitext(os.path.basename(fbx_path))[0]
    asset_path = f"/Game/ImportedAssets/{asset_name}"
    
    actual_stats = measurer.measure_asset(asset_path)
    if actual_stats:
        results = validator.validate_predictions(metadata, actual_stats)
        
        print("\nVALIDATION RESULTS")
        print("==================")
        print(f"Actual Polygons: {actual_stats['triangles']}")
        print(f"Polygon Error: {results['poly_error']:.1f}%")
        print(f"Complexity - Predicted: {results['predicted_complexity']}, Actual: {results['actual_complexity']}")
        print(f"Memory Usage: {results['memory_mb']:.2f} MB")
        print(f"Accuracy Score: {results['accuracy_score']:.1f}%")
        
        if results['accuracy_score'] >= 85:
            print("VALIDATION PASSED!")
        else:
            print("VALIDATION FAILED!")

test_path = "D:/Puoli/An3 Sem1 - UL/Graphics/exports/test2FixSmoothingGroupsWarning.fbx"
import_asset_with_metadata(test_path)
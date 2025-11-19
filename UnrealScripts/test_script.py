import unreal #type:ignore

export_path = "D:/Puoli/An3 Sem1 - UL/Graphics/exports/"
files = ["test4_decimated.fbx", "test4_decimated_LOD1.fbx", "test4_decimated_LOD2.fbx"]

for name in ["test4_decimated", "test4_decimated_LOD1", "test4_decimated_LOD2"]:
    asset_path = f"/Game/ImportedAssets/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.EditorAssetLibrary.delete_asset(asset_path)

for fbx_file in files:
    task = unreal.AssetImportTask()
    task.filename = export_path + fbx_file
    task.destination_path = '/Game/ImportedAssets'
    task.automated = True
    task.replace_existing = True
    task.save = True
    
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = False
    
    static_mesh_options = unreal.FbxStaticMeshImportData()
    static_mesh_options.combine_meshes = True
    static_mesh_options.auto_generate_collision = False
    
    options.static_mesh_import_data = static_mesh_options
    task.options = options
    
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    
    asset_path = f"/Game/ImportedAssets/{fbx_file.replace('.fbx', '')}"
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if asset:
        nanite_settings = asset.get_editor_property('nanite_settings')
        nanite_settings.enabled = False
        asset.set_editor_property('nanite_settings', nanite_settings)
        unreal.EditorAssetLibrary.save_loaded_asset(asset)
    
    print(f"Imported: {fbx_file} (Nanite disabled)")

print("\nAll LODs imported!")

asset_paths = [
    '/Game/ImportedAssets/test4_decimated',
    '/Game/ImportedAssets/test4_decimated_LOD1',
    '/Game/ImportedAssets/test4_decimated_LOD2'
]

print("\n" + "="*60)
print("POLYGON COUNT VERIFICATION")
print("="*60)

for path in asset_paths:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset:
        num_triangles = asset.get_num_triangles(0)
        name = path.split('/')[-1]
        print(f"{name}: {num_triangles} triangles")

print("\nExpected from 3ds Max:")
print("test4_decimated: 7306 polygons")
print("test4_decimated_LOD1: 3652 polygons") 
print("test4_decimated_LOD2: 1824 polygons")
print("="*60)
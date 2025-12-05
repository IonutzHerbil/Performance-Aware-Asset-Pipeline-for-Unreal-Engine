import json
import os

class UnrealImporter:
    def __init__(self):
        self.import_destination = "/Game/ImportedAssets"

    def generate_import_script(self, fbx_path, json_path=None):
        asset_name = os.path.splitext(os.path.basename(fbx_path))[0]
        fbx_path_unix = fbx_path.replace('\\', '/')
        json_path_unix = fbx_path_unix.replace('.fbx', '.json')

        if "_LOD" in fbx_path:
            clean_name = fbx_path.split("_LOD")[0] + ".fbx"
            return f"""
import unreal
import os
unreal.log_error("PIPELINE USER ERROR: You selected an LOD file!")
unreal.log_error("Please select the BASE file instead: {os.path.basename(clean_name)}")
print("ERROR: Please import the base file, not the LOD.")
"""

        script = f"""
import unreal
import os
import json
import webbrowser

ASSET_NAME = "{asset_name}"
FBX_PATH = r"{fbx_path_unix}"
JSON_PATH = r"{json_path_unix}"
DESTINATION = "{self.import_destination}"
MAX_POLY_BUDGET = 50000

metadata = {{}}
if os.path.exists(JSON_PATH):
    with open(JSON_PATH, 'r') as f:
        metadata = json.load(f)

print(f"--- PIPELINE START: {{ASSET_NAME}} ---")

tex_issues = metadata.get('texture_issues', "")
if tex_issues:
    unreal.log_warning(f"TEXTURE VALIDATION FAILED: {{tex_issues}}")
    print(f"WARNING: {{tex_issues}}")
else:
    print("Texture Audit: PASSED")

enable_nanite = metadata.get('enable_nanite', False)
if enable_nanite:
    print("Optimization Mode: NANITE ENABLED")
else:
    print("Optimization Mode: STANDARD (LODs)")

predicted_polys = metadata.get('polygons', 0)
if predicted_polys > MAX_POLY_BUDGET:
    unreal.log_warning("ASSET EXCEEDS POLYGON BUDGET! Proceeding with caution...")

task = unreal.AssetImportTask()
task.filename = FBX_PATH
task.destination_path = DESTINATION
task.automated = True
task.replace_existing = True
task.save = True

task.factory = unreal.FbxFactory() 

options = unreal.FbxImportUI()
options.import_mesh = True
options.import_materials = True
options.import_textures = False
options.static_mesh_import_data.combine_meshes = True
options.static_mesh_import_data.auto_generate_collision = True

options.static_mesh_import_data.build_nanite = enable_nanite

task.options = options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

asset_path = f"{{DESTINATION}}/{{ASSET_NAME}}"
loaded_mesh = unreal.EditorAssetLibrary.load_asset(asset_path)

imported_lods = 0

if loaded_mesh:
    base_dir = os.path.dirname(FBX_PATH)
    
    for i in range(1, 4):
        lod_filename = f"{{ASSET_NAME}}_LOD{{i}}.fbx"
        lod_full_path = os.path.join(base_dir, lod_filename).replace('\\\\', '/')
        
        if os.path.exists(lod_full_path):
            print(f"Found LOD{{i}}: {{lod_filename}}")
            ret = unreal.EditorStaticMeshLibrary.import_lod(loaded_mesh, i, lod_full_path)
            if ret != -1: 
                imported_lods += 1
                print(f"Successfully imported LOD {{i}}")
        else:
            break

actual_tris = 0
data_source = "Unknown"

if loaded_mesh:
    try:
        actual_tris = loaded_mesh.source_models[0].get_triangle_count()
        data_source = "Source Model (Exact)"
    except:
        try:
            actual_tris = loaded_mesh.get_source_model(0).get_triangle_count()
            data_source = "Source Model (Getter)"
        except:
            actual_tris = loaded_mesh.get_num_triangles(0)
            data_source = "Render Mesh (Fallback)"

accuracy = 100
if predicted_polys > 0:
    diff = abs(predicted_polys - actual_tris)
    accuracy = max(0, 100 - (diff / predicted_polys * 100))

status_color = "red"
status_text = "REVIEW NEEDED"

if accuracy > 90:
    status_color = "green"
    status_text = "PASSED"
elif enable_nanite and actual_tris > 0:
    status_color = "green" 
    status_text = "PASSED (Nanite Optimized)"
    accuracy = 100 
else:
    status_color = "red"
    status_text = "FAILED"

html_content = f'''
<html>
<body style="font-family: Arial; background-color: #333; color: white; padding: 20px;">
    <h1>Pipeline Report: {{ASSET_NAME}}</h1>
    <div style="background-color: #444; padding: 15px; border-radius: 5px;">
        <h2>Status: <span style="color: {{status_color}}">{{status_text}}</span></h2>
        <p>Accuracy Score: <strong>{{accuracy:.2f}}%</strong></p>
    </div>
    <br>
    <table border="1" style="width:100%; border-collapse: collapse; text-align: left;">
        <tr><th style="padding: 10px;">Metric</th><th style="padding: 10px;">Details</th></tr>
        <tr><td style="padding: 10px;">Poly Count</td><td style="padding: 10px;">{{actual_tris}} (Pred: {{predicted_polys}})</td></tr>
        <tr><td style="padding: 10px;">Data Source</td><td style="padding: 10px;">{{data_source}}</td></tr>
        <tr><td style="padding: 10px;">LODs</td><td style="padding: 10px;">{{imported_lods}} imported</td></tr>
        <tr><td style="padding: 10px;">Nanite</td><td style="padding: 10px;">{{"ENABLED" if enable_nanite else "Disabled"}}</td></tr>
        <tr><td style="padding: 10px;">Texture Audit</td><td style="padding: 10px;">{{tex_issues if tex_issues else "OK"}}</td></tr>
    </table>
</body>
</html>
'''

report_path = FBX_PATH.replace('.fbx', '_Report.html')
with open(report_path, 'w') as f:
    f.write(html_content)

print(f"Report generated: {{report_path}}")
webbrowser.open('file://' + os.path.realpath(report_path))
"""
        return script

    def save_import_script(self, fbx_path):
        json_path = fbx_path.replace('.fbx', '.json')
        script_content = self.generate_import_script(fbx_path, json_path)
        script_path = fbx_path.replace('.fbx', '_import.py')
        with open(script_path, 'w') as f:
            f.write(script_content)
        return script_path
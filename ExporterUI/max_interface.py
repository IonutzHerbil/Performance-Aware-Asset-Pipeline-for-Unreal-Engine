import os
import time
import json
from pathlib import Path


class MaxScriptInterface:
    def __init__(self):
        self.temp_dir = Path("D:/Puoli/An3 Sem1 - UL/Graphics/Pipeline-for-Unreal-Engine/temp")
        self.temp_dir.mkdir(exist_ok=True)

        self.command_file = self.temp_dir / "command.ms"
        self.result_file = self.temp_dir / "result.txt"
    
    def execute(self, script, timeout=30):
        if self.result_file.exists():
            self.result_file.unlink()

        with open(self.command_file, 'w') as f:
            f.write(script)

        max_attempts = timeout * 10
        for i in range(max_attempts):
            if self.result_file.exists():
                time.sleep(0.1)

                with open(self.result_file, 'r') as f:
                    result = f.read().strip()

                self.result_file.unlink()
                return result

            time.sleep(0.1)

        raise Exception(f"3ds Max didn't respond (timeout after {timeout}s)")
    
    def test_connection(self):
        try:
            result = self.execute('print "Connected"', timeout=5)
            return True
        except:
            return False
    
    def get_scene_objects(self):
        script = """
(
    local objList = #()
    for obj in geometry do (
        append objList obj.name
    )
    local result = ""
    for i = 1 to objList.count do (
        result += objList[i]
        if i < objList.count then result += ","
    )
    result
)
"""
        response = self.execute(script, timeout=10)
        
        if not response or response == "OK":
            return []
        
        return [obj.strip() for obj in response.split(',') if obj.strip()]
    
    def get_object_stats(self, object_name):
        script = f"""
(
    local obj = getNodeByName "{object_name}"
    if obj != undefined then (
        if classof obj.baseobject != Editable_Poly then (
            convertToPoly obj
        )

        local polys = polyOp.getNumFaces obj
        local verts = polyOp.getNumVerts obj

        polys as string + "," + verts as string
    ) else (
        "ERROR"
    )
)
"""
        response = self.execute(script, timeout=15)
        
        if response == "ERROR":
            raise Exception(f"Object '{object_name}' not found")
        
        parts = response.split(',')
        return {
            'polygons': int(parts[0]),
            'vertices': int(parts[1])
        }
    
    def export_fbx(self, object_name, export_path):
        export_path_escaped = export_path.replace('\\', '\\\\')

        script = f"""
(
    local obj = getNodeByName "{object_name}"
    if obj != undefined then (
        select obj

        FBXExporterSetParam "SmoothingGroups" true
        FBXExporterSetParam "TangentSpaceExport" true
        FBXExporterSetParam "SmoothMeshExport" true

        exportFile "{export_path_escaped}" #noPrompt selectedOnly:true using:FBXEXP
        "SUCCESS"
    ) else (
        "ERROR: Object not found"
    )
)
"""
        result = self.execute(script, timeout=60)

        if "ERROR" in result:
            raise Exception(result)

        return True
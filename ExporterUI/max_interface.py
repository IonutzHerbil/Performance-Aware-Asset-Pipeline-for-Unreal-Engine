import os
import time
import tempfile
from pathlib import Path

class MaxScriptInterface:
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "3dsMaxPipeline"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.command_file = self.temp_dir / "command.ms"
        self.result_file = self.temp_dir / "result.txt"
        
        if self.command_file.exists(): self.command_file.unlink()
        if self.result_file.exists(): self.result_file.unlink()

    def execute(self, script, timeout=30):
        if self.result_file.exists():
            self.result_file.unlink()

        with open(self.command_file, 'w') as f:
            f.write(script)

        max_attempts = timeout * 10
        for i in range(max_attempts):
            if self.result_file.exists():
                time.sleep(0.1) 
                try:
                    with open(self.result_file, 'r') as f:
                        result = f.read().strip()
                    self.result_file.unlink()
                    return result
                except:
                    pass
            time.sleep(0.1)
        raise Exception(f"3ds Max timed out ({timeout}s). Is monitor.ms running?")
    
    def test_connection(self):
        try:
            res = self.execute('print "Ping"', timeout=2)
            return True if res else False
        except:
            return False

    def get_scene_objects(self):
        script = """
        (
            local ss = stringStream ""
            local names = for o in geometry collect o.name
            for i = 1 to names.count do (
                format "%" names[i] to:ss
                if i < names.count do format "," to:ss
            )
            ss as string
        )
        """
        response = self.execute(script)
        if not response or "ERROR" in response: return []
        return [x for x in response.split(',') if x.strip()]

    def get_object_stats(self, object_name):
        script = f"""
        (
            local obj = getNodeByName "{object_name}"
            if obj != undefined then (
                local tmesh = snapshotAsMesh obj
                local tris = tmesh.numFaces 
                local verts = tmesh.numVerts
                delete tmesh 
                (tris as string) + "," + (verts as string)
            ) else "ERROR_NOT_FOUND"
        )
        """
        response = self.execute(script)
        if "ERROR" in response: raise Exception(f"Object '{object_name}' not found")
        if "," not in response: return {'polygons': 0, 'vertices': 0}
        try:
            p, v = response.split(',')
            return {'polygons': int(p), 'vertices': int(v)}
        except ValueError:
            raise Exception(f"Could not parse data: {response}")

    def export_fbx(self, object_name, export_path, do_lods=True):
        path = export_path.replace('\\', '\\\\')
        
        max_bool = "true" if do_lods else "false"
        
        script = f"""
        (
            if pipeline != undefined then (
                pipeline.runAutomatedExport "{object_name}" "{path}" {max_bool}
            ) else (
                "ERROR: AssetPipeline.ms not loaded!"
            )
        )
        """
        res = self.execute(script, timeout=120) # Increased timeout for LOD processing
        if "ERROR" in res: raise Exception(res)
        return True
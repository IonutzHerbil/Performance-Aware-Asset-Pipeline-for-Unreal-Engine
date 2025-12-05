import json

class Exporter:
    def create_metadata(self, object_name, stats, export_path):
        polygons = stats['polygons']
        vertices = stats['vertices']

        complexity = "Low"
        if polygons > 10000: complexity = "Medium"
        if polygons > 50000: complexity = "High"

        metadata = {
            'asset_name': object_name,
            'export_path': export_path,
            'polygons': polygons, 
            'vertices': vertices,
            'complexity': complexity
        }

        json_path = export_path.replace('.fbx', '.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata, json_path
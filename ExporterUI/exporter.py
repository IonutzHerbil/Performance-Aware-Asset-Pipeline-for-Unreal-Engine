import json

class Exporter:
    def create_metadata(self, object_name, stats, export_path):
        polygons = stats['polygons']
        vertices = stats['vertices']

        metadata = {
            'asset_name': object_name,
            'export_path': export_path,
            'geometry': {
                'polygons': polygons, 
                'vertices': vertices
            },
        }

        json_path = export_path.replace('.fbx', '.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata, json_path
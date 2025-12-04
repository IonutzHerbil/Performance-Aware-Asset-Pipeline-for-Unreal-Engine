import unreal #type:ignore

class PerformanceMeasurer:
    def measure_asset(self, asset_path):
        if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            unreal.log_error(f"PerformanceMeasurer: Asset not found at {asset_path}")
            return None

        asset = unreal.EditorAssetLibrary.load_asset(asset_path)

        if isinstance(asset, unreal.StaticMesh):
            triangles = asset.get_num_triangles(0)
            vertices = asset.get_num_vertices(0)

            memory_bytes = vertices * 64
            memory_mb = memory_bytes / (1024 * 1024)

            return {
                'triangles': triangles,
                'vertices': vertices,
                'memory_mb': round(memory_mb, 4)
            }

        unreal.log_warning(f"PerformanceMeasurer: Asset {asset_path} is not a Static Mesh")
        return None
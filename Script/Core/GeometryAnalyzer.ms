struct GeometryAnalyzer (
    fn analyze obj = (
        local bbox = nodeGetBoundingBox obj obj.transform
        local bboxSize = bbox[2] - bbox[1]
        local volume = bboxSize.x * bboxSize.y * bboxSize.z
        
        return #(obj.numFaces, obj.numVerts, bboxSize, volume)
    )
)

global geoAnalyzer = GeometryAnalyzer()
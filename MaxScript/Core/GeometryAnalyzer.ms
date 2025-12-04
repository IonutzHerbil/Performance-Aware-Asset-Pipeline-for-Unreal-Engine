struct GeometryAnalyzer (
    fn analyze obj = (
        local tmesh = snapshotAsMesh obj
        local tris = tmesh.numFaces
        local verts = tmesh.numVerts
        delete tmesh
        return #(tris, verts)
    )
)
global geoAnalyzer = GeometryAnalyzer()
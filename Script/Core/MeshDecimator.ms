struct MeshDecimator (
    fn generateLOD obj targetPercent = (
        local startPolys = getPolygonCount obj
        
        try (
            select obj
            modPanel.setCurrentObject obj.baseObject
            
            addModifier obj (ProOptimizer())
            local proOpt = obj.modifiers[#ProOptimizer]
            
            proOpt.Calculate = true 
            proOpt.KeepUV = true     
            proOpt.KeepNormals = true 
            proOpt.VertexPercent = targetPercent
            
            convertToPoly obj
            
            local finalPolys = (getPolygonCount obj)[1]
            return finalPolys
            
        ) catch (
            format "LOD Error: %\n" (getCurrentException())
            return 0
        )
    )
)
global meshDecimator = MeshDecimator()
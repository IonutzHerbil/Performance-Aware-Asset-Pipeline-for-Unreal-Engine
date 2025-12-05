struct MeshDecimator (
    fn generateLOD obj targetPercent = (
        try (
            if classof obj != Editable_Poly then convertToPoly obj
            
            addModifier obj (ProOptimizer())
            local proOpt = obj.modifiers[#ProOptimizer]
            
            proOpt.KeepTextures = true  
            proOpt.KeepVC = false      
            proOpt.KeepNormals = false  
            
            select obj
            proOpt.Calculate = true 
            
            proOpt.VertexPercent = targetPercent
            
            convertToPoly obj 
            
            return obj.numFaces
        ) catch (
            format "Decimator Error: %\n" (getCurrentException())
            return 0
        )
    )
)
global meshDecimator = MeshDecimator()
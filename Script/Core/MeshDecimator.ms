struct MeshDecimator (
    fn generateLOD obj targetPercent = (
        local geoType = "poly"
        if classOf obj.baseobject == Editable_Mesh then (
            geoType = "mesh"
        ) else if classOf obj.baseobject != Editable_Poly then (
            convertToPoly obj
            geoType = "poly"
        )
        
        local mesh = obj
        local startPolys = polyOp.getNumFaces mesh
        local targetPolys = (startPolys * targetPercent / 100.0) as integer
        
        if targetPolys >= startPolys then (
            format "Target already met: % polygons\n" startPolys
            return startPolys
        )
        
        format "Starting LOD: % -> % polygons (target % percent)\n" startPolys targetPolys targetPercent
        
        try (
            select mesh
            
            modPanel.setCurrentObject mesh.baseObject
            modPanel.addModToSelection (MultiRes()) ui:on
            
            mesh.MultiRes.vertexPercent = targetPercent
            
            mesh.MultiRes.generate = true
            max select none
            select mesh
            mesh.MultiRes.generate = true
            
            modPanel.setCurrentObject mesh.modifiers[#MultiRes]
            
            select mesh
            if geoType == "poly" then (
                convertToPoly mesh
            ) else (
                convertToMesh mesh
            )
            
            local finalPolys = polyOp.getNumFaces mesh
            local reduction = 100.0 * (startPolys - finalPolys) / startPolys
            format "LOD Complete: % polygons (%.1f percent reduction)\n" finalPolys reduction
            
            return finalPolys
            
        ) catch (
            format "LOD generation failed: %\n" (getCurrentException())
            return startPolys
        )
    )
)

global meshDecimator = MeshDecimator()
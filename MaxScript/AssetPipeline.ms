filein "Core/GeometryAnalyzer.ms"
filein "Core/PerformancePredictor.ms"
filein "Core/MaterialAnalyzer.ms"
filein "Core/MeshDecimator.ms"

struct AssetPipeline (
    fn runAnalysis = (
        if selection.count == 0 then (
            messageBox "Select an object!"
            return false
        )
        
        local obj = selection[1]
        local geoData = geoAnalyzer.analyze obj
        local perfData = perfPredictor.predict geoData
        local matData = matAnalyzer.analyze obj
        
        local lodChoice = queryBox "Generate LOD versions?" title:"LOD Generation"
        
        local exportPath = getSaveFileName caption:"Export FBX" types:"FBX Files (*.fbx)|*.fbx"
        if exportPath != undefined then (
            select obj
            
            FBXExporterSetParam "SmoothingGroups" true
            FBXExporterSetParam "TangentSpaceExport" true
            FBXExporterSetParam "SmoothMeshExport" true
            
            exportFile exportPath #noPrompt selectedOnly:true using:FBXEXP
            
            local lodCount = 0
            local lodObjects = #() 
            
            if lodChoice then (
                local lodLevels = #(50, 25)
                
                for i = 1 to lodLevels.count do (
                    local lodNum = i
                    local targetPercent = lodLevels[i]
                    
                    local objCopy = copy obj
                    objCopy.name = obj.name + "_LOD" + (lodNum as string)
                    
                    if classof objCopy.baseobject != Editable_Poly then (
                        convertToPoly objCopy
                    )
                    
                    local finalPolyCount = meshDecimator.generateLOD objCopy targetPercent
                    
                    if isValidNode objCopy then (
                        local lodPath = substituteString exportPath ".fbx" ("_LOD" + (lodNum as string) + ".fbx")
                        select objCopy
                        exportFile lodPath #noPrompt selectedOnly:true using:FBXEXP
                        
                        append lodObjects objCopy  
                        lodCount += 1
                        format "LOD% exported: % polygons\n" lodNum finalPolyCount
                    ) else (
                        format "LOD% object was deleted during generation\n" lodNum
                    )
                )
                
                for lodObj in lodObjects do (
                    if isValidNode lodObj then (
                        delete lodObj
                    )
                )
            )
            
            local jsonPath = (substituteString exportPath ".fbx" ".json")
            local jsonFile = createFile jsonPath
            
            format "{" to:jsonFile
            format "\"asset\":\"%\"," obj.name to:jsonFile
            format "\"polygons\":%," geoData[1] to:jsonFile
            format "\"vertices\":%," geoData[2] to:jsonFile
            format "\"texture_count\":%," matData[1] to:jsonFile
            format "\"material\":\"%\"," matData[2] to:jsonFile
            format "\"has_diffuse\":%," (if matData[3] then "true" else "false") to:jsonFile
            format "\"has_normal\":%," (if matData[4] then "true" else "false") to:jsonFile
            format "\"has_specular\":%," (if matData[5] then "true" else "false") to:jsonFile
            format "\"complexity\":\"%\"," perfData[2] to:jsonFile
            format "\"estimated_objects\":%," perfData[1] to:jsonFile
            format "\"lod_count\":%"  lodCount to:jsonFile
            format "}" to:jsonFile
            
            close jsonFile
            
            format "Exported: %\n" exportPath
            format "Metadata: %\n" jsonPath
        )
        
        local report = "ASSET ANALYSIS\n"
        report += "==============\n"
        report += "Object: " + obj.name + "\n"
        report += "Polygons: " + (geoData[1] as string) + "\n"
        report += "Vertices: " + (geoData[2] as string) + "\n"
        report += "Material: " + matData[2] + "\n"
        report += "Textures: " + (matData[1] as string) + "\n"
        report += "Est. Objects: " + (perfData[1] as string) + "\n"
        report += "Complexity: " + perfData[2] + "\n"
        
        format "%\n" report
        messageBox report title:"Analysis Complete"
    )
)

global pipeline = AssetPipeline()
pipeline.runAnalysis()
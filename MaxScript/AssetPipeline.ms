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
        local lodChoice = queryBox "Generate LOD versions?" title:"LOD Generation"
        local exportPath = getSaveFileName caption:"Export FBX" types:"FBX Files (*.fbx)|*.fbx"
        
        if exportPath != undefined then (
            self.runAutomatedExport obj.name exportPath lodChoice
        )
    ),

    fn runAutomatedExport objName exportPath doLODs = (
        local obj = getNodeByName objName
        if obj == undefined then return "ERROR_OBJ_NOT_FOUND"

        select obj
        
        local geoData = geoAnalyzer.analyze obj
        local perfData = perfPredictor.predict geoData
        local matData = matAnalyzer.analyze obj

        FBXExporterSetParam "AxisConversionMethod" "None" 
        FBXExporterSetParam "UpAxis" "Z" 
        FBXExporterSetParam "SmoothingGroups" true
        FBXExporterSetParam "Triangulate" true
        
        exportFile exportPath #noPrompt selectedOnly:true using:FBXEXP
        
        local lodCount = 0
        local lodObjects = #() 
        
        if doLODs then (
            local lodLevels = #(50, 25, 12) 
            
            for i = 1 to lodLevels.count do (
                local lodNum = i
                local targetPercent = lodLevels[i]
                local objCopy = copy obj
                objCopy.name = obj.name + "_LOD" + (lodNum as string)
                
                if classof objCopy.baseobject != Editable_Poly then convertToPoly objCopy
                
                local finalPolyCount = meshDecimator.generateLOD objCopy targetPercent
                
                if isValidNode objCopy then (
                    local lodPath = substituteString exportPath ".fbx" ("_LOD" + (lodNum as string) + ".fbx")
                    select objCopy
                    exportFile lodPath #noPrompt selectedOnly:true using:FBXEXP
                    append lodObjects objCopy  
                    lodCount += 1
                )
            )
            for lodObj in lodObjects do ( if isValidNode lodObj then delete lodObj )
        )
        
        
        local jsonPath = (substituteString exportPath ".fbx" ".json")
        local jsonFile = createFile jsonPath
        format "{" to:jsonFile
        format "\"asset\":\"%\"," obj.name to:jsonFile
        format "\"polygons\":%," geoData[1] to:jsonFile
        format "\"vertices\":%," geoData[2] to:jsonFile
        format "\"complexity\":\"%\"," perfData[2] to:jsonFile
        format "\"lod_count\":%"  lodCount to:jsonFile
        format "}" to:jsonFile
        close jsonFile
        
        return "SUCCESS"
    )
)

global pipeline = AssetPipeline()
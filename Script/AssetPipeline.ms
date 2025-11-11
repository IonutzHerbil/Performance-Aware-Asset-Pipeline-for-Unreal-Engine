filein "Core/GeometryAnalyzer.ms"
filein "Core/PerformancePredictor.ms"

struct AssetPipeline (
    fn runAnalysis = (
        if selection.count == 0 then (
            messageBox "Select an object!"
            return false
        )
        
        local obj = selection[1]
        local geoData = geoAnalyzer.analyze obj
        local perfData = perfPredictor.predict geoData
        
        local exportPath = getSaveFileName caption:"Export FBX" types:"FBX Files (*.fbx)|*.fbx"
        if exportPath != undefined then (
            select obj
            
            FBXExporterSetParam "SmoothingGroups" true
            FBXExporterSetParam "TangentSpaceExport" true
            FBXExporterSetParam "SmoothMeshExport" true
            
            exportFile exportPath #noPrompt selectedOnly:true using:FBXEXP
            
            local jsonPath = (substituteString exportPath ".fbx" ".json")
            local jsonFile = createFile jsonPath
            
            format "{" to:jsonFile
            format "\"asset\":\"%\"," obj.name to:jsonFile
            format "\"polygons\":%," geoData[1] to:jsonFile
            format "\"vertices\":%," geoData[2] to:jsonFile
            format "\"complexity\":\"%\"," perfData[2] to:jsonFile
            format "\"estimated_objects\":%"  perfData[1] to:jsonFile
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
        report += "Est. Objects: " + (perfData[1] as string) + "\n"
        report += "Complexity: " + perfData[2] + "\n"
        
        format "%\n" report
        messageBox report title:"Analysis Complete"
    )
)

global pipeline = AssetPipeline()
pipeline.runAnalysis()
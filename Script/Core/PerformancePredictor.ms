struct PerformancePredictor (
    fn predict geoData = (
        local polyCount = geoData[1]
        
        local complexity = "Low"
        if polyCount > 2000 then complexity = "Medium"
        if polyCount > 10000 then complexity = "High"
        if polyCount > 50000 then complexity = "Very High"
        
        local estimatedObjects = (polyCount / 5000) as integer
        if estimatedObjects < 1 then estimatedObjects = 1
        
        return #(estimatedObjects, complexity)
    )
)

global perfPredictor = PerformancePredictor()
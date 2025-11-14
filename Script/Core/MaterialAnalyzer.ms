struct MaterialAnalyzer (
    fn analyze obj = (
        local textureCount = 0
        local materialName = "None"
        local hasNormalMap = false
        local hasSpecularMap = false
        local hasDiffuseMap = false
        
        if obj.material != undefined then (
            materialName = obj.material.name
            
            if classOf obj.material == Standardmaterial then (
                if obj.material.diffuseMap != undefined then (
                    hasDiffuseMap = true
                    textureCount += 1
                )
                if obj.material.bumpMap != undefined then (
                    hasNormalMap = true
                    textureCount += 1
                )
                if obj.material.specularMap != undefined then (
                    hasSpecularMap = true
                    textureCount += 1
                )
            )
        )
        
        return #(textureCount, materialName, hasDiffuseMap, hasNormalMap, hasSpecularMap)
    )
)

global matAnalyzer = MaterialAnalyzer()
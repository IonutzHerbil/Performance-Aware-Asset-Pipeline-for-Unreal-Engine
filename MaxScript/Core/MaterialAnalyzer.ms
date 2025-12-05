struct MaterialAnalyzer (
    fn analyze obj = (
        local textureCount = 0
        local materialName = "None"
        local issues = ""
        
        if obj.material != undefined then (
            materialName = obj.material.name
            
            fn checkMap map mapType = (
                if map != undefined and classof map == Bitmaptexture then (
                    try (
                        local w = map.bitmap.width
                        local h = map.bitmap.height
                        local err = ""
                        
                        if (w > 2048 or h > 2048) then (
                            err += (mapType + " " + (w as string) + "x" + (h as string) + " is too large. ")
                        )
                        if (bit.and w (w-1)) != 0 or (bit.and h (h-1)) != 0 then (
                            err += (mapType + " " + (w as string) + "x" + (h as string) + " is NOT Power of Two. ")
                        )
                        
                        return err
                    ) catch ( return "" )
                )
                return ""
            )

            try (
                if hasProperty obj.material "diffuseMap" and obj.material.diffuseMap != undefined then (
                    textureCount += 1
                    issues += checkMap obj.material.diffuseMap "Diffuse"
                )
                if hasProperty obj.material "base_color_map" and obj.material.base_color_map != undefined then (
                    textureCount += 1
                    issues += checkMap obj.material.base_color_map "BaseColor"
                )
            ) catch()
        )
        
        return #(textureCount, materialName, issues)
    )
)
global matAnalyzer = MaterialAnalyzer()
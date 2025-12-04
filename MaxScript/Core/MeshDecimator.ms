struct MeshDecimator (
    fn generateLOD obj targetPercent = (
        try (
            addModifier obj (ProOptimizer())
            local proOpt = obj.modifiers[#ProOptimizer]
            proOpt.Calculate = true
            proOpt.KeepUV = true
            proOpt.KeepNormals = true
            proOpt.VertexPercent = targetPercent
            return true
        ) catch (
            return false
        )
    )
)
global meshDecimator = MeshDecimator()
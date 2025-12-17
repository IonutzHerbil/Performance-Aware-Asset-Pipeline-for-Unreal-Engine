# Performance-Aware 3D Asset Pipeline for Unreal Engine

An automated asset conditioning pipeline that bridges 3ds Max and Unreal Engine 5, streamlining the process of preparing, optimizing, and validating 3D assets for game development.

**Author:** Ioan Herbil    
**Repository:** [github.com/IonutzHerbil](https://github.com/IonutzHerbil)

---

## Overview

This pipeline automates the workflow from Digital Content Creation (DCC) tools to game engines, eliminating repetitive manual tasks and ensuring technical compliance through automated validation. The system is built on principles of modularity, loose coupling, and flexibility.

### Key Features

- **Automated LOD Generation:** Generates multiple Level of Detail variants (50%, 25%, 12% reduction) using ProOptimizer
- **Nanite Support:** Configurable Nanite virtualized geometry integration for UE5
- **Performance Prediction:** Classifies asset complexity and predicts runtime impact
- **Validation Engine:** 100% polygon count accuracy verification between DCC and engine
- **Technical Compliance:** Automated texture validation (Power-of-Two, resolution limits)
- **HTML Reporting:** Instant validation reports with actionable feedback
- **Decoupled Architecture:** Modular design allows independent testing and debugging

---

## Architecture

The pipeline consists of three distinct stages:

### Stage I: Preparation (3ds Max)
**Technology:** MAXScript

- Geometry analysis and polygon counting
- Automated LOD generation using ProOptimizer
- Material and texture validation
- Performance prediction and classification
- Technical compliance checks

### Stage II: Communication Bridge
**Technology:** JSON Manifest

- Serializes all technical data from 3ds Max
- Stores user settings (Nanite enable/disable, LOD preferences)
- Provides asynchronous Inter-Process Communication (IPC)
- Acts as data adapter between platforms

### Stage III: Assembly (Unreal Engine 5)
**Technology:** Python API

- Ingests FBX and JSON manifest
- Configures asset properties and import settings
- Injects LOD groups into asset hierarchy
- Validates imported geometry against predictions
- Generates HTML validation report

---

## Technical Implementation

### Geometry Optimization

**ProOptimizer Integration:**
```maxscript
// Critical Decimation Fix: KeepNormals = false
proOpt.KeepNormals = false  // Enforce Modifier Baking
convertToPoly obj
```

The pipeline enforces modifier baking with aggressive flags to ensure decimated geometry is finalized as static mesh data before export, preventing unstable procedural forms in the FBX stream.

### Performance Classification

Assets are classified based on polygon thresholds:
- **Low:** < 10,000 polygons
- **Medium:** 10,000 - 30,000 polygons
- **High:** 30,000 - 50,000 polygons
- **Very High:** > 50,000 polygons

### Cross-Platform Data Model

The pipeline handles the polygon/triangle discrepancy between platforms:
- **3ds Max:** Reports faces/polygons (quads and n-gons)
- **Unreal Engine:** Reports triangles
- **Conversion:** `Triangles = Polygons × 2`

This mapping is critical for validation accuracy and is implemented in the Python validation engine.

---

## Requirements

### Software
- **3ds Max** (2020 or later) with MAXScript support
- **Unreal Engine 5** with Python API enabled
- **Python 3.7+** (typically bundled with UE5)

### Dependencies
- JSON parsing libraries (standard in both Python and MAXScript)
- Unreal Engine Python API (`unreal` module)

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/IonutzHerbil/[repository-name].git
cd [repository-name]
```

2. Configure 3ds Max MAXScript path:
   - Copy MAXScript files to your 3ds Max scripts directory
   - Or add the scripts folder to your MAXScript search paths

3. Enable Python in Unreal Engine:
   - Edit → Plugins → Search "Python"
   - Enable "Python Editor Script Plugin"
   - Restart Unreal Engine

4. Configure pipeline paths in JSON manifest template

---

## Usage

### Basic Workflow

1. **Prepare Asset in 3ds Max:**
   ```maxscript
   -- Run the preparation script
   fileIn "PreparationScript.ms"
   -- Follow UI prompts to configure LODs and settings
   ```

2. **Export:**
   - Pipeline automatically generates JSON manifest
   - FBX is exported with baked geometry and LODs
   - Files are saved to configured export directory

3. **Import to Unreal Engine:**
   ```python
   # Run the assembly script in UE5 Python console
   import AssemblyScript
   AssemblyScript.process_asset("path/to/manifest.json")
   ```

4. **Review Validation Report:**
   - HTML report is generated automatically
   - Review flagged issues (texture compliance, poly budget, etc.)
   - Iterate on asset if needed

### Advanced Configuration

**Enable Nanite Support:**
```json
{
  "enable_nanite": true,
  "nanite_fallback_percent": 100
}
```

**Custom LOD Settings:**
```json
{
  "lod_levels": [
    {"reduction": 50, "screen_size": 0.5},
    {"reduction": 25, "screen_size": 0.25},
    {"reduction": 12, "screen_size": 0.1}
  ]
}
```

---

## Project Structure

```
pipeline/
├── maxscript/
│   ├── GeometryAnalyzer.ms      # Polygon counting and analysis
│   ├── MeshDecimator.ms         # LOD generation
│   ├── MaterialAnalyzer.ms      # Texture validation
│   ├── PerformancePredictor.ms  # Complexity classification
│   └── PreparationScript.ms     # Main UI and orchestration
├── python/
│   ├── AssemblyScript.py        # UE5 import and configuration
│   ├── ValidationEngine.py      # Polygon count verification
│   └── ReportGenerator.py       # HTML report creation
├── manifests/
│   └── template.json            # JSON manifest template
└── docs/
    └── technical_specification.md
```

---

## Key Technical Solutions

### Problem: Geometry Stability
**Issue:** ProOptimizer produced 0% reduction upon export  
**Solution:** Enforced modifier baking with `convertToPoly` and `KeepNormals = false`

### Problem: Cross-Platform Data Mismatch
**Issue:** Validation failures due to polygon vs. triangle counting  
**Solution:** Implemented mathematical relationship (Triangle = Polygons × 2) in validation engine

### Problem: Texture Compliance
**Issue:** Manual texture checking is error-prone  
**Solution:** Automated checks using bitwise operations for Power-of-Two validation

### Problem: IPC Latency
**Issue:** File-based polling introduces latency  
**Future Solution:** Transition to socket-based communication for real-time interaction

---

## Performance Results

- **Automation:** Eliminates manual LOD export and configuration steps
- **Validation Accuracy:** 100% polygon count verification
- **Throughput:** Processes assets in seconds vs. minutes of manual work
- **Quality Assurance:** Instant HTML reports with actionable feedback

---

## Testing Methodology

The pipeline was validated using three football models with varying polygon counts:
- **Low Poly:** ~5,000 polygons
- **Medium Poly:** ~20,000 polygons  
- **High Poly:** ~60,000 polygons

Each model was processed through all three pipeline stages with verification at each step:
1. GeometryAnalyzer accuracy
2. MeshDecimator reduction percentages
3. JSON serialization correctness
4. UE5 import polygon count matching

---

## Future Enhancements

- [ ] Socket-based IPC for reduced latency
- [ ] Material graph automation and validation
- [ ] UV layout optimization and validation
- [ ] Collision mesh generation
- [ ] Batch processing support for asset libraries
- [ ] Integration with version control systems
- [ ] Real-time preview in UE5 during 3ds Max editing

---

## References

1. [Stanford Computer Graphics - Mesh Simplification](https://graphics.stanford.edu/courses/cs468-10-fall/LectureSlides/08_Simplification.pdf)
2. [Unreal Engine Nanite Documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine)
3. [Unreal Engine Python API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/)
4. [ScriptSpot - MAXScript Resources](https://www.scriptspot.com/)

---

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Test changes with multiple asset types
4. Submit pull request with detailed description

---

## License

This project was developed as part of academic coursework at the University of Limerick.

---

## Contact

**Ioan Herbil**  
University of Limerick  
Student ID: 25341723

For questions, issues, or collaboration inquiries, please open an issue on GitHub.

---

## Acknowledgments

- University of Limerick Computer Graphics course materials
- Autodesk 3ds Max documentation and community
- Epic Games Unreal Engine documentation
- Open source MAXScript community at ScriptSpot

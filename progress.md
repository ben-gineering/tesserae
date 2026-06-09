# Tesserae - Development Progress

## Project Timeline

### 2026-06-08 — Initial Development

#### Phase 1: Visual Analysis
- Analyzed reference image (`lamp.jpg`) — industrial floor lamp with 6 spotlights
- Identified key characteristics:
  - Black metal truss/lattice frame structure
  - Approximately 150-180cm height
  - 25-35cm width/depth
  - 6 vertical sections
  - ~15-20mm rod diameter

#### Phase 2: Base Model Creation
- Created initial parametric OpenSCAD design (`lamp_frame.scad`)
- Implemented core structure:
  - 4 vertical corner posts
  - Horizontal rings at each section
  - X cross-bracing on all faces

#### Phase 3: Geometry Fixes
**Issue**: Horizontal rods extended beyond corner posts in renders

**Iterations**:
- v1: Initial design — protrusion visible
- v2-v4: Adjusted `rod_x()` and `rod_y()` modules — issue persisted
- v5: **Root cause identified** — positioning logic didn't connect corner-to-corner

**Solution**: Replaced directional rod modules with unified `rod_between(p1, p2)` using `hull()` between two spheres at endpoints. This ensures precise corner-to-corner connections.

**Verification**: All views (isometric, front, back, left, right, top) rendered cleanly with no protrusions.
- Final model: Manifold, 5313 vertices, 11010 facets, genus 97

#### Phase 4: Bracing Options Expansion
Added flexible bracing configuration:

1. **Bracing Type Selection**
   - `enable_x_bracing`: X-pattern (two diagonals per face)
   - `enable_z_bracing`: Z-pattern (single diagonal per face)
   - Mutually exclusive options

2. **Per-Side Control**
   - `bracing_front`, `bracing_back`, `bracing_left`, `bracing_right`
   - Independent control for each of the 4 faces

3. **Z-Bracing Direction**
   - `z_bracing_direction = "forward"` (/ pattern)
   - `z_bracing_direction = "backward"` (\ pattern)

**Test Renders Verified**:
| Configuration | Vertices | Facets | Genus |
|---------------|----------|--------|-------|
| X-bracing all sides | 5305 | 10994 | 97 |
| X-bracing front only | 1067 | 2190 | 15 |
| Z-bracing all sides | 1182 | 2428 | 17 |
| Z-bracing forward (front only) | 865 | 1770 | 11 |
| Z-bracing backward (front only) | 861 | 1762 | 11 |
| No bracing | 754 | 1540 | 9 |
| Left+Right only | 1364 | 2808 | 21 |

#### Phase 5: Project Naming & Documentation
- Named project **"Tesserae"** — from Latin for mosaic tiles, reflecting modular construction
- Created project structure at `/home/bn/.local/src/tesserae/`
- Wrote README.md with full parameter documentation
- Documented development history (this file)

#### Phase 6: Spotlight Import Integration
- Downloaded IKEA HEKTAR Wand-Klemmspot 3D model (GLB format)
- Converted GLB → STL using Blender + Python (trimesh/manual export)
  - Original: `HEKTAR Wand-Klemmspot - dunkelgrau (80215308)-mini.glb` (237 KB)
  - Exported: `media/spotlight.stl` (10.5 MB ASCII, 16,658 vertices)
  - Dimensions: ~10.8 × 22 × 31 cm (real-world scale)
- Added spotlight configuration parameters and `spotlight_at(z_center)` module
- Places one spotlight per section at vertical center with configurable scale/rotation/offset

#### Phase 7: Geometry Refactor & BOSL2 Integration
- Renamed frame dimensions to per-section dimensions:
  - `frame_width` → `section_width`
  - `frame_depth` → `section_depth`
  - `frame_height` replaced by `section_height * num_sections`
- Integrated BOSL2 primitives
- Replaced axis-aligned cylinders with BOSL2-based geometry for posts and rings
- Kept diagonal/bracing logic separate for iterative experimentation

#### Phase 8: Tube-Based Structure and Offset Controls
- Replaced `rod_diameter` with:
  - `rod_od` (outer diameter)
  - `rod_id` (inner diameter, `0` for solid rods)
- Switched structural members to BOSL2 `tube()` for hollow tube modeling
- Added `vertical_post_offset_mode`:
  - `"inside"`
  - `"outside"`
  - `"topright"`
- Changed `corner_offset` behavior:
  - Vertical posts move inward/outward as configured
  - Horizontal rings keep full span to preserve overlap for real connectors
- Horizontal ring placement updated so `xcyl` and `ycyl` both respond correctly to offsets

#### Phase 9: Bracing Simplification
- Removed endpoint-driven `rod_between()` / `diagonal_tube()` approach
- Added `bracing_angle` parameter to describe braces relative to vertical
- Implemented angle-driven braces using BOSL2 `tube()`:
  - `enable_z_bracing`: one clockwise brace per enabled face
  - `enable_x_bracing`: one clockwise and one counter-clockwise brace per enabled face
- Fixed OpenSCAD scoping issue in `angled_brace()` by replacing block-local assignment with ternary assignment
- Verified CLI renders from isometric and all orthographic axes

---

## Current Status

✅ **Complete**:
- Parametric multi-section frame model with section-based dimensions
- Hollow or solid tube modeling via `rod_od` / `rod_id`
- Horizontal ring overlap behavior for connector approximation
- Vertical post offset modes and ring/post offset controls
- Angle-driven X/Z bracing per enabled face
- Imported spotlight placement in each section
- BOSL2-based tube geometry throughout primary structure
- Documentation updated for current parameter set

⏳ **Future Enhancements**:
- [ ] Custom spotlight mount/connectors for physical fabrication
- [ ] Connector/joint designs for physical fabrication
- [ ] Material thickness calculations for metal tubing
- [ ] Cable management integration
- [ ] Base plate design for stability
- [ ] Spotlight mount variants
- [ ] Assembly instructions

---

## Technical Notes

### OpenSCAD Version
- Developed with OpenSCAD v2026.05.31
- Uses BOSL2 `tube()` for hollow structural members
- Angle-driven brace placement uses standard OpenSCAD vector math

### Key Design Decisions

1. **Tube Modeling**: BOSL2 `tube()` provides cleaner hollow-member geometry than custom boolean wrappers

2. **Connector Approximation**: `corner_offset` now moves posts without shortening horizontal members, preserving overlap for real connectors

3. **Bracing Strategy**: Braces are controlled by angle relative to vertical rather than exact endpoint targeting, matching pre-cut tube fabrication better

4. **Parameter Organization**: All user-adjustable values grouped at top of file for easy modification

5. **Scale**: 1 unit = 1 cm (real-world dimensions)

### Known Limitations

- No connector/joint modeling (frame-only design)
- No lamp fixtures or spotlight mounts beyond imported spotlight bodies
- Bracing is angle-driven and not trimmed to exact joints
- Overlapping members can produce non-manifold-looking intersections in some backends, though preview/render works correctly for current workflow
- Requires external fabrication knowledge for real-world build

---

## Render Commands Reference

```bash
# Isometric view
openscad -o lamp_iso.png --projection=p --viewall --render \
  --camera=-30,25,0,35,0,35 lamp_frame.scad

# Front view
openscad -o lamp_front.png --projection=p --viewall --render \
  --camera=0,90,0,0,0,25 lamp_frame.scad

# With custom bracing
openscad -o lamp_custom.png --projection=p --viewall --render \
  --camera=-30,25,0,35,0,35 \
  -D 'enable_x_bracing=false' \
  -D 'enable_z_bracing=true' \
  -D 'bracing_front=true' \
  -D 'bracing_back=false' \
  lamp_frame.scad
```

---

*Last updated: 2026-06-09*

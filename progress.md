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

---

## Current Status

✅ **Complete**:
- Parametric frame model with adjustable dimensions
- Full bracing configuration options (X/Z patterns, per-side control)
- Clean geometry verified across multiple views
- Manifold solid suitable for 3D printing/fabrication
- Documentation complete

⏳ **Future Enhancements**:
- [ ] Lamp fixture/arm attachments (currently excluded per requirements)
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
- Uses `hull()` + `sphere()` technique for clean rod connections
- All modules use proper scoping (no global `return` statements)

### Key Design Decisions

1. **Rod Connection Method**: `rod_between(p1, p2)` with `hull()` ensures manifold geometry and precise endpoint connections

2. **Parameter Organization**: All user-adjustable values grouped at top of file for easy modification

3. **Modular Architecture**: Separate modules for posts, rings, and bracing enable independent testing

4. **Scale**: 1 unit = 1 cm (real-world dimensions)

### Known Limitations

- No connector/joint modeling (frame-only design)
- No lamp fixtures or spotlight mounts
- Flat bottom cut optional (commented out in code)
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

*Last updated: 2026-06-08*

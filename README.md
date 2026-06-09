# Tesserae

A parametric industrial floor lamp frame inspired by lattice/truss tower structures.

![Tesserae Lamp Frame](lamp_iso.png)

## Overview

**Tesserae** is a modular, parametric floor lamp design consisting of a structural rod frame with optional bracing patterns. The name comes from *tesserae* — the small tiles used in ancient mosaics — reflecting the lamp's modular, geometric construction where repeating sections build up a larger pattern.

## Design Philosophy

- **Industrial aesthetic**: Exposed structural elements, no hidden connectors
- **Parametric design**: All dimensions adjustable via variables
- **Modular construction**: Repeating sections stacked vertically
- **Flexible bracing**: Choose X-pattern, Z-pattern, or no bracing per side
- **Integrated spotlights**: Import and place 3D models in each section

## Parameters

### Section Dimensions

| Parameter | Default | Description |
|-----------|---------|-------------|
| `section_width` | 25 cm | Width of each section along x-axis |
| `section_depth` | 25 cm | Depth of each section along y-axis |
| `section_height` | 25 cm | Height of each section along z-axis |

### Structure

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_sections` | 6 | Number of stacked vertical sections |
| `rod_od` | 1.72 cm | Tube outer diameter |
| `rod_id` | `rod_od - 2*0.235` | Tube inner diameter (`0` for solid rods) |
| `corner_offset` | `1.5 * rod_od` | Moves post locations inward while horizontal rods keep full span |
| `rod_connection_offset` | `rod_od` | Vertical offset used to seat horizontal tubes relative to posts |
| `vertical_post_offset_mode` | `"outside"` | Vertical post shift mode: `"inside"`, `"outside"`, or `"topright"` |

### Bracing Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_x_bracing` | `false` | Enable X cross-bracing (two braces per enabled face) |
| `enable_z_bracing` | `true` | Enable Z bracing (single brace per enabled face) |
| `bracing_angle` | `45` | Brace angle measured from vertical; positive values are clockwise when viewed from outside |
| `bracing_front` | `false` | Enable bracing on front face |
| `bracing_back` | `true` | Enable bracing on back face |
| `bracing_left` | `true` | Enable bracing on left face |
| `bracing_right` | `true` | Enable bracing on right face |

### Spotlight Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_spotlights` | `true` | Enable imported spotlight models |
| `spotlight_file` | `"media/spotlight.stl"` | Path to imported 3D model |
| `spotlight_scale` | `1.0` | Scale factor for spotlight size |
| `spotlight_rotation` | `[90, 45, 0]` | Rotation [x, y, z] in degrees |
| `spotlight_offset` | `[4, 19, 3]` | Additional offset from section center |

## Usage

### OpenSCAD

1. Open `lamp_frame.scad` in OpenSCAD
2. Adjust parameters at the top of the file
3. Press F5 to preview, F6 to render
4. Export as STL for 3D printing or DXF/SVG for fabrication

### Example Configurations

```openscad
// Minimal rear/side Z bracing
enable_x_bracing = false;
enable_z_bracing = true;
bracing_angle = 35;
bracing_front = false;
bracing_back = true;
bracing_left = true;
bracing_right = true;

// Heavy duty X bracing on all faces
enable_x_bracing = true;
enable_z_bracing = false;
bracing_angle = 45;
bracing_front = true;
bracing_back = true;
bracing_left = true;
bracing_right = true;

// Solid rods instead of tubes
rod_id = 0;

// Posts pulled inward while keeping ring overlap
corner_offset = 2.5;
vertical_post_offset_mode = "inside";

// Custom spotlight orientation
enable_spotlights = true;
spotlight_scale = 1.5;
spotlight_rotation = [90, 0, 0];
```

## Files

| File | Description |
|------|-------------|
| `lamp_frame.scad` | Main parametric OpenSCAD model |
| `README.md` | This file |
| `progress.md` | Development history and notes |

## Fabrication Notes

- Designed for metal tubing (steel, aluminum, or brass)
- Default tube size is approximately 17.2 mm OD with ~2.35 mm wall
- Set `rod_id = 0` to model solid rods instead of tubes
- `corner_offset` is intended to approximate overlap needed for real connectors or welded joints
- Horizontal rings keep their full span even when posts are moved inward, so overlap is preserved
- Braces are angle-driven rather than exact endpoint-driven, which is useful when selecting pre-cut stock lengths
- Scale factor: 1 unit = 1 cm in real world

## License

[Add your license here]

---

*Tesserae — building light from geometric modules.*

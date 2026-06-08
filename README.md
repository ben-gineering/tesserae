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

### Overall Dimensions

| Parameter | Default | Description |
|-----------|---------|-------------|
| `frame_width` | 30 cm | Width along x-axis |
| `frame_depth` | 30 cm | Depth along y-axis |
| `frame_height` | 165 cm | Total height |

### Structure

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_sections` | 6 | Number of vertical sections |
| `rod_diameter` | 1.8 cm | Diameter of all rods/tubes |
| `corner_offset` | 0 cm | Offset from corners for aesthetic |

### Bracing Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_x_bracing` | `true` | Enable X cross-bracing (two diagonals) |
| `enable_z_bracing` | `false` | Enable Z bracing (single diagonal) |
| `bracing_front` | `true` | Enable bracing on front face |
| `bracing_back` | `true` | Enable bracing on back face |
| `bracing_left` | `true` | Enable bracing on left face |
| `bracing_right` | `true` | Enable bracing on right face |
| `z_bracing_direction` | `"forward"` | Diagonal direction: `"forward"` (/) or `"backward"` (\) |

### Spotlight Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_spotlights` | `true` | Enable imported spotlight models |
| `spotlight_file` | `"media/spotlight.stl"` | Path to imported 3D model |
| `spotlight_scale` | `1.0` | Scale factor for spotlight size |
| `spotlight_rotation` | `[0, 0, 0]` | Rotation [x, y, z] in degrees |
| `spotlight_offset` | `[0, 0, 0]` | Additional offset from section center |

## Usage

### OpenSCAD

1. Open `lamp_frame.scad` in OpenSCAD
2. Adjust parameters at the top of the file
3. Press F5 to preview, F6 to render
4. Export as STL for 3D printing or DXF/SVG for fabrication

### Example Configurations

```openscad
// Minimal bracing (front only, Z-pattern)
enable_x_bracing = false;
enable_z_bracing = true;
z_bracing_direction = "forward";
bracing_front = true;
bracing_back = false;
bracing_left = false;
bracing_right = false;

// Heavy duty (all sides, X-pattern)
enable_x_bracing = true;
enable_z_bracing = false;
bracing_front = true;
bracing_back = true;
bracing_left = true;
bracing_right = true;

// Asymmetric design
enable_x_bracing = true;
bracing_front = true;
bracing_back = false;
bracing_left = true;
bracing_right = false;

// With custom spotlight orientation
enable_spotlights = true;
spotlight_scale = 1.5;
spotlight_rotation = [-90, 0, 0];  // Point forward
```

## Files

| File | Description |
|------|-------------|
| `lamp_frame.scad` | Main parametric OpenSCAD model |
| `README.md` | This file |
| `progress.md` | Development history and notes |

## Fabrication Notes

- Designed for metal tubing (steel, aluminum, or brass)
- Rod diameter: 18mm recommended for full-scale (165cm height)
- Connections require custom fittings or welding
- Scale factor: 1 unit = 1 cm in real world

## License

[Add your license here]

---

*Tesserae — building light from geometric modules.*

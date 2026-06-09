// Parametric Industrial Lamp Frame
// Based on lattice/truss tower design
// Only structural rods (no connectors, no lamp fixtures)
// Uses BOSL2 for enhanced primitives

include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>

// ==================== PARAMETERS ====================

// Section dimensions
section_width = 25;      // Width of each section in cm (x-axis)
section_depth = 25;      // Depth of each section in cm (y-axis)
section_height = 25;     // Height of each section in cm (z-axis)

// Structure parameters
num_sections = 2;      // Number of vertical sections
rod_od = 1.72;         // Rod/tube outer diameter in cm
rod_id = 1.22;         // Rod/tube inner diameter in cm (set to 0 for solid rods)
corner_offset = 1.5 * rod_od;     // Offset from corners for aesthetic (0 = centered on corner)
rod_connection_offset = rod_od;  // Rod offset for edge alignment: 0=centered, ±(rod_od/2)=flush edges
// Each rod offset in axes perpendicular to its own axis:
//   zcyl (vertical): X and Y | xcyl (X-axis): Y only | ycyl (Y-axis): X only
vertical_post_offset_mode = "outside";  // How vertical posts are offset: "inside", "outside", "topright"

// Bracing pattern
enable_x_bracing = false;   // Enable X cross-bracing (two diagonals) in each section
enable_z_bracing = true;  // Enable Z bracing (single diagonal) - mutually exclusive with X bracing
enable_horizontal = true;  // Enable horizontal rings at each section

// Spotlight configuration
enable_spotlights = true;  // Enable imported spotlight models
spotlight_file = "media/spotlight.stl";  // Path to imported 3D model
spotlight_scale = 1.0;  // Scale factor (model already in cm: ~11x22x31 cm)
spotlight_rotation = [90, 45, 0];  // Rotation [x, y, z] degrees
spotlight_offset = [4, 19, 3];  // Additional offset from section center

// Per-side bracing control (applies to both X and Z bracing)
bracing_front = false;   // Front face (y = min)
bracing_back = true;    // Back face (y = max)
bracing_left = true;    // Left face (x = min)
bracing_right = true;   // Right face (x = max)

// Z bracing direction (which way the diagonal runs)
z_bracing_direction = "forward"; // "forward" (/) or "backward" (\) when viewed from outside

// ==================== DERIVED VALUES ====================

half_rod = rod_od / 2;
wall_thickness = (rod_od - rod_id) / 2;

// Vertical post positions (adjusted for corner_offset and rod centering)
x_positions = [
    -section_width/2 + corner_offset + half_rod,
    section_width/2 - corner_offset - half_rod
];
y_positions = [
    -section_depth/2 + corner_offset + half_rod,
    section_depth/2 - corner_offset - half_rod
];

// Full-width corner positions for horizontal rod lengths (ignores corner_offset)
x_full = [-section_width/2 + half_rod, section_width/2 - half_rod];
y_full = [-section_depth/2 + half_rod, section_depth/2 - half_rod];

// ==================== MODULES ====================

// Create a rod between two points using hull of spheres
// Works for any orientation (axis-aligned or diagonal)
module rod_between(p1, p2) {
    hull() {
        translate(p1) sphere(d = rod_od, $fn = 16);
        translate(p2) sphere(d = rod_od, $fn = 16);
    }
}

// Note: diagonal_rod is now rod_between (same functionality)

// Create X bracing for one section
module x_bracing(z_base, section_h) {
    if (enable_x_bracing) {
        // Front face X (y = y_positions[0])
        if (bracing_front) {
        rod_between([x_positions[0], y_positions[0], z_base], [x_positions[1], y_positions[0], z_base + section_h]);
        rod_between([x_positions[1], y_positions[0], z_base], [x_positions[0], y_positions[0], z_base + section_h]);
    }
    
    // Back face X (y = y_positions[1])
    if (bracing_back) {
        rod_between([x_positions[0], y_positions[1], z_base], [x_positions[1], y_positions[1], z_base + section_h]);
        rod_between([x_positions[1], y_positions[1], z_base], [x_positions[0], y_positions[1], z_base + section_h]);
    }
    
    // Left face X (x = x_positions[0])
    if (bracing_left) {
        rod_between([x_positions[0], y_positions[0], z_base], [x_positions[0], y_positions[1], z_base + section_h]);
        rod_between([x_positions[0], y_positions[1], z_base], [x_positions[0], y_positions[0], z_base + section_h]);
    }
    
        // Right face X (x = x_positions[1])
        if (bracing_right) {
            rod_between([x_positions[1], y_positions[0], z_base], [x_positions[1], y_positions[1], z_base + section_h]);
            rod_between([x_positions[1], y_positions[1], z_base], [x_positions[1], y_positions[0], z_base + section_h]);
        }
    }
}

// Create Z bracing for one section (single diagonal per side)
module z_bracing(z_base, section_h) {
    if (enable_z_bracing) {
    
    // Determine diagonal direction
    forward = (z_bracing_direction == "forward");
    
    // Front face Z (y = y_positions[0])
    if (bracing_front) {
        if (forward) {
            rod_between([x_positions[0], y_positions[0], z_base], [x_positions[1], y_positions[0], z_base + section_h]);
        } else {
            rod_between([x_positions[1], y_positions[0], z_base], [x_positions[0], y_positions[0], z_base + section_h]);
        }
    }
    
    // Back face Z (y = y_positions[1]) - viewed from outside, so direction is reversed
    if (bracing_back) {
        if (forward) {
            rod_between([x_positions[1], y_positions[1], z_base], [x_positions[0], y_positions[1], z_base + section_h]);
        } else {
            rod_between([x_positions[0], y_positions[1], z_base], [x_positions[1], y_positions[1], z_base + section_h]);
        }
    }
    
    // Left face Z (x = x_positions[0]) - viewed from outside
    if (bracing_left) {
        if (forward) {
            rod_between([x_positions[0], y_positions[1], z_base], [x_positions[0], y_positions[0], z_base + section_h]);
        } else {
            rod_between([x_positions[0], y_positions[0], z_base], [x_positions[0], y_positions[1], z_base + section_h]);
        }
    }
    
        // Right face Z (x = x_positions[1]) - viewed from outside
        if (bracing_right) {
            if (forward) {
                rod_between([x_positions[1], y_positions[0], z_base], [x_positions[1], y_positions[1], z_base + section_h]);
            } else {
                rod_between([x_positions[1], y_positions[1], z_base], [x_positions[1], y_positions[0], z_base + section_h]);
            }
        }
    }
}

// Create horizontal ring at a given height using BOSL2 axis-aligned cylinders
module horizontal_ring(z_height) {
    if (enable_horizontal) {
        // Rod endpoint positions (with corner_offset for post alignment)
        fl = [x_positions[0], y_positions[0], z_height];  // front-left
        fr = [x_positions[1], y_positions[0], z_height];  // front-right
        bl = [x_positions[0], y_positions[1], z_height];  // back-left
        br = [x_positions[1], y_positions[1], z_height];  // back-right
        
        // Full-length endpoints (for rod length, ignoring corner_offset)
        fl_full = [x_full[0], y_full[0], z_height];
        fr_full = [x_full[1], y_full[0], z_height];
        bl_full = [x_full[0], y_full[1], z_height];
        br_full = [x_full[1], y_full[1], z_height];
        
        // Front horizontal (along X) - use tube oriented along X axis
        mid_x_front = (fl + fr) / 2;  // Position based on posts
        translate(mid_x_front + [0, 0, -rod_connection_offset])
            tube(l = norm(fr_full - fl_full), od = rod_od, id = rod_id, orient = RIGHT, $fn = 32);
        
        // Back horizontal (along X)
        mid_x_back = (bl + br) / 2;
        translate(mid_x_back + [0, 0, -rod_connection_offset])
            tube(l = norm(br_full - bl_full), od = rod_od, id = rod_id, orient = RIGHT, $fn = 32);
        
        // Left horizontal (along Y) - use tube oriented along Y axis
        // Position Y-midpoint based on posts (respects corner_offset)
        // But length spans full depth (ignores corner_offset)
        mid_y_left = [(fl[0] + bl[0])/2, (fl_full[1] + bl_full[1])/2, z_height];
        translate(mid_y_left + [0, 0, 0])
            tube(l = norm(bl_full - fl_full), od = rod_od, id = rod_id, orient = BACK, $fn = 32);
        
        // Right horizontal (along Y)
        mid_y_right = [(fr[0] + br[0])/2, (fr_full[1] + br_full[1])/2, z_height];
        translate(mid_y_right + [0, 0, 0])
            tube(l = norm(br_full - fr_full), od = rod_od, id = rod_id, orient = BACK, $fn = 32);
    }
}

// Import and place spotlight in center of section
module spotlight_at(z_center) {
    if (enable_spotlights) {
        translate([0, 0, z_center])
        translate(spotlight_offset)
        rotate(spotlight_rotation)
        scale(spotlight_scale)
        color("#222222")
        import(spotlight_file);
    }
}

// Create one complete section
module lamp_section(section_idx) {
    z_base = section_idx * section_height;
    z_center = z_base + section_height / 2;
    
    // Horizontal rings
    horizontal_ring(z_base);
    
    // Bracing (X or Z, not both)
    if (enable_x_bracing) {
        x_bracing(z_base, section_height);
    } else if (enable_z_bracing) {
        z_bracing(z_base, section_height);
    }
    
    // Spotlight in center of section
    spotlight_at(z_center);
}

// Determine vertical post offset direction based on mode
function get_post_offset(px, py) = 
    vertical_post_offset_mode == "inside" ? [
        px < 0 ? rod_connection_offset : -rod_connection_offset,
        py < 0 ? rod_connection_offset : -rod_connection_offset
    ] :
    vertical_post_offset_mode == "outside" ? [
        px < 0 ? -rod_connection_offset : rod_connection_offset,
        py < 0 ? -rod_connection_offset : rod_connection_offset
    ] : // topright (default)
        [rod_connection_offset, rod_connection_offset];

// Create all four vertical corner posts using BOSL2 zcyl
// Vertical posts offset in BOTH X and Y (perpendicular to Z axis)
module vertical_posts() {
    total_height = num_sections * section_height;
    
    for (i = [0:1]) {
        for (j = [0:1]) {
            px = x_positions[i];
            py = y_positions[j];
            offset = get_post_offset(px, py);
            translate([px + offset[0], py + offset[1], total_height/2])
                tube(h = total_height, od = rod_od, id = rod_id, $fn = 32);
        }
    }
}

// ==================== MAIN ASSEMBLY ====================

module lamp_frame() {
    difference() {
        union() {
            // Vertical corner posts
            vertical_posts();
            
            // Each section with bracing
            for (i = [0 : num_sections - 1]) {
                lamp_section(i);
            }
            
            // Top ring
            horizontal_ring(num_sections * section_height);
        }
        // Optional: cut flat bottom for stability
        // translate([-frame_width, -frame_depth, -1])
        // cube([frame_width*2, frame_depth*2, 2]);
    }
}

// Render the lamp frame
scale(1) // Scale factor (1 = 1 unit = 1 cm in real world)
lamp_frame();

// ==================== REFERENCE CUBE (commented out) ====================
// Uncomment to show reference grid
// color("lightgray", 0.3)
// translate([-section_width/2, -section_depth/2, 0])
// cube([section_width, section_depth, num_sections * section_height]);

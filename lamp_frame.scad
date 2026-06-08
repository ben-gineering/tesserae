// Parametric Industrial Lamp Frame
// Based on lattice/truss tower design
// Only structural rods (no connectors, no lamp fixtures)

// ==================== PARAMETERS ====================

// Overall dimensions
frame_width = 25;      // Width in cm (x-axis)
frame_depth = 25;      // Depth in cm (y-axis)
frame_height = 50;    // Total height in cm (z-axis)

// Structure parameters
num_sections = 2;      // Number of vertical sections
rod_diameter = 1;    // Rod/tube diameter in cm
corner_offset = 0;     // Offset from corners for aesthetic (0 = centered on corner)

// Bracing pattern
enable_x_bracing = false;   // Enable X cross-bracing (two diagonals) in each section
enable_z_bracing = true;  // Enable Z bracing (single diagonal) - mutually exclusive with X bracing
enable_horizontal = true;  // Enable horizontal rings at each section

// Per-side bracing control (applies to both X and Z bracing)
bracing_front = false;   // Front face (y = min)
bracing_back = true;    // Back face (y = max)
bracing_left = true;    // Left face (x = min)
bracing_right = true;   // Right face (x = max)

// Z bracing direction (which way the diagonal runs)
z_bracing_direction = "forward"; // "forward" (/) or "backward" (\) when viewed from outside

// ==================== DERIVED VALUES ====================

section_height = frame_height / num_sections;
half_rod = rod_diameter / 2;

// Corner positions (adjusted for rod centering)
x_positions = [
    -frame_width/2 + corner_offset + half_rod,
    frame_width/2 - corner_offset - half_rod
];
y_positions = [
    -frame_depth/2 + corner_offset + half_rod,
    frame_depth/2 - corner_offset - half_rod
];

// ==================== MODULES ====================

// Create a single rod along Z axis
module rod_z(height) {
    cylinder(h = height, d = rod_diameter, $fn = 16);
}

// Create a rod from point p1 to point p2 using hull
module rod_between(p1, p2) {
    hull() {
        translate(p1) sphere(d = rod_diameter, $fn = 16);
        translate(p2) sphere(d = rod_diameter, $fn = 16);
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

// Create horizontal ring at a given height
module horizontal_ring(z_height) {
    if (enable_horizontal) {
        // Define corner points at this height
        front_left = [x_positions[0], y_positions[0], z_height];
        front_right = [x_positions[1], y_positions[0], z_height];
        back_left = [x_positions[0], y_positions[1], z_height];
        back_right = [x_positions[1], y_positions[1], z_height];
        
        // Front horizontal (along X)
        rod_between(front_left, front_right);
        
        // Back horizontal (along X)
        rod_between(back_left, back_right);
        
        // Left horizontal (along Y)
        rod_between(front_left, back_left);
        
        // Right horizontal (along Y)
        rod_between(front_right, back_right);
    }
}

// Create one complete section
module lamp_section(section_idx) {
    z_base = section_idx * section_height;
    
    // Horizontal rings
    horizontal_ring(z_base);
    
    // Bracing (X or Z, not both)
    if (enable_x_bracing) {
        x_bracing(z_base, section_height);
    } else if (enable_z_bracing) {
        z_bracing(z_base, section_height);
    }
}

// Create all four vertical corner posts
module vertical_posts() {
    for (x = x_positions) {
        for (y = y_positions) {
            translate([x, y, 0])
            rod_z(frame_height);
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
            horizontal_ring(frame_height);
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
// translate([-frame_width/2, -frame_depth/2, 0])
// cube([frame_width, frame_depth, frame_height]);

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
num_sections = 6;      // Number of vertical sections
rod_od = 1.72;         // Rod/tube outer diameter in cm
rod_id = rod_od - 2*0.235;         // Rod/tube inner diameter in cm (set to 0 for solid rods)
bracing_angle = 45;    // Bracing angle from vertical (degrees). Positive=clockwise when viewed from outside
bracing_length = 25;    // Fixed brace length in cm. 0 = auto-fit to face height/angle
corner_offset = 1.5 * rod_od;     // Offset from corners for aesthetic (0 = centered on corner)
rod_connection_offset = rod_od;  // Rod offset for edge alignment: 0=centered, ±(rod_od/2)=flush edges
// Each rod offset in axes perpendicular to its own axis:
//   zcyl (vertical): X and Y | xcyl (X-axis): Y only | ycyl (Y-axis): X only
vertical_post_offset_mode = "outside";  // How vertical posts are offset: "inside", "outside", "topright"

// Bracing pattern
enable_x_bracing = false;   // Enable X cross-bracing (two diagonals) in each section
enable_z_bracing = false;  // Enable Z bracing (single diagonal) - mutually exclusive with X bracing
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

// Create tube between two arbitrary 3D points
module brace_between(p1, p2, length_override = 0) {
    v = p2 - p1;
    full_len = norm(v);
    len = length_override > 0 ? min(length_override, full_len) : full_len;
    start = length_override > 0 ? p1 + (v/full_len) * ((full_len - len)/2) : p1;

    translate(start)
        rot(from=UP, to=v)
            tube(h = len, od = rod_od, id = rod_id, anchor = BOTTOM, $fn = 32);
}

// Create angled brace on a face
// center_pos: brace center on the face
// face_span: horizontal span available in face plane
// height: vertical height of face
// angle_deg: angle from vertical (positive=clockwise when viewed from outside)
// axis: BACK for XZ faces, RIGHT for YZ faces
module angled_brace(center_pos, face_span, height, angle_deg, axis) {
    auto_len = min(height / cos(angle_deg), face_span / max(0.001, abs(sin(angle_deg))));
    len = bracing_length > 0 ? bracing_length : auto_len;
    half_vert = (len * cos(angle_deg)) / 2;
    half_horiz = (len * sin(angle_deg)) / 2;
    delta = axis == RIGHT ? [0, half_horiz, half_vert] : [half_horiz, 0, half_vert];
    brace_between(center_pos - delta, center_pos + delta, 0);
}

// Create X bracing for one section (two diagonals per enabled face)
module x_bracing(z_base, section_h) {
    if (enable_x_bracing) {
        // Calculate face dimensions
        face_width_x = x_positions[1] - x_positions[0];  // Width of front/back faces
        face_width_y = y_positions[1] - y_positions[0];  // Width of left/right faces
        
        // Front face X bracing (XZ plane at y=min)
        if (bracing_front) {
            face_center = [0, y_positions[0], z_base + section_h/2];
            angled_brace(face_center, face_width_x, section_h, bracing_angle, BACK);
            angled_brace(face_center, face_width_x, section_h, -bracing_angle, BACK);
        }
        
        // Back face X bracing (XZ plane at y=max)
        if (bracing_back) {
            face_center = [0, y_positions[1], z_base + section_h/2];
            angled_brace(face_center, face_width_x, section_h, bracing_angle, BACK);
            angled_brace(face_center, face_width_x, section_h, -bracing_angle, BACK);
        }
        
        // Left face X bracing (YZ plane at x=min)
        if (bracing_left) {
            face_center = [x_positions[0], 0, z_base + section_h/2];
            angled_brace(face_center, face_width_y, section_h, bracing_angle, RIGHT);
            angled_brace(face_center, face_width_y, section_h, -bracing_angle, RIGHT);
        }
        
        // Right face X bracing (YZ plane at x=max)
        if (bracing_right) {
            face_center = [x_positions[1], 0, z_base + section_h/2];
            angled_brace(face_center, face_width_y, section_h, bracing_angle, RIGHT);
            angled_brace(face_center, face_width_y, section_h, -bracing_angle, RIGHT);
        }
    }
}

// Create Z bracing for one section (single diagonal per side)
// Create Z bracing for one section (single diagonal per enabled face)
// Uses bracing_angle parameter, always clockwise when viewed from outside
module z_bracing(z_base, section_h) {
    if (enable_z_bracing) {
    
    // Calculate face dimensions
    face_width_x = x_positions[1] - x_positions[0];  // Width of front/back faces
    face_width_y = y_positions[1] - y_positions[0];  // Width of left/right faces
    
    // Front face Z (XZ plane at y=min)
    if (bracing_front) {
        angled_brace([0, y_positions[0], z_base + section_h/2], face_width_x, section_h, bracing_angle, BACK);
    }
    
    // Back face Z (XZ plane at y=max)
    if (bracing_back) {
        angled_brace([0, y_positions[1], z_base + section_h/2], face_width_x, section_h, bracing_angle, BACK);
    }
    
    // Left face Z (YZ plane at x=min)
    if (bracing_left) {
        angled_brace([x_positions[0], 0, z_base + section_h/2], face_width_y, section_h, bracing_angle, RIGHT);
    }
    
    // Right face Z (YZ plane at x=max)
    if (bracing_right) {
        angled_brace([x_positions[1], 0, z_base + section_h/2], face_width_y, section_h, bracing_angle, RIGHT);
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
        color("#333333")
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

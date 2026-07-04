// QR code tag for filament-swap printing
// Generates a printable tag with raised QR modules on a flat base.
// URL encoded in QR: https://bengineering45.odoo.com/

include <media/odoo_qr_modules.scad>

url = "https://bengineering45.odoo.com/";

// Tag dimensions (mm)
tag_width = 50;
tag_height = 65;
tag_thickness = 1.6;
corner_radius = 3;

// Raised QR settings (mm)
qr_size = 38;
qr_modules_per_side = 25;  // active QR pattern size
qr_raise = 1.0;   // enough for a clean filament-swap top layer
qr_margin = 0;

// Hole
hole_diameter = 4;
hole_offset_y = 10;

// Border around QR area (mm)
qr_top_margin = 20;
qr_bottom_margin = 8;

$fn = 48;

module rounded_tag(w, h, r, t) {
    linear_extrude(height=t)
        hull() {
            for (x = [-w/2 + r, w/2 - r])
                for (y = [-h/2 + r, h/2 - r])
                    translate([x, y]) circle(r=r);
        }
}

module base_tag() {
    difference() {
        rounded_tag(tag_width, tag_height, corner_radius, tag_thickness);
        translate([0, tag_height/2 - hole_offset_y, -0.1])
            cylinder(h=tag_thickness + 0.2, d=hole_diameter);
    }
}

module raised_qr() {
    qr_area_h = qr_size;
    qr_center_y = (tag_height/2 - qr_top_margin - qr_area_h/2);
    module_pitch = qr_size / qr_modules_per_side;

    translate([0, qr_center_y, tag_thickness])
        linear_extrude(height=qr_raise)
            union() {
                for (m = qr_modules)
                    translate([
                        (m[0] - qr_modules_per_side/2) * module_pitch + module_pitch/2,
                        ((qr_modules_per_side - 1 - m[1]) - qr_modules_per_side/2) * module_pitch + module_pitch/2
                    ])
                        square([module_pitch, module_pitch], center=true);
            }
}

base_tag();
color("black") raised_qr();

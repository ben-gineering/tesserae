include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <BOSL2/screws.scad>
$fn=50;

module lamp_mount(u) {
mount_depth = 30;
mount_width = 35;
mount_height = 20 - 5;
screw_distance = 22;

difference(){
  cuboid([mount_depth,mount_width,mount_height],rounding=5,except=BOT);
  ycopies(screw_distance) zmove(mount_height/2) screw_hole("M4,20", head="socket", anchor=TOP, $fn=32);
  zmove(-mount_height/2 + u/2) xcyl(d=u, l=mount_depth+1);
  zmove(-mount_height/2 + u/4) cuboid([mount_depth+1,u,u/2]);
  };
};

lamp_mount(10);

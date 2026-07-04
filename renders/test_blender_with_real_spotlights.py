import bpy, math
from mathutils import Vector
OUT='/home/bn/.local/src/tesserae/renders/test_real_spotlights.png'
FRAME='/home/bn/.local/src/tesserae/renders/tesserae_2sec_frameonly.stl'
SPOT='/home/bn/.local/src/tesserae/media/spotlight.stl'
section_height=25
num_sections=2
spotlight_offset=(4,19,3)
spotlight_rotation=(90,45,0)
spotlight_scale=1.0

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
world=bpy.data.worlds['World']
world.use_nodes=True
bg=world.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(0.93,0.93,0.92,1)
bg.inputs['Strength'].default_value=0.6

# materials
frame_mat=bpy.data.materials.new('Frame')
frame_mat.use_nodes=True
bsdf=frame_mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value=(0.08,0.08,0.09,1)
bsdf.inputs['Metallic'].default_value=0.9
bsdf.inputs['Roughness'].default_value=0.42

spot_mat=bpy.data.materials.new('Spot')
spot_mat.use_nodes=True
sbsdf=spot_mat.node_tree.nodes['Principled BSDF']
sbsdf.inputs['Base Color'].default_value=(0.12,0.12,0.13,1)
sbsdf.inputs['Metallic'].default_value=0.75
sbsdf.inputs['Roughness'].default_value=0.48

# import frame
bpy.ops.wm.stl_import(filepath=FRAME)
frame=bpy.context.selected_objects[0]
frame.data.materials.append(frame_mat)

# import spotlights
for i in range(num_sections):
    z_center=i*section_height + section_height/2
    bpy.ops.wm.stl_import(filepath=SPOT)
    obj=bpy.context.selected_objects[0]
    obj.data.materials.append(spot_mat)
    obj.location = (spotlight_offset[0], spotlight_offset[1], z_center + spotlight_offset[2])
    obj.rotation_euler = tuple(math.radians(a) for a in spotlight_rotation)
    obj.scale = (spotlight_scale, spotlight_scale, spotlight_scale)

# ground
bpy.ops.mesh.primitive_plane_add(size=10, location=(0,0,0))
plane=bpy.context.object
gmat=bpy.data.materials.new('Ground')
gmat.use_nodes=True
gbsdf=gmat.node_tree.nodes['Principled BSDF']
gbsdf.inputs['Base Color'].default_value=(0.19,0.19,0.19,1)
gbsdf.inputs['Roughness'].default_value=0.65
plane.data.materials.append(gmat)

# lighting
lights=[
    ((4.5,-5.5,6.0),(math.radians(58),0,math.radians(32)),4500,6),
    ((-3.5,4.0,4.5),(math.radians(75),0,math.radians(-55)),1800,9),
    ((0.5,-2.0,7.0),(math.radians(35),0,math.radians(10)),1200,4),
]
for loc,rot,energy,size in lights:
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l=bpy.context.object
    l.data.energy=energy
    l.data.size=size

# camera framing
objs=[o for o in bpy.data.objects if o.type=='MESH']
mins=Vector((1e9,1e9,1e9))
maxs=Vector((-1e9,-1e9,-1e9))
for obj in objs:
    for c in obj.bound_box:
        v=obj.matrix_world @ Vector(c)
        mins=Vector((min(mins[i],v[i]) for i in range(3)))
        maxs=Vector((max(maxs[i],v[i]) for i in range(3)))
center=(mins+maxs)/2
size=max((maxs-mins))
target=center+Vector((0,0,size*0.12))
camloc=target+Vector((size*0.9,-size*2.0,size*0.65))

bpy.ops.object.camera_add(location=camloc)
cam=bpy.context.object
cam.data.lens=75
empty=bpy.data.objects.new('Target',None)
bpy.context.collection.objects.link(empty)
empty.location=target
con=cam.constraints.new(type='TRACK_TO')
con.target=empty
con.track_axis='TRACK_NEGATIVE_Z'
con.up_axis='UP_Y'
bpy.context.scene.camera=cam

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=96
scene.render.resolution_x=1400
scene.render.resolution_y=1000
scene.render.filepath=OUT
scene.render.image_settings.file_format='PNG'
scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.render.render(write_still=True)
print(OUT)

import bpy, math
from mathutils import Vector
OUT='/home/bn/.local/src/tesserae/renders/combined_test_above.png'
MODEL='/home/bn/.local/src/tesserae/renders/tesserae_2sec.stl'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
world=bpy.data.worlds['World']
world.use_nodes=True
bg=world.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(0.94,0.94,0.92,1)
bg.inputs['Strength'].default_value=0.5

# materials
for name, base, met, rough in [
    ('Frame',(0.09,0.09,0.1),0.9,0.4),
]:
    pass
mat=bpy.data.materials.new('Frame')
mat.use_nodes=True
bsdf=mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value=(0.09,0.09,0.1,1)
bsdf.inputs['Metallic'].default_value=0.9
bsdf.inputs['Roughness'].default_value=0.4

bpy.ops.wm.stl_import(filepath=MODEL)
obj=bpy.context.selected_objects[0]
obj.data.materials.append(mat)

# ground
bpy.ops.mesh.primitive_plane_add(size=8, location=(0,0,0))
plane=bpy.context.object
gmat=bpy.data.materials.new('Ground')
gmat.use_nodes=True
gbsdf=gmat.node_tree.nodes['Principled BSDF']
gbsdf.inputs['Base Color'].default_value=(0.2,0.2,0.2,1)
gbsdf.inputs['Roughness'].default_value=0.6
plane.data.materials.append(gmat)

# lights
for loc,rot,energy,size in [
    ((4,-4,5),(math.radians(60),0,math.radians(35)),5000,5),
    ((-3,3,4),(math.radians(75),0,math.radians(-45)),1800,8),
    ((0,-3,7),(math.radians(35),0,0),1800,4),
]:
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l=bpy.context.object
    l.data.energy=energy
    l.data.size=size

bbox=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
center=sum(bbox, Vector((0,0,0)))/8
size=max((v-center).length for v in bbox)

target=center+Vector((0,0,size*0.25))
camloc=target+Vector((size*1.7,-size*2.4,size*1.4))
bpy.ops.object.camera_add(location=camloc)
cam=bpy.context.object
cam.data.lens=70
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

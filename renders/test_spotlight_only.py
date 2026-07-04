import bpy, math
from mathutils import Vector, Euler
out='/home/bn/.local/src/tesserae/renders/spotlight_only_test.png'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
world=bpy.data.worlds['World']
world.use_nodes=True
bg=world.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(0.9,0.9,0.9,1)
bg.inputs['Strength'].default_value=0.8

mat=bpy.data.materials.new('Mat')
mat.use_nodes=True
bsdf=mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value=(0.1,0.1,0.1,1)
bsdf.inputs['Metallic'].default_value=0.8
bsdf.inputs['Roughness'].default_value=0.4

bpy.ops.wm.stl_import(filepath='/home/bn/.local/src/tesserae/media/spotlight.stl')
obj=bpy.context.selected_objects[0]
obj.data.materials.append(mat)
bpy.ops.object.light_add(type='AREA', location=(3,-4,4), rotation=(math.radians(60),0,math.radians(30)))
light=bpy.context.object
light.data.energy=5000
light.data.size=6

bbox=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
center=sum(bbox, Vector((0,0,0)))/8
size=max((v-center).length for v in bbox)

bpy.ops.object.camera_add(location=center+Vector((size*1.8,-size*2.3,size*1.2)))
cam=bpy.context.object
con=cam.constraints.new(type='TRACK_TO')
empty=bpy.data.objects.new('Target',None)
bpy.context.collection.objects.link(empty)
empty.location=center+Vector((0,0,size*0.1))
con.target=empty
con.track_axis='TRACK_NEGATIVE_Z'
con.up_axis='UP_Y'
bpy.context.scene.camera=cam

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=64
scene.render.resolution_x=1200
scene.render.resolution_y=1200
scene.render.filepath=out
scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True)
print(out)

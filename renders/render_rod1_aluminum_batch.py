import bpy, math, os, sys
from mathutils import Vector

ROOT='/home/bn/.local/src/tesserae/renders'
OUT=os.path.join(ROOT,'website')
os.makedirs(OUT, exist_ok=True)
SPOT='/home/bn/.local/src/tesserae/media/spotlight.stl'
section_height=25
spotlight_offset=(4,19,3)
spotlight_rotation=(90,45,0)
variant = sys.argv[-1] if '--' in sys.argv else '2sec'

CFG={
    '2sec': dict(frame=os.path.join(ROOT,'tesserae_2sec_frameonly_rod1.stl'), num_sections=2, prefix='tesserae_2sec_rod1_aluminum'),
    '6sec': dict(frame=os.path.join(ROOT,'tesserae_6sec_frameonly_rod1.stl'), num_sections=6, prefix='tesserae_6sec_rod1_aluminum'),
}[variant]

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def mat(name, base, metallic, rough):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*base,1)
    b.inputs['Metallic'].default_value=metallic
    b.inputs['Roughness'].default_value=rough
    return m

def add_light(loc, rot, energy, size, color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l=bpy.context.object
    l.data.energy=energy
    l.data.size=size
    l.data.color=color

def bounds(objs):
    pts=[]
    for obj in objs:
        for c in obj.bound_box:
            pts.append(obj.matrix_world @ Vector(c))
    mins=Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    maxs=Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (mins+maxs)/2, max(maxs-mins)

def import_stl(path, material):
    bpy.ops.wm.stl_import(filepath=path)
    o=bpy.context.selected_objects[0]
    o.data.materials.append(material)
    return o

def setup_world():
    w=bpy.data.worlds['World']
    w.use_nodes=True
    bg=w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value=(0.95,0.95,0.94,1)
    bg.inputs['Strength'].default_value=0.6

def add_ground():
    bpy.ops.mesh.primitive_plane_add(size=16, location=(0,0,0))
    g=bpy.context.object
    g.data.materials.append(mat('Ground',(0.22,0.22,0.22),0,0.65))

def add_camera(target, loc, lens, shift_y=0):
    bpy.ops.object.camera_add(location=loc)
    cam=bpy.context.object
    cam.data.lens=lens
    cam.data.shift_y=shift_y
    e=bpy.data.objects.new('Target',None)
    bpy.context.collection.objects.link(e)
    e.location=target
    c=cam.constraints.new(type='TRACK_TO')
    c.target=e
    c.track_axis='TRACK_NEGATIVE_Z'
    c.up_axis='UP_Y'
    bpy.context.scene.camera=cam
    return cam, e

def render(name, cam_params):
    clear_scene()
    setup_world()
    add_ground()
    add_light((4.5,-5.5,6.0),(math.radians(58),0,math.radians(32)),5200,6,(1.0,0.99,0.97))
    add_light((-3.5,4.0,4.5),(math.radians(75),0,math.radians(-55)),2200,9,(0.9,0.95,1.0))
    add_light((0.5,-2.0,7.0),(math.radians(35),0,math.radians(10)),1500,4)
    frame=import_stl(CFG['frame'], mat('Frame',(0.72,0.73,0.75),1.0,0.32))
    spots=[]
    for i in range(CFG['num_sections']):
        z_center=i*section_height + section_height/2
        s=import_stl(SPOT, mat(f'Spot{i}',(0.22,0.22,0.24),0.75,0.48))
        s.location=(spotlight_offset[0], spotlight_offset[1], z_center + spotlight_offset[2])
        s.rotation_euler=tuple(math.radians(a) for a in spotlight_rotation)
        spots.append(s)
    center,size=bounds([frame]+spots)
    target=center+Vector((0,0,size*cam_params['target_z']))
    loc=target+Vector((size*cam_params['x'], -size*cam_params['y'], size*cam_params['z']))
    cam,empty=add_camera(target, loc, cam_params['lens'], cam_params.get('shift_y',0))
    sc=bpy.context.scene
    sc.render.engine='CYCLES'
    sc.cycles.samples=72
    sc.cycles.use_adaptive_sampling=True
    sc.render.resolution_x=cam_params['res'][0]
    sc.render.resolution_y=cam_params['res'][1]
    sc.render.filepath=os.path.join(OUT, f"{CFG['prefix']}_{name}.png")
    sc.render.image_settings.file_format='PNG'
    sc.view_settings.look='AgX - Medium High Contrast'
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)

if variant=='2sec':
    render('hero_landscape', dict(x=0.85,y=2.0,z=0.62,lens=78,res=(1800,1200),target_z=0.10))
    render('detail_square', dict(x=0.75,y=1.55,z=0.55,lens=90,res=(1400,1400),target_z=0.05))
    render('mobile_portrait', dict(x=0.9,y=2.05,z=0.7,lens=78,res=(1200,1800),target_z=0.13,shift_y=0.08))
else:
    render('hero_landscape', dict(x=0.65,y=1.7,z=0.38,lens=95,res=(1800,1200),target_z=0.14))
    render('detail_square', dict(x=0.58,y=1.45,z=0.36,lens=110,res=(1400,1400),target_z=0.10))
    render('mobile_portrait', dict(x=0.68,y=1.78,z=0.42,lens=98,res=(1200,1800),target_z=0.18,shift_y=0.1))

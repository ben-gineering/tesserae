import bpy, math, os, sys
from mathutils import Vector

ROOT='/home/bn/.local/src/tesserae/renders'
OUT=os.path.join(ROOT,'website')
os.makedirs(OUT, exist_ok=True)
FRAME_2=os.path.join(ROOT,'tesserae_2sec_frameonly.stl')
FRAME_6=os.path.join(ROOT,'tesserae_6sec_frameonly.stl')
SPOT='/home/bn/.local/src/tesserae/media/spotlight.stl'
section_height=25
spotlight_offset=(4,19,3)
spotlight_rotation=(90,45,0)
spotlight_scale=1.0
batch = sys.argv[-1] if '--' in sys.argv else '2sec_black'

CONFIGS = {
    '2sec_black': dict(frame=FRAME_2, num_sections=2, frame_color=(0.08,0.08,0.09), spot_color=(0.12,0.12,0.13), style='studio', prefix='tesserae_2sec_black'),
    '2sec_aluminum': dict(frame=FRAME_2, num_sections=2, frame_color=(0.72,0.73,0.75), spot_color=(0.2,0.2,0.22), style='studio', prefix='tesserae_2sec_aluminum'),
    '6sec_black': dict(frame=FRAME_6, num_sections=6, frame_color=(0.08,0.08,0.09), spot_color=(0.12,0.12,0.13), style='industrial', prefix='tesserae_6sec_black'),
    '6sec_aluminum': dict(frame=FRAME_6, num_sections=6, frame_color=(0.72,0.73,0.75), spot_color=(0.2,0.2,0.22), style='industrial', prefix='tesserae_6sec_aluminum'),
    'cutouts': dict(frame=FRAME_2, num_sections=2, frame_color=(0.08,0.08,0.09), spot_color=(0.12,0.12,0.13), style='studio', prefix='tesserae_cutouts'),
}


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def set_world(style, transparent=False):
    world=bpy.data.worlds['World']
    world.use_nodes=True
    nodes=world.node_tree.nodes
    bg=nodes['Background']
    if style=='studio':
        bg.inputs['Color'].default_value=(0.94,0.94,0.92,1)
        bg.inputs['Strength'].default_value=0.55
    else:
        bg.inputs['Color'].default_value=(0.90,0.90,0.88,1)
        bg.inputs['Strength'].default_value=0.35
    bpy.context.scene.render.film_transparent=transparent


def make_mat(name, base, metallic, roughness):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value=(*base,1)
    bsdf.inputs['Metallic'].default_value=metallic
    bsdf.inputs['Roughness'].default_value=roughness
    return mat


def add_light(loc, rot, energy, size, color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l=bpy.context.object
    l.data.energy=energy
    l.data.size=size
    l.data.color=color


def setup_lights(style):
    if style=='studio':
        add_light((4.5,-5.5,6.0),(math.radians(58),0,math.radians(32)),4500,6)
        add_light((-3.5,4.0,4.5),(math.radians(75),0,math.radians(-55)),1800,9,(0.92,0.95,1.0))
        add_light((0.5,-2.0,7.0),(math.radians(35),0,math.radians(10)),1200,4)
    else:
        add_light((5.5,-6.5,7.0),(math.radians(60),0,math.radians(30)),5200,7,(1.0,0.98,0.95))
        add_light((-5.0,5.0,4.0),(math.radians(78),0,math.radians(-60)),1300,10,(0.82,0.88,1.0))
        add_light((0,-1.5,9.0),(math.radians(20),0,0),1400,5)


def add_ground():
    bpy.ops.mesh.primitive_plane_add(size=16, location=(0,0,0))
    plane=bpy.context.object
    mat=make_mat('Ground',(0.19,0.19,0.19),0,0.65)
    plane.data.materials.append(mat)


def import_stl(filepath, material):
    bpy.ops.wm.stl_import(filepath=filepath)
    obj=bpy.context.selected_objects[0]
    obj.data.materials.append(material)
    return obj


def add_spotlights(num_sections, material):
    objs=[]
    for i in range(num_sections):
        z_center=i*section_height + section_height/2
        bpy.ops.wm.stl_import(filepath=SPOT)
        obj=bpy.context.selected_objects[0]
        obj.data.materials.append(material)
        obj.location = (spotlight_offset[0], spotlight_offset[1], z_center + spotlight_offset[2])
        obj.rotation_euler = tuple(math.radians(a) for a in spotlight_rotation)
        obj.scale = (spotlight_scale, spotlight_scale, spotlight_scale)
        objs.append(obj)
    return objs


def scene_bounds(meshes):
    pts=[]
    for obj in meshes:
        for c in obj.bound_box:
            pts.append(obj.matrix_world @ Vector(c))
    mins=Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    maxs=Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mins, maxs, (mins+maxs)/2, max(maxs-mins)


def set_camera(target, location, lens, shift_y=0):
    bpy.ops.object.camera_add(location=location)
    cam=bpy.context.object
    cam.data.lens=lens
    cam.data.shift_y=shift_y
    empty=bpy.data.objects.new('Target',None)
    bpy.context.collection.objects.link(empty)
    empty.location=target
    con=cam.constraints.new(type='TRACK_TO')
    con.target=empty
    con.track_axis='TRACK_NEGATIVE_Z'
    con.up_axis='UP_Y'
    bpy.context.scene.camera=cam
    return cam, empty


def render(filepath, resx, resy, samples=72, transparent=False):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=samples
    scene.cycles.use_adaptive_sampling=True
    scene.render.resolution_x=resx
    scene.render.resolution_y=resy
    scene.render.filepath=filepath
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=transparent
    scene.view_settings.look='AgX - Medium High Contrast'
    bpy.ops.render.render(write_still=True)


def remove_camera(cam, empty):
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)


def render_variant(cfg, name, loc_factor, lens, res, target_z, shift_y=0, transparent=False):
    clear_scene()
    set_world(cfg['style'], transparent)
    setup_lights(cfg['style'])
    if not transparent:
        add_ground()
    frame_mat=make_mat('Frame', cfg['frame_color'], 0.9 if cfg['frame_color'][0] < 0.2 else 1.0, 0.42 if cfg['frame_color'][0] < 0.2 else 0.32)
    spot_mat=make_mat('Spot', cfg['spot_color'], 0.75, 0.48)
    frame=import_stl(cfg['frame'], frame_mat)
    spots=add_spotlights(cfg['num_sections'], spot_mat)
    mins,maxs,center,size=scene_bounds([frame]+spots)
    target=center+Vector((0,0,size*target_z))
    camloc=target+Vector((size*loc_factor[0], -size*loc_factor[1], size*loc_factor[2]))
    cam, empty = set_camera(target, camloc, lens, shift_y)
    render(os.path.join(OUT, f"{cfg['prefix']}_{name}.png"), res[0], res[1], 72 if not transparent else 56, transparent)
    remove_camera(cam, empty)

cfg=CONFIGS[batch]
if batch=='2sec_black':
    render_variant(cfg,'hero_landscape',(0.85,2.0,0.62),78,(1800,1200),0.10)
    render_variant(cfg,'detail_square',(0.75,1.55,0.55),90,(1400,1400),0.05)
    render_variant(cfg,'mobile_portrait',(0.9,2.05,0.7),78,(1200,1800),0.13,0.08)
elif batch=='2sec_aluminum':
    render_variant(cfg,'hero_landscape',(0.85,2.0,0.62),78,(1800,1200),0.10)
    render_variant(cfg,'detail_square',(0.75,1.55,0.55),90,(1400,1400),0.05)
    render_variant(cfg,'mobile_portrait',(0.9,2.05,0.7),78,(1200,1800),0.13,0.08)
elif batch=='6sec_black':
    render_variant(cfg,'hero_landscape',(0.65,1.7,0.38),95,(1800,1200),0.14)
    render_variant(cfg,'detail_square',(0.58,1.45,0.36),110,(1400,1400),0.10)
    render_variant(cfg,'mobile_portrait',(0.68,1.78,0.42),98,(1200,1800),0.18,0.1)
elif batch=='6sec_aluminum':
    render_variant(cfg,'hero_landscape',(0.65,1.7,0.38),95,(1800,1200),0.14)
    render_variant(cfg,'detail_square',(0.58,1.45,0.36),110,(1400,1400),0.10)
    render_variant(cfg,'mobile_portrait',(0.68,1.78,0.42),98,(1200,1800),0.18,0.1)
elif batch=='cutouts':
    render_variant(CONFIGS['2sec_black'],'2sec_transparent_iso',(0.82,1.95,0.62),82,(1600,1600),0.10,transparent=True)
    render_variant(CONFIGS['6sec_black'],'6sec_transparent_iso',(0.64,1.72,0.38),96,(1600,1600),0.14,transparent=True)

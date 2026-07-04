import bpy
import math
import os
from mathutils import Vector, Euler

ROOT = "/home/bn/.local/src/tesserae/renders"
OUT = os.path.join(ROOT, "website")
os.makedirs(OUT, exist_ok=True)

# ---------- scene helpers ----------

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    world = bpy.data.worlds['World']
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    bg = nodes.new('ShaderNodeBackground')
    out = nodes.new('ShaderNodeOutputWorld')
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    bg.inputs['Color'].default_value = (0.96, 0.96, 0.94, 1.0)
    bg.inputs['Strength'].default_value = 0.35


def set_render(filepath, resx, resy, transparent=False, samples=72):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.render.resolution_x = resx
    scene.render.resolution_y = resy
    scene.render.film_transparent = transparent
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = filepath
    scene.view_settings.look = 'AgX - Medium High Contrast'


def make_material(name, base, metallic, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*base, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.5
    return mat


def add_area_light(name, location, rotation, power, size, color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA', location=location, rotation=rotation)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'RECTANGLE'
    light.data.size = size[0]
    light.data.size_y = size[1]
    light.data.color = color
    return light


def setup_lighting(style='studio'):
    if style == 'studio':
        add_area_light('Key', (4.5, -5.5, 5.5), (math.radians(55), 0, math.radians(35)), 4000, (6, 6))
        add_area_light('Fill', (-5.5, 3.5, 3.0), (math.radians(70), 0, math.radians(-55)), 1800, (8, 8))
        add_area_light('Rim', (-2.0, -5.0, 8.0), (math.radians(40), 0, math.radians(-10)), 2500, (4, 10))
    else:
        add_area_light('Key', (6.0, -7.0, 6.5), (math.radians(60), 0, math.radians(30)), 4500, (7, 7), (1.0, 0.98, 0.95))
        add_area_light('Fill', (-6.5, 5.5, 2.5), (math.radians(85), 0, math.radians(-60)), 900, (10, 10), (0.85, 0.9, 1.0))
        add_area_light('Top', (0.0, 0.0, 10.0), (0, 0, 0), 1200, (12, 12))


def add_ground(size=12, color=(0.17,0.17,0.17), roughness=0.55):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0,0,0))
    plane = bpy.context.object
    mat = make_material('Ground', color, metallic=0.0, roughness=roughness)
    plane.data.materials.append(mat)
    return plane


def import_model(path, material):
    bpy.ops.wm.stl_import(filepath=path)
    objs = list(bpy.context.selected_objects)
    root = objs[0]
    bpy.context.view_layer.objects.active = root
    bpy.ops.object.shade_smooth()
    for obj in objs:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(material)
    return root


def frame_object(obj):
    bpy.context.view_layer.update()
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(bbox, Vector((0,0,0))) / 8.0
    size = max((v - center).length for v in bbox)
    return center, size


def set_camera(target, distance, rot_x_deg, rot_z_deg, lens=55, shift_y=0.0):
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.lens = lens
    rx = math.radians(rot_x_deg)
    rz = math.radians(rot_z_deg)
    direction = Vector((0, -distance, 0))
    direction.rotate(Euler((rx, 0, rz), 'XYZ'))
    cam.location = target + direction
    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = bpy.data.objects.new('EmptyTarget', None)
    bpy.context.collection.objects.link(constraint.target)
    constraint.target.location = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    cam.data.shift_y = shift_y
    bpy.context.scene.camera = cam
    return cam


def render_setup(model_path, material_kind, style, with_ground, camera_cfgs, prefix):
    reset_scene()
    if material_kind == 'black_steel':
        material = make_material('BlackSteel', (0.08, 0.08, 0.085), 0.85, 0.42)
    else:
        material = make_material('Aluminum', (0.72, 0.73, 0.75), 1.0, 0.32)
    setup_lighting(style)
    if with_ground:
        add_ground()
    obj = import_model(model_path, material)
    center, size = frame_object(obj)
    for name, cfg in camera_cfgs.items():
        set_camera(center + Vector(cfg.get('target_offset', (0,0,cfg.get('target_z',0)))), cfg['distance'] * size,
                   cfg['rot_x'], cfg['rot_z'], cfg.get('lens', 55), cfg.get('shift_y', 0.0))
        set_render(os.path.join(OUT, f"{prefix}_{name}.png"), cfg['resx'], cfg['resy'], cfg.get('transparent', False), cfg.get('samples', 128))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(bpy.context.scene.camera, do_unlink=True)
        for obj in [o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith('EmptyTarget')]:
            bpy.data.objects.remove(obj, do_unlink=True)

two_sec_cams = {
    'hero_landscape': dict(distance=2.3, rot_x=62, rot_z=38, lens=70, resx=1800, resy=1200, target_offset=(0,0,0.35), samples=96),
    'detail_square': dict(distance=1.9, rot_x=58, rot_z=22, lens=85, resx=1400, resy=1400, target_offset=(0,0,0.15), samples=96),
    'mobile_portrait': dict(distance=2.4, rot_x=66, rot_z=30, lens=65, resx=1200, resy=1800, target_offset=(0,0,0.45), shift_y=0.08, samples=96),
    'transparent_iso': dict(distance=2.1, rot_x=64, rot_z=36, lens=72, resx=1600, resy=1600, target_offset=(0,0,0.3), transparent=True, samples=72),
}

six_sec_cams = {
    'hero_landscape': dict(distance=2.9, rot_x=74, rot_z=32, lens=88, resx=1800, resy=1200, target_offset=(0,0,1.0), samples=96),
    'detail_square': dict(distance=2.3, rot_x=70, rot_z=20, lens=105, resx=1400, resy=1400, target_offset=(0,0,0.6), samples=96),
    'mobile_portrait': dict(distance=2.7, rot_x=76, rot_z=28, lens=92, resx=1200, resy=1800, target_offset=(0,0,1.0), shift_y=0.12, samples=96),
    'transparent_iso': dict(distance=2.7, rot_x=74, rot_z=32, lens=90, resx=1600, resy=1600, target_offset=(0,0,0.9), transparent=True, samples=72),
}

render_setup(os.path.join(ROOT, 'tesserae_2sec.stl'), 'black_steel', 'studio', True, two_sec_cams, 'tesserae_2sec_black_studio')
render_setup(os.path.join(ROOT, 'tesserae_2sec.stl'), 'aluminum', 'studio', True, two_sec_cams, 'tesserae_2sec_aluminum_studio')
render_setup(os.path.join(ROOT, 'tesserae_6sec.stl'), 'black_steel', 'industrial', True, six_sec_cams, 'tesserae_6sec_black_industrial')
render_setup(os.path.join(ROOT, 'tesserae_6sec.stl'), 'aluminum', 'industrial', True, six_sec_cams, 'tesserae_6sec_aluminum_industrial')
render_setup(os.path.join(ROOT, 'tesserae_6sec.stl'), 'black_steel', 'studio', False, {'transparent_iso': six_sec_cams['transparent_iso']}, 'tesserae_6sec_black_cutout')
render_setup(os.path.join(ROOT, 'tesserae_2sec.stl'), 'black_steel', 'studio', False, {'transparent_iso': two_sec_cams['transparent_iso']}, 'tesserae_2sec_black_cutout')

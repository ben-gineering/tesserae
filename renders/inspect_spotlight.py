import bpy, os
from mathutils import Vector
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
path="/home/bn/.local/src/tesserae/media/spotlight.stl"
bpy.ops.wm.stl_import(filepath=path)
objs=bpy.context.selected_objects
print("objects", len(objs))
for o in objs:
    print(o.name, o.type, len(o.data.vertices), len(o.data.polygons))
    mins=[min(v.co[i] for v in o.data.vertices) for i in range(3)]
    maxs=[max(v.co[i] for v in o.data.vertices) for i in range(3)]
    print("bbox", mins, maxs)

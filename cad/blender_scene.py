"""OPTIONAL Blender (4.x) scene builder -- NOT RUN in the authoring environment (no Blender there);
the delivered renders/MP4 were made with render_vtk.py from the same meshes.
Usage:  blender -b -P blender_scene.py -- out/viz  [--render]
Imports out/viz/*.stl (world frame, mm), applies materials, and keyframes the same exploded->assembled
motion defined in manifest.json. Saves slimcase_anim.blend next to the meshes."""
import bpy, json, sys, os, math
viz = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "out/viz"
man = json.load(open(os.path.join(viz, "manifest.json")))
FPS, HOLD0, MOVE, HOLD1, SC = 24, 1.5, 6.5, 3.0, 0.001   # mm -> m
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = round((HOLD0 + MOVE + HOLD1) * FPS)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
mats = {}
for p in man:
    bpy.ops.wm.stl_import(filepath=os.path.join(viz, p["file"]), global_scale=SC)
    o = bpy.context.selected_objects[0]; o.name = p["name"]
    key = tuple(p["color"])
    if key not in mats:
        m = bpy.data.materials.new(p["name"] + "_mat"); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*key, 1); b.inputs["Roughness"].default_value = 0.55
        mats[key] = m
    o.data.materials.append(mats[key])
    n0, n1 = round(HOLD0 * FPS), round(MOVE * FPS)
    for f in range(n0, n0 + n1 + 1):
        s = (f - n0) / n1; off = [0, 0, 0]
        for seg in p["explode"]:
            k = 1 - ease((s - seg["t0"]) / (seg["t1"] - seg["t0"]))
            for i in range(3): off[i] += seg["vec"][i] * k * SC
        o.location = off; o.keyframe_insert("location", frame=f + 1)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
d = (1.0, -1.0, 0.42); L = math.sqrt(sum(k * k for k in d)); foc = (0.130, 0.120, 0.205)
cam.location = [foc[i] + d[i] / L * 1.45 for i in range(3)]; cam.data.angle = math.radians(28) * 16 / 9
t = bpy.data.objects.new("target", None); t.location = foc; sc.collection.objects.link(t)
c = cam.constraints.new("TRACK_TO"); c.target = t; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.rotation_euler = (math.radians(50), 0, math.radians(-25)); sun.data.energy = 3; sc.collection.objects.link(sun)
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.image_settings.file_format = "FFMPEG"; sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
sc.render.filepath = os.path.join(viz, "..", "slimcase_blender.mp4")
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(os.path.join(viz, "..", "slimcase_anim.blend")))
if "--render" in sys.argv: bpy.ops.render.render(animation=True)

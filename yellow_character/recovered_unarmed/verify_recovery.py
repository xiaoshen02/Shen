"""Read and render the recovered original without saving over it."""
import bpy,os,json,math
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
path=os.path.join(OUT,'YellowFriend_v29_1_unarmed.blend')
bpy.ops.wm.open_mainfile(filepath=path)
sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update()
body=bpy.data.objects['YellowFriend | continuous shoulders and rebuilt hands']
rig=bpy.data.objects['YellowFriend_Rig']
report={'model':os.path.basename(path),'finger_revision':body.get('Finger_revision'),'feet_revision':body.get('Feet_revision'),'belly_revision':body.get('Belly_revision'),'action':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,'vertices':len(body.data.vertices),'external_libraries':[x.filepath for x in bpy.data.libraries],'unpacked_file_images':[x.filepath for x in bpy.data.images if x.source=='FILE' and not x.packed_file],'visible_sword_meshes':[o.name for o in sc.objects if o.type=='MESH' and o.name.startswith('Sword_') and not o.hide_render],'arms':{s:{'shoulder':list(rig.pose.bones['upper_arm'+s].head),'wrist':list(rig.pose.bones['hand'+s].head)} for s in ['.L','.R']},'finite_vertices':all(math.isfinite(c) for v in body.data.vertices for c in v.co)}
assert report['finger_revision'].startswith('v29.1')
assert report['action']=='09_Neutral_threeview'
assert not report['visible_sword_meshes'] and not report['external_libraries'] and not report['unpacked_file_images']
assert report['finite_vertices']
assert all(x['wrist'][2]<x['shoulder'][2]-.8 for x in report['arms'].values())
with open(os.path.join(OUT,'recovery_validation.json'),'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('RECOVERY_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
data=bpy.data.cameras.new('Recovered original front');cam=bpy.data.objects.new('Recovered original front',data);sc.collection.objects.link(cam)
cam.location=(0,-12,2.50);cam.rotation_euler=(Vector((0,0,2.50))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=5.5;sc.camera=cam
sc.render.engine='BLENDER_EEVEE';sc.eevee.taa_render_samples=32;sc.eevee.use_raytracing=False
sc.render.resolution_x=714;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG'
sc.render.filepath=os.path.join(OUT,'recovered_front.png');bpy.ops.render.render(write_still=True)
print('RECOVERED_PREVIEW_READY',flush=True)

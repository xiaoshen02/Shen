"""Refine only the feet: flat soles, outward toes, softer dorsal bulges."""
import bpy,os,math,json
from mathutils import Vector
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report={}
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
for mode,name in [('grip','YellowFriend_v29_reference_grip.blend'),('neutral','YellowFriend_v29_neutral.blend')]:
 path=os.path.join(OUT,name);bpy.ops.wm.open_mainfile(filepath=path)
 body=bpy.data.objects['YellowFriend | continuous shoulders and rebuilt hands'];rig=bpy.data.objects['YellowFriend_Rig']
 original=[v.co.copy() for v in body.data.vertices]
 def foot(q):
  x,y,z=q
  fade=1-smooth(.20,.43,z)
  if fade<=0:return Vector(q)
  sign=1 if x>=0 else -1;cx=sign*(.78+(.12 if mode=='grip' and sign<0 else 0))
  dx=(x-cx)*(1-.15*fade);dy=(y+.035)*(1-.08*fade)
  a=sign*math.radians(56)*fade;c=math.cos(a);s=math.sin(a)
  nz=z-(z-.047)*.33*fade
  if nz<.061:nz=.047+(nz-.04)*.10
  return Vector((cx+c*dx-s*dy,-.035+s*dx+c*dy,nz))
 for v in body.data.vertices:v.co=foot(v.co)
 # Relax the round pad ridges while retaining the three toe silhouettes.
 vg=body.vertex_groups.new(name='Feet polish only')
 for v in body.data.vertices:
  w=1-smooth(.14,.26,v.co.z)
  if w>0:vg.add([v.index],w,'REPLACE')
 sm=body.modifiers.new('Flatten and soften foot pads','SMOOTH');sm.vertex_group=vg.name;sm.factor=.50;sm.iterations=18
 bpy.context.view_layer.objects.active=body;bpy.ops.object.select_all(action='DESELECT');body.select_set(True)
 # Bake the local sculpt on the base mesh without changing modifier order.
 while list(body.modifiers).index(sm)>0:bpy.ops.object.modifier_move_up(modifier=sm.name)
 bpy.ops.object.modifier_apply(modifier=sm.name)
 bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for side in ['.L','.R']:
  bone=rig.data.edit_bones['foot'+side];bone.head=foot(bone.head);bone.tail=foot(bone.tail)
  shin=rig.data.edit_bones['shin'+side];shin.tail=bone.head
 bpy.ops.object.mode_set(mode='OBJECT')
 for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 body['Feet_revision']='v29: outward 56-degree forefeet, flatter sole and dorsal shape, softened toe pads. Arm/hand/face geometry unchanged.'
 polish_group=body.vertex_groups.get('Feet polish only')
 if polish_group:body.vertex_groups.remove(polish_group)
 unchanged=max((v.co-original[v.index]).length for v in body.data.vertices if original[v.index].z>.43)
 coords=[v.co for v in body.data.vertices if v.co.z<.30]
 report[mode]={'max_change_above_feet':unchanged,'sole_min_z':min(v.z for v in coords),'sole_max_z':max(v.z for v in coords),'foot_bounds_x':[min(v.x for v in coords),max(v.x for v in coords)]}
 bpy.context.view_layer.objects.active=body;body.select_set(True)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=path)
 print('FEET_REFINED',mode,report[mode],flush=True)
with open(os.path.join(OUT,'feet_validation.json'),'w') as f:json.dump(report,f,indent=2)

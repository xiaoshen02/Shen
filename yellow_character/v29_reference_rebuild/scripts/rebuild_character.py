"""Rebuild continuous shoulders/arms and sculpt the grip in a clean bind pose.

The new pose has its own bind rig. Legacy actions remain in v28, since applying
them to a changed bind skeleton would be incorrect. A separate neutral model
uses the same trunk proportions for three-view review.
"""
import bpy, bmesh, os, sys, json, math
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE=os.path.dirname(OUT)
MODE='neutral' if '--neutral' in sys.argv else 'grip'
bpy.ops.wm.open_mainfile(filepath=os.path.join(BASE,'v28_hand_refined','YellowFriend_hand_refined.blend'))
sc=bpy.context.scene;sc.frame_set(1)
rig=bpy.data.objects['YellowFriend_Rig'];old=bpy.data.objects['YellowFriend | latest shoulders and sword']
def center(o):return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
old_guard=center(bpy.data.objects['Sword_Guard'])
old_axis=(center(bpy.data.objects['Sword_Pommel'])-old_guard).normalized()
swordworld={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Sword_')}
faceworld={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.parent==rig and o.parent_bone=='head'}
rig.animation_data_clear()
for p in rig.pose.bones:
 for c in list(p.constraints):p.constraints.remove(c)
 p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
for n,m in faceworld.items():bpy.data.objects[n].matrix_world=m
skin=old.data.materials[0]
collection=old.users_collection[0]
parts=[]
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def mix(a,b,t):return tuple(a[i]*(1-t)+b[i]*t for i in range(3))
def morph(q):
 x,y,z=q
 # A rounder head, wider upper trunk and fuller thighs/ankles.
 # Face is explicitly locked to v28. Shape edits fade out below the head.
 widening=1+.065*math.exp(-((z-3.5)/.49)**2)*(1-smooth(3.70,4.00,z))
 x*=widening
 if z<1.6:
  sign=1 if x>=0 else -1;axis=sign*(.78-.11*smooth(.25,1.38,z))
  x=axis+(x-axis)*(1+.14*smooth(.40,.95,z)*(1-smooth(1.05,1.55,z)))
  # Broader, flatter feet with less spherical-looking toes.
  footfade=1-smooth(.20,.40,z)
  x=sign*.80+(x-sign*.80)*(1+.12*footfade)
  if MODE=='grip' and x<0:x-=.12*(1-smooth(.25,1.50,z))
 # Lift the rear lumbar volume, keep the belly's front bulge.
 y+=.045*smooth(0,.65,y)*math.exp(-((z-2.5)/.95)**2)
 return Vector((x,y,z))

# Keep the established torso/legs. All old arm vertices are replaced.
trunk=bpy.data.objects.new('Continuous trunk donor',old.data.copy());collection.objects.link(trunk)
for g in old.vertex_groups:trunk.vertex_groups.new(name=g.name)
bm=bmesh.new();bm.from_mesh(trunk.data)
layer=bm.verts.layers.int.get('SkinRegion')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v[layer]>0],context='VERTS')
bm.to_mesh(trunk.data);bm.free()
for v in trunk.data.vertices:v.co=morph(v.co)
trunk.data.update();parts.append(trunk)
trunkcoords=[v.co.copy() for v in trunk.data.vertices]
trunkfaces=[tuple(p.vertices) for p in trunk.data.polygons]
trunktree=BVHTree.FromPolygons(trunkcoords,trunkfaces)
donor=trunk.copy();donor.data=trunk.data.copy();collection.objects.link(donor);donor.name='Weight donor only';donor.hide_render=True;donor.hide_viewport=True

def catmull(vals,t):
 i=min(int(t),len(vals)-2);u=t-i;a=vals[max(0,i-1)];b=vals[i];c=vals[i+1];d=vals[min(len(vals)-1,i+2)]
 return .5*(2*b+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)
def tube(name,points,radii,depth=1.,resolution=12):
 points=[Vector(p) for p in points];cols=list(zip(*points));verts=[];faces=[];count=(len(points)-1)*resolution+1;sides=32
 for j in range(count):
  t=j/(count-1)*(len(points)-1);p=Vector([catmull(c,t) for c in cols]);r=max(.002,catmull(radii,t))
  tangent=Vector([catmull(c,min(len(points)-1,t+.005))-catmull(c,max(0,t-.005)) for c in cols]).normalized()
  axis=Vector((0,1,0))
  if abs(tangent.dot(axis))>.96:axis=Vector((1,0,0))
  u=tangent.cross(axis).normalized();w=tangent.cross(u).normalized()
  for k in range(sides):
   a=2*math.pi*k/sides;verts.append(tuple(p+r*(math.cos(a)*u+depth*math.sin(a)*w)))
 for j in range(count-1):
  for k in range(sides):
   a=j*sides+k;b=j*sides+(k+1)%sides;faces.append((a,b,b+sides,a+sides))
 faces.extend([tuple(reversed(range(sides))),tuple((count-1)*sides+k for k in range(sides))])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);collection.objects.link(o);parts.append(o);return o
def ellipsoid(name,loc,axes):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc)
 o=bpy.context.object;o.name=name
 m=Matrix(axes).transposed()
 for v in o.data.vertices:v.co=m@v.co
 parts.append(o);return o

A=Vector((-.63,0,.7766)).normalized();U=Vector((A.z,0,-A.x));F=Vector((0,-1,0))
guard=Vector((.07,-1.36,2.72))
stations={'.L':guard+A*.32,'.R':guard-A*.31}
arms={};fingerpaths={};palms={}
for side,sign in [('.L',-1),('.R',1)]:
 shoulder=Vector((sign*.85,.015,3.43))
 root=Vector((sign*.64,.09,3.52))
 if MODE=='grip' and side=='.R':
  # The lower hand in the drawing supports the flat at the sword root,
  # below the guard. It does not grip the same hilt as the upper hand.
  station=stations[side]+F*.055;N=U;T=F
  wrist=Vector((.77,-1.19,2.64))
  palm=station+U*.22+F*.11
  elbow=Vector((1.02,-.39,3.05))
  points=[root,shoulder,shoulder.lerp(elbow,.46),elbow,elbow.lerp(wrist,.55),wrist,palm]
  radii=[.23,.245,.232,.195,.156,.111,.10]
  tube('Anatomical arm '+side,points,radii,.96)
  ellipsoid('Supporting palm '+side,palm,[A*.18,U*.12,F*.075])
  for i,off in enumerate([-.108,0,.108]):
   path=[station+A*(off+.006*t)+U*(.19-.32*t)+F*(.115-.015*math.sin(math.pi*t)) for t in [0,.16,.32,.48,.64,.80,.94,1]]
   tube('Supporting finger '+side+str(i),path,[.046,.045,.044,.042,.041,.038,.030,.008],1.,6)
   fingerpaths['finger'+str(i)+side]=path
  path=[station+A*(.18+.035*t)+U*(.29-.22*t)+F*(.12-.015*t) for t in [0,.2,.4,.6,.8,1]]
  tube('Supporting thumb '+side,path,[.059,.056,.051,.045,.035,.008],1.,7);fingerpaths['thumb'+side]=path
 elif MODE=='grip':
  N=(U*(sign*.77)+Vector((0,1,0))*.638).normalized()
  T=A.cross(N).normalized() * (1 if sign<0 else -1)
  station=stations[side]
  wrist=station+N*.32+A*.18
  palm=station+N*.170
  elbow=Vector((sign*1.12,-.43,3.25))
  points=[root,shoulder,shoulder.lerp(elbow,.45),elbow,elbow.lerp(wrist,.58),wrist,palm]
  radii=[.23,.245,.235,.205,.164,.115,.105]
  tube('Anatomical arm '+side,points,radii,.96)
  ellipsoid('Palm '+side,palm,[A*.181,T*.123,N*.083])
  for i,off in enumerate([-.112,0,.112]):
   path=[]
   for j in range(10):
    t=j/9;angle=.24+t*2.72;rad=.170*(1-smooth(0,.38,t))+.114*smooth(0,.38,t)
    path.append(station+A*(off+.008*math.sin(math.pi*t))+rad*(N*math.cos(angle)+T*math.sin(angle)))
   rr=[.047,.047,.045,.044,.043,.042,.041,.039,.034,.009]
   tube('Curved finger '+side+str(i),path,rr,1.,5)
   fingerpaths['finger'+str(i)+side]=path
  off=-.190 if sign<0 else .190
  path=[station+A*(off+.015*t)+.155*(N*math.cos(-.32-t*1.84)+T*math.sin(-.32-t*1.84)) for t in [0,.15,.30,.45,.60,.75,.90,1.]]
  tube('Opposing thumb '+side,path,[.060,.058,.055,.051,.048,.044,.036,.009],.96,6)
  ellipsoid('Thenar '+side,station+A*off+N*.145-T*.028,[A*.075,T*.075,N*.075])
  fingerpaths['thumb'+side]=path
 else:
  wrist=Vector((sign*1.18,-.13,2.09));palm=Vector((sign*1.18,-.155,1.95));elbow=Vector((sign*1.20,-.035,2.80))
  points=[root,shoulder,Vector((sign*1.08,.005,3.13)),elbow,Vector((sign*1.21,-.08,2.38)),wrist,palm]
  tube('Anatomical arm '+side,points,[.23,.245,.24,.22,.165,.115,.10],.94)
  ellipsoid('Palm '+side,palm,[Vector((.112,0,0)),Vector((0,.163,0)),Vector((0,0,.17))])
  for i in range(3):
   y=-.275+i*.11;z=[1.68,1.66,1.71][i]
   path=[Vector((sign*1.18,y,1.86)),Vector((sign*1.19,y-.007,1.77)),Vector((sign*1.17,y-.017,z+.03)),Vector((sign*1.155,y-.02,z))]
   tube('Relaxed finger '+side+str(i),path,[.045,.044,.035,.009],1,8);fingerpaths['finger'+str(i)+side]=path
  path=[Vector((sign*1.145,-.265,2.015)),Vector((sign*1.095,-.35,1.97)),Vector((sign*1.08,-.38,1.89)),Vector((sign*1.1,-.37,1.85))]
  tube('Relaxed thumb '+side,path,[.060,.055,.040,.009],1,8);fingerpaths['thumb'+side]=path
 arms[side]={'root':root,'shoulder':shoulder,'elbow':elbow,'wrist':wrist,'palm':palm,'points':points,'radii':radii if MODE=='grip' else [.23,.245,.24,.22,.165,.115,.10]}
 palms[side]=palm

# One welded skin surface, including the shoulders. No overlapping arm caps.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=trunk;bpy.ops.object.join();body=trunk;body.name='YellowFriend | continuous shoulders and rebuilt hands'
for m in list(body.modifiers):body.modifiers.remove(m)
rem=body.modifiers.new('Weld shoulders, wrist and fingers','REMESH');rem.mode='VOXEL';rem.voxel_size=.011;rem.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=rem.name)
sm=body.modifiers.new('Organic surface relaxation','SMOOTH');sm.factor=.38;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
wg=body.vertex_groups.new(name='Shoulder root relaxation')
for v in body.data.vertices:
 x,y,z=v.co
 w=math.exp(-((abs(x)-.82)/.28)**4-((z-3.42)/.28)**4)*smooth(-.50,-.20,y)
 if w>.001:wg.add([v.index],w,'REPLACE')
sm=body.modifiers.new('Sculpt shoulder root transition','SMOOTH');sm.factor=.65;sm.iterations=65;sm.vertex_group=wg.name;bpy.ops.object.modifier_apply(modifier=sm.name)
dec=body.modifiers.new('Editable sculpt density','DECIMATE');dec.ratio=.50;bpy.ops.object.modifier_apply(modifier=dec.name)
# Remove tiny isolated cap fragments left by voxel/decimation at finger tips.
bm=bmesh.new();bm.from_mesh(body.data);seen=set();discard=[]
for v in bm.verts:
 if v in seen:continue
 todo=[v];seen.add(v);component=[]
 while todo:
  u=todo.pop();component.append(u)
  for e in u.link_edges:
   q=e.other_vert(u)
   if q not in seen:seen.add(q);todo.append(q)
 if len(component)<32:discard.extend(component)
if discard:bmesh.ops.delete(bm,geom=discard,context='VERTS')
bm.to_mesh(body.data);bm.free()
print('SCULPT_WELDED',MODE,len(body.data.vertices),flush=True)

# New arm bind pose follows the actual, untwisted sculpt. Reusing the old action
# would reintroduce the invalid rotations; retain those only in previous files.
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for side,info in arms.items():
 for stem,a,b in [('upper_arm',info['shoulder'],info['elbow']),('forearm',info['elbow'],info['wrist']),('hand',info['wrist'],info['palm'])]:
  eb=rig.data.edit_bones[stem+side];eb.use_connect=False;eb.head=a;eb.tail=b;eb.roll=0
 for stem in ['finger0','finger1','finger2','thumb']:
  path=fingerpaths[stem+side];mid=len(path)//2
  for seg,a,b in [(1,path[0],path[mid]),(2,path[mid],path[-1])]:
   eb=rig.data.edit_bones[stem+f'_0{seg}'+side];eb.use_connect=False;eb.head=a;eb.tail=b;eb.roll=0
for eb in rig.data.edit_bones:
 if eb.name.startswith(('thigh','shin','foot')):
  eb.head=morph(eb.head);eb.tail=morph(eb.tail)
bpy.ops.object.mode_set(mode='OBJECT')
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()

# Transfer only trunk weights; each arm/finger is then assigned analytically.
bpy.context.view_layer.objects.active=body;bpy.ops.object.select_all(action='DESELECT');body.select_set(True)
for g in list(body.vertex_groups):body.vertex_groups.remove(g)
for b in rig.data.bones:body.vertex_groups.new(name=b.name)
donor.hide_viewport=False
dt=body.modifiers.new('Trunk weight donor','DATA_TRANSFER');dt.object=donor;dt.use_vert_data=True;dt.data_types_verts={'VGROUP_WEIGHTS'};dt.vert_mapping='POLYINTERP_NEAREST';dt.layers_vgroup_select_src='ALL';dt.layers_vgroup_select_dst='NAME'
bpy.ops.object.modifier_apply(modifier=dt.name)
bpy.data.objects.remove(donor,do_unlink=True);bpy.data.objects.remove(old,do_unlink=True)
def segment(q,a,b):
 ab=b-a;t=max(0,min(1,(q-a).dot(ab)/ab.length_squared));return (q-(a+ab*t)).length,t
def pathdistance(q,path):
 rows=[(*segment(q,a,b),j) for j,(a,b) in enumerate(zip(path[:-1],path[1:]))]
 d,t,j=min(rows);return d,(j+t)/(len(path)-1)
region=body.data.attributes.get('SkinRegion')
if region:body.data.attributes.remove(region)
region=body.data.attributes.new('SkinRegion','INT','POINT')
ca=body.data.color_attributes.get('SkinColor')
if ca:body.data.color_attributes.remove(ca)
ca=body.data.color_attributes.new(name='SkinColor',type='FLOAT_COLOR',domain='POINT')
for v in body.data.vertices:
 q=v.co;x,y,z=q;side='.L' if x<0 else '.R'
 # Closest arm determines side even when a hand crosses the centre line.
 ar=[]
 for s,inf in arms.items():
  d,t=pathdistance(q,inf['points']);ar.append((d,s,t))
 ad,side,at=min(ar);inf=arms[side]
 td=trunktree.find_nearest(q)[3]
 armzone=(ad<.29 and (td>.018 or (abs(x)>.72 and z>3.12)))
 weights=None;handfade=0.
 if armzone:
  rootblend=smooth(.70,1.00,abs(x)) if z>3.14 and y>-.38 else 1.
  d1,t1=segment(q,inf['shoulder'],inf['elbow']);d2,t2=segment(q,inf['elbow'],inf['wrist']);d3,t3=segment(q,inf['wrist'],inf['palm'])
  if d1<d2 and t1<.88:weights={'upper_arm'+side:1.}
  elif d2<d3:
   e=smooth(0,.18,t2);h=smooth(.76,1,t2);weights={'upper_arm'+side:1-e,'forearm'+side:e*(1-h),'hand'+side:e*h}
  else:weights={'hand'+side:1.}
  handfade=smooth(.64,1.0,t2) if d2<d3 else 1.
  nearest=[]
  for stem in ['finger0','finger1','finger2','thumb']:
   fd,ft=pathdistance(q,fingerpaths[stem+side]);nearest.append((fd,stem,ft))
  fd,stem,ft=min(nearest)
  if fd<(.07 if stem=='thumb' else .06) and (q-inf['wrist']).length>.16:
   blend=smooth(.04,.25,ft);w2=smooth(.32,.68,ft)
   weights={n:w*(1-blend) for n,w in weights.items()};weights[stem+'_01'+side]=blend*(1-w2);weights[stem+'_02'+side]=blend*w2;handfade=1.
  weights={n:w*rootblend for n,w in weights.items()};weights['chest']=1-rootblend
  for g in list(v.groups):body.vertex_groups[g.group].remove([v.index])
  for n,w in weights.items():
   if w>1e-7:body.vertex_groups[n].add([v.index],w,'REPLACE')
  region.data[v.index].value=(1 if side=='.L' else 2) if rootblend>.5 else 0
 else:region.data[v.index].value=0
 # The distal side of a closed finger can lie far from the arm centreline.
 # Classify it by the actual finger curves, never by proximity to the belly.
 finger_candidates=[]
 for s in arms:
  for stem in ['finger0','finger1','finger2','thumb']:
   fd,ft=pathdistance(q,fingerpaths[stem+s]);finger_candidates.append((fd,s,stem,ft))
 fd,fs,stem,ft=min(finger_candidates)
 if fd<(.076 if stem=='thumb' else .065):
  armzone=True;handfade=1.;region.data[v.index].value=1 if fs=='.L' else 2
  blend=smooth(.04,.25,ft);w2=smooth(.32,.68,ft)
  for g in list(v.groups):body.vertex_groups[g.group].remove([v.index])
  for n,w in {'hand'+fs:1-blend,stem+'_01'+fs:blend*(1-w2),stem+'_02'+fs:blend*w2}.items():
   if w>1e-7:body.vertex_groups[n].add([v.index],w,'REPLACE')
 col=mix((1.,.56,.016),(1.,.76,.045),smooth(1.3,4.85,z))
 dz=(z-2.75)/(.86 if z>2.75 else .67)
 exponent=2 if z>2.75 else 4
 boundary=(x/1.13)**2+abs(dz)**exponent
 # A continuous distance field fades the belly patch at the shoulder union.
 # A hard arm/trunk classification creates visible paint seams on welded skin.
 patch=(1-smooth(.93,1.07,boundary))*(1-smooth(-.20,-.04,y))*(1-smooth(.012,.095,td))
 col=mix(col,(.84,.76,.59),patch)
 col=mix(col,(.175,.151,.092),max(handfade,1-smooth(.18,.38,z))*.96)
 ca.data[v.index].color=(*col,1)
 if v.index%50000==0:print('WEIGHTED',v.index,flush=True)
for p in body.data.polygons:p.use_smooth=True
body.data.materials.clear();body.data.materials.append(skin);body.data.color_attributes.active_color=ca
body.parent=rig
arm=body.modifiers.new('Clean bind deform','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
sub=body.modifiers.new('Surface polish','SUBSURF');sub.levels=1;sub.render_levels=1
body['Revision']='v29: one welded shoulder/trunk skin, new forearms and cylindrical finger grasp; clean pose-specific bind. Neutral proportions saved separately.'
rig['Bind_note']='New sculpt-aligned bind. Legacy v28 actions intentionally not assigned.'
rig.show_in_front=False

# Transform the sword as a complete rigid assembly into the drawn low guard.
rot=old_axis.rotation_difference(A).to_matrix()
root=bpy.data.objects['SwordRoot'];root.animation_data_clear();root.constraints.clear();root.parent=None;root.matrix_world=Matrix.Identity(4)
for n,coords in swordworld.items():
 o=bpy.data.objects[n];o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=Matrix.Identity(4)
 for v,co in zip(o.data.vertices,coords):
  delta=co-old_guard;axial=old_axis*delta.dot(old_axis);radial=delta-axial
  scale=.56 if delta.dot(old_axis)>0 else .80
  v.co=guard+rot@(axial*scale+radial)
 if MODE=='neutral':o.hide_render=True;o.hide_viewport=True
 if o.name.startswith('Sword_Guard_Hook'):o.hide_render=True;o.hide_viewport=True
if MODE=='grip':
 # Bind to lower hand while maintaining the newly established world placement.
 world=root.matrix_world.copy();root.parent=rig;root.parent_type='BONE';root.parent_bone='hand.R';root.matrix_world=world

# Preserve the complete v28 facial assembly, including its world transforms.
for n,m in faceworld.items():
 bpy.data.objects[n].matrix_world=m

action=bpy.data.actions.new('09_Reference_low_guard' if MODE=='grip' else '09_Neutral_threeview');action.use_fake_user=True
rig.animation_data_create();rig.animation_data.action=action
for p in rig.pose.bones:
 p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
 p.keyframe_insert('rotation_euler',frame=1,group=p.name);p.keyframe_insert('location',frame=1,group=p.name)
sc.frame_start=1;sc.frame_end=1;sc.frame_set(1)
sc.render.engine='BLENDER_EEVEE';sc.eevee.taa_render_samples=32;sc.eevee.use_raytracing=False
sc.render.resolution_percentage=100;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG'
sc.world.color=(1,1,1)
# Use a white studio for useful silhouette comparisons.
for n in sc.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Color'].default_value=(1,1,1,1)
sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=-.35
floor=bpy.data.objects.get('Studio floor');floor.scale=(1,1,1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
   area.spaces.active.region_3d.view_location=Vector((0,0,2.5));area.spaces.active.region_3d.view_distance=7
sc.camera=bpy.data.objects['Camera | Beauty'];sc.camera.location=(.4,-14,3.8);sc.camera.rotation_euler=(Vector((.2,-.1,2.5))-sc.camera.location).to_track_quat('-Z','Y').to_euler();sc.camera.data.ortho_scale=5.85
sc.render.resolution_x=860;sc.render.resolution_y=1000
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.context.preferences.filepaths.save_version=0
filename='YellowFriend_v29_reference_grip.blend' if MODE=='grip' else 'YellowFriend_v29_neutral.blend'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,filename))
report={'mode':MODE,'vertices':len(body.data.vertices),'shoulders':'voxel-welded to trunk, continuous skin','bind':'new sculpt-aligned rest pose; v28 actions not reused','arms':{s:{k:[list(v) for v in val] if k=='points' else list(val) if isinstance(val,Vector) else val for k,val in inf.items()} for s,inf in arms.items()}}
with open(os.path.join(OUT,MODE+'_build.json'),'w') as f:json.dump(report,f,indent=2)
print('MODEL_SAVED',filename,flush=True)
if '--no-render' not in sys.argv:
 sc.render.filepath=os.path.join(OUT,MODE+'_full.png');bpy.ops.render.render(write_still=True)
 if MODE=='grip':
  cam=bpy.data.objects['Camera | Hand_detail'];cam.location=(.1,-7,3.65);cam.rotation_euler=(Vector((.1,-1.30,2.94))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.65
  sc.camera=cam;sc.render.resolution_x=1100;sc.render.resolution_y=900;sc.render.filepath=os.path.join(OUT,'grip_detail.png');bpy.ops.render.render(write_still=True)
print('BUILD_COMPLETE',MODE,flush=True)

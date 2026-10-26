import bpy,bmesh,os,json,math,sys
import numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE=os.path.dirname(OUT)
SOURCE=os.path.join(BASE,'v28_hand_refined','YellowFriend_hand_refined.blend')
MAIN=os.path.join(OUT,'YellowFriend_v29_reference_grip.blend')
NEUTRAL=os.path.join(OUT,'YellowFriend_v29_neutral.blend')

def mesh(o,details=True):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 raw=np.empty(len(m.vertices)*3);m.vertices.foreach_get('co',raw);wm=np.array(e.matrix_world)
 co=raw.reshape(-1,3)@wm[:3,:3].T+wm[:3,3];faces=[tuple(p.vertices) for p in m.polygons]
 names={g.index:g.name for g in o.vertex_groups}
 groups=[{names[g.group]:g.weight for g in v.groups} for v in m.vertices] if details else None
 colors=np.array([v.color[:] for v in m.color_attributes['SkinColor'].data]) if details and m.color_attributes.get('SkinColor') else None
 e.to_mesh_clear();return co,faces,groups,colors
def tree(co,faces):return BVHTree.FromPolygons(co.tolist(),faces)
def configure():
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.eevee.use_raytracing=False
 s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
 return s
def camera(name,loc,target,scale):
 o=bpy.data.objects.get(name)
 if o is None:
  o=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.context.scene.collection.objects.link(o)
 o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;return o
def render(name,cam,w=714,h=850):
 s=configure();s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
 print('QA_RENDER',name,flush=True)

if '--finger-review' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=MAIN);bpy.context.scene.frame_set(1)
 render('grip_detail',camera('QA Hands',(.1,-7,3.65),(.1,-1.30,2.94),1.65),1400,1100)
 render('left_fingers',camera('QA Upper fingers',(-.35,-7,3.85),(-.17,-1.35,2.99),.90),1100,1000)
 render('right_fingers',camera('QA Lower fingers',(.75,-7,3.3),(.43,-1.49,2.53),.88),1100,1000)
 render('grip_full',bpy.data.objects['Camera | Beauty'],860,1000)
 sys.exit(0)

if '--hands-only' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=MAIN);bpy.context.scene.frame_set(1)
 render('grip_detail',camera('QA Hands',(.1,-7,3.65),(.1,-1.30,2.94),1.65),1100,900)
 sys.exit(0)

if '--renders-only' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=MAIN);bpy.context.scene.frame_set(1)
 render('grip_full',bpy.data.objects['Camera | Beauty'],860,1000)
 render('feet_detail',camera('QA Feet',(2.4,-6,1.65),(0,-.12,.24),3.10),1200,620)
 bpy.ops.wm.open_mainfile(filepath=NEUTRAL);bpy.context.scene.frame_set(1)
 for name,loc in [('front',(0,-12,2.5)),('side',(-12,0,2.5)),('back',(0,12,2.5))]:
  render('neutral_'+name,camera('QA '+name,loc,(0,0,2.50),5.5),620,780)
 sys.exit(0)

bpy.ops.wm.open_mainfile(filepath=SOURCE);bpy.context.scene.frame_set(1)
sourcefaces={o.name:{'matrix':np.array(o.matrix_world),'co':np.array([tuple(v.co) for v in o.data.vertices]) if o.type=='MESH' else None} for o in bpy.data.objects if o.parent_bone=='head'}
old=bpy.data.objects['YellowFriend | latest shoulders and sword']
oldco=np.array([v.co[:] for v in old.data.vertices]);oldfaces=[tuple(p.vertices) for p in old.data.polygons]
oldhead=tree(oldco,[p for p in oldfaces if all(oldco[i,2]>3.96 for i in p)])
sourcecam=camera('QA Face',(0,-8,4.60),(0,-.2,4.50),1.25)
if '--checks-only' not in sys.argv:render('face_v28',sourcecam,600,600)

bpy.ops.wm.open_mainfile(filepath=MAIN);bpy.context.scene.frame_set(1)
b=bpy.data.objects['YellowFriend | continuous shoulders and rebuilt hands'];rig=bpy.data.objects['YellowFriend_Rig']
co,faces,groups,colors=mesh(b)
report={'pose':'static reference low guard, frame 1','finite_coordinates':bool(np.isfinite(co).all()),'evaluated_subdivision_level':1,'face':{},'collisions':{},'shoulder_deformation':{}}
report['face']['max_feature_transform_delta']=max(float(np.max(np.abs(np.array(bpy.data.objects[n].matrix_world)-d['matrix']))) for n,d in sourcefaces.items())
report['face']['feature_meshes_unchanged']=all(d['co'] is None or np.array_equal(np.array([tuple(v.co) for v in bpy.data.objects[n].data.vertices]),d['co']) for n,d in sourcefaces.items())
hd=[oldhead.find_nearest(Vector(q))[3] for q in co[co[:,2]>4.05][::3]]
report['face']['head_surface_distance_max']=float(max(hd));report['face']['head_surface_distance_p99']=float(np.quantile(hd,.99))

hands={}
for side,label in [('.L','left'),('.R','right')]:
 mask=np.array([sum(w for n,w in g.items() if n.endswith(side) and n.startswith(('hand','finger','thumb')))>.72 for g in groups])
 ff=[p for p in faces if all(mask[i] for i in p)];hands[label]=(mask,tree(co,ff))
 report[label+'_hand_vertices']=int(mask.sum())
 report[label+'_max_hand_color_component']=float(colors[mask,:3].max())
report['collisions']['hand_hand']=len(hands['left'][1].overlap(hands['right'][1]))
torso=np.array([not any(n.startswith(('upper_arm','forearm','hand','finger','thumb')) and w>.2 for n,w in g.items()) for g in groups])
torsofaces=[p for p in faces if all(torso[i] for i in p)];tt=tree(co,torsofaces)
for label,(mask,ht) in hands.items():report['collisions'][label+'_hand_torso']=len(ht.overlap(tt))
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('Sword_') or o.hide_render:continue
 wc,wf,_,_=mesh(o);wt=tree(wc,wf)
 for label,(mask,ht) in hands.items():report['collisions'][label+'_'+o.name]=len(ht.overlap(wt))
 if o.name=='Sword_Blade':
  report['collisions']['blade_torso']=len(wt.overlap(tt));report['blade_min_z']=float(wc[:,2].min())
 if o.name=='Sword_Grip':
  for label,(mask,ht) in hands.items():
   hits=[(q,wt.find_nearest(Vector(q))) for q in co[mask][::3]]
   report[label+'_grip_nearest']=float(min(hit[3] for q,hit in hits))
   report[label+'_grip_signed_penetration_sample']=float(max(max(0.,-(Vector(q)-hit[0]).dot(hit[1])) for q,hit in hits))

# A welded shoulder must be in the same connected component as the abdomen.
bm=bmesh.new();bm.from_mesh(b.data);seen=set();components=[]
for v in bm.verts:
 if v.index in seen:continue
 todo=[v];seen.add(v.index);count=0
 while todo:
  u=todo.pop();count+=1
  for e in u.link_edges:
   q=e.other_vert(u)
   if q.index not in seen:seen.add(q.index);todo.append(q)
 components.append(count)
report['skin_connected_components']=sorted(components,reverse=True)
report['boundary_edges']=sum(not e.is_manifold for e in bm.edges);bm.free()

armweight=np.array([sum(w for n,w in g.items() if n.startswith(('upper_arm','forearm','hand','finger','thumb'))) for g in groups])
belly=(np.abs(co[:,0])<.68)&(co[:,2]>1.7)&(co[:,2]<3.08)&(armweight<1e-8)
original=co[belly].copy()
for name,rot in [('raise_left',(.0,.0,.20)),('raise_right',(.0,.0,-.20))]:
 p=rig.pose.bones['upper_arm.L' if name=='raise_left' else 'upper_arm.R'];p.rotation_euler=rot;bpy.context.view_layer.update()
 posed,_,_,_=mesh(b,False)
 distances=np.linalg.norm(posed[belly]-original,axis=1);idx=np.flatnonzero(belly)[int(np.argmax(distances))]
 report['shoulder_deformation'][name]={'belly_max_displacement':float(distances.max()),'finite':bool(np.isfinite(posed).all()),'worst_point':co[idx].tolist(),'worst_weights':groups[idx]}
 p.rotation_euler=(0,0,0);bpy.context.view_layer.update()
with open(os.path.join(OUT,'validation.json'),'w') as f:json.dump(report,f,indent=2)
print('QA_REPORT',json.dumps(report),flush=True)
if '--checks-only' in sys.argv:sys.exit(0)
render('face_v29',camera('QA Face',(0,-8,4.60),(0,-.2,4.50),1.25),600,600)
render('shoulder_detail',camera('QA Shoulders',(.2,-9,4.3),(0,-.05,3.38),2.85),1100,700)

bpy.ops.wm.open_mainfile(filepath=NEUTRAL);bpy.context.scene.frame_set(1)
for name,loc in [('front',(0,-12,2.5)),('side',(-12,0,2.5)),('back',(0,12,2.5))]:
 render('neutral_'+name,camera('QA '+name,loc,(0,0,2.50),5.5),620,780)
print('VERIFICATION_COMPLETE',flush=True)

"""Local finger sculpt pass. Preserve pose, colours and all other geometry."""
import bpy,os,math,json,shutil,sys,hashlib
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP=r'C:\Users\L\.codex\visualizations\2026\10\23\01a166ac-17cc-79c0-a443-2a4a3a7357fd\yellow_character_history\before_finger_detail'
os.makedirs(BACKUP,exist_ok=True)
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def catmull(vals,t):
 i=min(int(t),len(vals)-2);u=t-i;a=vals[max(0,i-1)];b=vals[i];c=vals[i+1];d=vals[min(len(vals)-1,i+2)]
 return .5*(2*b+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)
def paths(mode):
 A=Vector((-.63,0,.7766)).normalized();U=Vector((A.z,0,-A.x));F=Vector((0,-1,0));guard=Vector((.07,-1.36,2.72));result={}
 for side,sign in [('.L',-1),('.R',1)]:
  if mode=='grip' and side=='.R':
   station=guard-A*.31+F*.055
   for i,off in enumerate([-.108,0,.108]):
    result['finger'+str(i)+side]=[station+A*(off+.006*t)+U*(.19-.32*t)+F*(.115-.015*math.sin(math.pi*t)) for t in [0,.16,.32,.48,.64,.80,.94,1]]
   result['thumb'+side]=[station+A*(.18+.035*t)+U*(.29-.22*t)+F*(.12-.015*t) for t in [0,.2,.4,.6,.8,1]]
  elif mode=='grip':
   N=(U*(sign*.77)+Vector((0,1,0))*.638).normalized();T=A.cross(N).normalized()*(1 if sign<0 else -1);station=guard+A*.32
   for i,off in enumerate([-.112,0,.112]):
    p=[]
    for j in range(10):
     t=j/9;angle=.24+t*2.72;r=.170*(1-smooth(0,.38,t))+.114*smooth(0,.38,t)
     p.append(station+A*(off+.008*math.sin(math.pi*t))+r*(N*math.cos(angle)+T*math.sin(angle)))
    result['finger'+str(i)+side]=p
   off=-.190
   result['thumb'+side]=[station+A*(off+.015*t)+.155*(N*math.cos(-.32-t*1.84)+T*math.sin(-.32-t*1.84)) for t in [0,.15,.30,.45,.60,.75,.90,1]]
  else:
   for i in range(3):
    y=-.275+i*.11;z=[1.68,1.66,1.71][i]
    result['finger'+str(i)+side]=[Vector((sign*1.18,y,1.86)),Vector((sign*1.19,y-.007,1.77)),Vector((sign*1.17,y-.017,z+.03)),Vector((sign*1.155,y-.02,z))]
   result['thumb'+side]=[Vector((sign*1.145,-.265,2.015)),Vector((sign*1.095,-.35,1.97)),Vector((sign*1.08,-.38,1.89)),Vector((sign*1.1,-.37,1.85))]
 return result
def sample_path(points):
 cols=list(zip(*points));samples=[];count=500
 for j in range(count):samples.append(Vector([catmull(c,j/(count-1)*(len(points)-1)) for c in cols]))
 length=[0.]
 for a,b in zip(samples[:-1],samples[1:]):length.append(length[-1]+(b-a).length)
 tangents=[(samples[min(count-1,j+1)]-samples[max(0,j-1)]).normalized() for j in range(count)]
 kd=KDTree(count)
 for j,q in enumerate(samples):kd.insert(q,j)
 kd.balance();return samples,tangents,[x/length[-1] for x in length],kd

reports={}
for mode,filename in [('grip','YellowFriend_v29_reference_grip.blend'),('neutral','YellowFriend_v29_neutral.blend')]:
 target=os.path.join(OUT,filename);backup=os.path.join(BACKUP,filename)
 bpy.ops.wm.open_mainfile(filepath=target)
 current_body=bpy.data.objects['YellowFriend | continuous shoulders and rebuilt hands']
 if current_body.get('Finger_revision'):
  if '--redo' not in sys.argv:
   print('FINGER_DETAIL_ALREADY_APPLIED',mode,flush=True);continue
  backup=current_body.get('Finger_source_backup',backup)
  bpy.ops.wm.open_mainfile(filepath=backup)
 else:
  source_hash=hashlib.sha256(open(target,'rb').read()).hexdigest()
  backup=os.path.join(BACKUP,os.path.splitext(filename)[0]+'_'+source_hash[:12]+'.blend')
  if not os.path.exists(backup):shutil.copy2(target,backup)
 scene=bpy.context.scene;scene.frame_set(1)
 body=bpy.data.objects['YellowFriend | continuous shoulders and rebuilt hands']
 before=np.array([v.co[:] for v in body.data.vertices]);before_colors=np.array([c.color[:] for c in body.data.color_attributes['SkinColor'].data])
 names={g.index:g.name for g in body.vertex_groups};curves={k:sample_path(v) for k,v in paths(mode).items()}
 groups={}
 for side in ['.L','.R']:
  for stem in ['finger0','finger1','finger2','thumb']:
   groups[stem+side]={body.vertex_groups[stem+f'_0{j}'+side].index for j in [1,2]}
 changed=[];perfinger={}
 for v in body.data.vertices:
  weights={g.group:g.weight for g in v.groups}
  influences={name:sum(weights.get(i,0.) for i in ids) for name,ids in groups.items()}
  name=max(influences,key=influences.get);influence=influences[name]
  if influence<.28:continue
  samples,tangents,arc,kd=curves[name];_,idx,dist=kd.find(v.co)
  if dist>.090:continue
  t=arc[idx];strength=smooth(.28,.78,influence)*smooth(.07,.22,t)
  if strength==0:continue
  q=samples[idx];tangent=tangents[idx];d=v.co-q;radial=d-tangent*d.dot(tangent);radius=radial.length
  normal=radial.normalized() if radius>1e-6 else v.normal.normalized();front=Vector((0,-1,0));dorsal=front-tangent*front.dot(tangent)
  if dorsal.length<.1:dorsal=Vector((0,0,1))-tangent*tangent.z
  dorsal.normalize();lateral=tangent.cross(dorsal).normalized();facing=normal.dot(dorsal)
  thumb=name.startswith('thumb');joints=[.43] if thumb else [.31,.65]
  # Slim shafts with small knuckle volumes, rather than uniform cylinders.
  scale=.970+sum((.09 if thumb else .085)*math.exp(-((t-j)/(.115 if thumb else .092))**2) for j in joints)
  scale-=.015*smooth(.76,.94,t)
  delta=radial*(scale-1.)
  # A low, rounded distal pad. Keep a soft dome without adding a nail.
  pad=math.exp(-((t-.855)/.12)**2)
  delta-=dorsal*radial.dot(dorsal)*(.040*pad if facing>0 else -.025*pad)
  # Shallow curved joint folds on the visible side, never ring-like grooves.
  crease=0.
  for j in joints:
   shifted=j+.020*(normal.dot(lateral)**2)
   crease+=math.exp(-((t-shifted)/.027)**2)
  delta-=normal*(.0009*crease*smooth(.0,.80,facing))
  # The supporting fingers have a subtle length hierarchy and relaxed ends.
  if mode=='grip' and name.endswith('.R') and not thumb:
   offset={'finger0.R':-.015,'finger1.R':.004,'finger2.R':-.004}[name]
   delta+=tangent*offset*smooth(.42,.98,t)
   delta+=dorsal*.0025*math.sin(math.pi*smooth(.55,1.,t))
  delta*=strength
  if delta.length>0:
   v.co+=delta;changed.append(v.index);perfinger[name]=perfinger.get(name,0)+1
 # Relax sampling ripples locally; cap vertices take the same end offset as
 # the surrounding rings, so a shortened finger cannot leave a pointed tip.
 after=np.array([v.co[:] for v in body.data.vertices])
 edges=np.array([e.vertices[:] for e in body.data.edges]);src=np.r_[edges[:,0],edges[:,1]];dst=np.r_[edges[:,1],edges[:,0]]
 counts=np.maximum(np.bincount(src,minlength=len(after)),1)
 for _ in range(2):
  neighbor=np.zeros_like(after);np.add.at(neighbor,src,after[dst]);neighbor/=counts[:,None]
  after[changed]=after[changed]*.88+neighbor[changed]*.12
 for i in changed:body.data.vertices[i].co=after[i]
 body.data.update()
 after=np.array([v.co[:] for v in body.data.vertices]);delta=np.linalg.norm(after-before,axis=1)
 outside=np.ones(len(before),dtype=bool);outside[changed]=False
 after_colors=np.array([c.color[:] for c in body.data.color_attributes['SkinColor'].data])
 report={'mode':mode,'edited_vertices':len(changed),'per_finger':perfinger,'max_finger_displacement':float(delta.max()),'max_nonfinger_displacement':float(delta[outside].max()),'all_skin_colors_unchanged':bool(np.array_equal(before_colors,after_colors)),'topology_unchanged':len(before)==len(after),'source_sha256':hashlib.sha256(open(backup,'rb').read()).hexdigest(),'detail':'Tapered phalanges, rounded pads, small knuckle volumes, shallow curved folds; subtle support-finger length hierarchy.'}
 assert report['max_nonfinger_displacement']==0 and report['all_skin_colors_unchanged']
 body['Finger_revision']='v29.1: local knuckle/pad/crease sculpt. Other geometry, colours, rig and weapon preserved.'
 body['Finger_source_backup']=backup
 scene['Finger_detail_note']='Local finger sculpt only; static pose and earlier feet/belly/face corrections retained.'
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=target)
 reports[mode]=report;print('FINGERS_REFINED',json.dumps(report),flush=True)
if reports:
 with open(os.path.join(OUT,'finger_detail_report.json'),'w') as f:json.dump(reports,f,indent=2)
old_detail=os.path.join(OUT,'grip_detail.png')
if os.path.exists(old_detail) and not os.path.exists(os.path.join(BACKUP,'grip_detail.png')):shutil.copy2(old_detail,os.path.join(BACKUP,'grip_detail.png'))
print('FINGER_DETAIL_PASS_COMPLETE',flush=True)

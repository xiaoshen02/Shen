"""Restore v28 ivory-belly extent; change vertex colours only."""
import bpy,os,json,math,hashlib
import numpy as np
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def mix(a,b,t):return tuple(a[i]*(1-t)+b[i]*t for i in range(3))
report={}
for mode,name in [('grip','YellowFriend_v29_reference_grip.blend'),('neutral','YellowFriend_v29_neutral.blend')]:
 path=os.path.join(OUT,name);bpy.ops.wm.open_mainfile(filepath=path)
 body=bpy.data.objects['YellowFriend | continuous shoulders and rebuilt hands']
 coords=np.array([v.co[:] for v in body.data.vertices]);before=np.array([c.color[:] for c in body.data.color_attributes['SkinColor'].data])
 names={g.index:g.name for g in body.vertex_groups};ca=body.data.color_attributes['SkinColor']
 before_mask=[];after_mask=[];hands=[]
 for v in body.data.vertices:
  x,y,z=v.co;aw=sum(g.weight for g in v.groups if names[g.group].startswith(('upper_arm','forearm','hand','finger','thumb')))
  hands.append(aw>.70)
  base=mix((1.,.56,.016),(1.,.76,.045),smooth(1.3,4.85,z))
  eligible=aw<.35 and 1.20<z<3.72
  old_patch=max(0,min(1,(before[v.index,2]-base[2])/(.59-base[2]))) if eligible else 0
  if eligible:
   # v28: belly centre 2.64, upper radius .88, lower radius .81.
   dz=(z-2.64)/(.88 if z>2.64 else .81);q=(x/1.14)**2+dz*dz
   patch=(1-smooth(.94,1.06,q))*(1-smooth(-.25,-.10,y))*(1-smooth(.08,.35,aw))
   ca.data[v.index].color=(*mix(base,(.98,.965,.91),patch),1)
  else:patch=0
  before_mask.append(old_patch);after_mask.append(patch)
 after=np.array([c.color[:] for c in ca.data]);hands=np.array(hands)
 # Surface-area integral of the colour masks (triangle fan for polygons).
 areas=[0.,0.]
 for p in body.data.polygons:
  ids=list(p.vertices)
  for j in range(1,len(ids)-1):
   tri=[ids[0],ids[j],ids[j+1]];a,b,c=coords[tri];area=np.linalg.norm(np.cross(b-a,c-a))*.5
   areas[0]+=area*sum(before_mask[i] for i in tri)/3;areas[1]+=area*sum(after_mask[i] for i in tri)/3
 report[mode]={'vertex_geometry_unchanged':bool(np.array_equal(coords,np.array([v.co[:] for v in body.data.vertices]))),'hand_color_max_change':float(np.abs(after[hands]-before[hands]).max()),'belly_surface_area_before':float(areas[0]),'belly_surface_area_after':float(areas[1]),'color':'.98, .965, .91 (v28 ivory)','mask':'v28 centre and vertical extent; soft shoulder boundary'}
 body['Belly_revision']='Restored v28 ivory coverage: centre z 2.64, upper radius .88, lower .81. Vertex colours only; geometry, hands, feet, face and pose unchanged.'
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=path)
 print('BELLY_RESTORED',mode,report[mode],flush=True)
with open(os.path.join(OUT,'belly_validation.json'),'w') as f:json.dump(report,f,indent=2)

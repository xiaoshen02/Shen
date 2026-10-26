import bpy,os,math
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF=os.path.join(os.path.dirname(OUT),'references','pose.jpg')
for name in ['YellowFriend_v29_reference_grip.blend','YellowFriend_v29_neutral.blend']:
 path=os.path.join(OUT,name);bpy.ops.wm.open_mainfile(filepath=path)
 body=bpy.data.objects['YellowFriend | continuous shoulders and rebuilt hands']
 bpy.context.view_layer.objects.active=body;bpy.ops.object.select_all(action='DESELECT');body.select_set(True)
 sub=next(m for m in body.modifiers if m.type=='SUBSURF')
 # Subdivide the bind mesh and its weights first, then deform. This keeps
 # zero-arm-weight belly vertices stationary during shoulder movement.
 while list(body.modifiers).index(sub)>0:bpy.ops.object.modifier_move_up(modifier=sub.name)
 body['Deform_order']='Subdivision in bind space, followed by armature; zero-weight belly vertices remain stationary.'
 image=bpy.data.images.load(REF,check_existing=True)
 if not image.packed_file:image.pack()
 collection=bpy.data.collections.get('REFERENCES | Packed orthographic images')
 if collection is None:
  collection=bpy.data.collections.new('REFERENCES | Packed images');bpy.context.scene.collection.children.link(collection)
 ref=bpy.data.objects.new('Reference | requested low-guard pose',None);collection.objects.link(ref)
 ref.empty_display_type='IMAGE';ref.data=image;ref.empty_display_size=6.3;ref.rotation_euler=(math.pi/2,0,0);ref.location=(-3,1.5,2.5);ref.color[3]=.35;ref.hide_render=True;ref.hide_viewport=True
 bpy.context.scene['Delivery_note']='Static reference pose. This revision has a new sculpt-aligned bind; do not apply legacy v28 actions. Source front/side/back and pose reference images are packed.'
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=path)
 print('FINALIZED',name,flush=True)

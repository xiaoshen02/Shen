"""Create and CRC-verify a recoverable archive before PowerShell cleanup."""
from pathlib import Path
import zipfile,json,os,hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'yellow_character';HISTORY=BASE/'history';HISTORY.mkdir(exist_ok=True)
old=['_archive_legacy_2026-10-21','v12_sword_animation','v15_arm_blend','v20_no_shoulder_cap','v21_sword_ready','v22_independent_arms','v23_arm_deformation_fix','v24_blender_export','v25_two_hand_grip','v26_reference_start','v27_reference_refined','Yellow_Friend.blend','小满-交接说明.md','Codex任务单-Mixamo预操作.md']
old+=['v28_hand_refined/'+n for n in ['scripts','hand_detail.png','full_body.png','grip_validation.json','grip_tuning.json','使用说明.md']]
targets=[(BASE/n).resolve() for n in old if (BASE/n).exists()]
for p in targets:
 if not p.is_relative_to(BASE.resolve()) or p==BASE.resolve():raise RuntimeError('Unsafe archive input '+str(p))
files=[]
for p in targets:files.extend(sorted(p.rglob('*')) if p.is_dir() else [p])
files=[p for p in files if p.is_file()]
dest=HISTORY/'旧版模型_2026-10-23.zip'
if dest.exists():raise RuntimeError('Archive already exists; refusing to overwrite')
manifest={'workspace':str(ROOT),'archive':str(dest),'targets':[str(p) for p in targets],'files':len(files),'source_bytes':sum(p.stat().st_size for p in files),'entries':[{'path':str(p.relative_to(BASE)).replace(os.sep,'/'),'bytes':p.stat().st_size} for p in files]}
print('ARCHIVING',len(files),manifest['source_bytes'],flush=True)
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(BASE)))
 z.writestr('归档清单.json',json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(dest) as z:
 bad=z.testzip()
 if bad:raise RuntimeError('Archive CRC failed: '+bad)
 if len(z.infolist())!=len(files)+1:raise RuntimeError('Archive file count mismatch')
manifest['crc_verified']=True;manifest['archive_bytes']=dest.stat().st_size
manifest['archive_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
with open(HISTORY/'cleanup_manifest.json','w',encoding='utf-8') as f:json.dump(manifest,f,ensure_ascii=False,indent=2)
print('ARCHIVE_VERIFIED',json.dumps({k:v for k,v in manifest.items() if k not in ['entries','targets']},ensure_ascii=False),flush=True)

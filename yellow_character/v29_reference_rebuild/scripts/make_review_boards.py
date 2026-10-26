from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
OUT=Path(__file__).resolve().parents[1]
FONT='C:/Windows/Fonts/msyh.ttc'
font=ImageFont.truetype(FONT,28);small=ImageFont.truetype(FONT,20)
board=Image.new('RGB',(1900,870),'white');draw=ImageDraw.Draw(board)
for i,(name,label) in enumerate([('neutral_front.png','正面'),('neutral_side.png','侧面'),('neutral_back.png','背面')]):
 draw.text((i*630+25,16),label,fill=(35,35,35),font=font)
 im=Image.open(OUT/name).convert('RGB');im.thumbnail((620,780));board.paste(im,(i*630+5,60))
draw.text((25,843),'v29 · 垂臂建模检查 · 脚型与肚皮浅色范围已同步',fill=(65,65,65),font=small)
board.save(OUT/'three_views.jpg',quality=94)
board=Image.new('RGB',(1280,1080),'white');draw=ImageDraw.Draw(board)
draw.text((25,18),'参考姿势',fill=(35,35,35),font=font);draw.text((480,18),'v29 当前模型',fill=(35,35,35),font=font)
for p,box,xy in [(OUT.parent/'references'/'pose.jpg',(430,960),(10,65)),(OUT/'grip_full.png',(820,960),(450,65))]:
 im=Image.open(p).convert('RGB');im.thumbnail(box);board.paste(im,(xy[0]+(box[0]-im.width)//2,xy[1]+(box[1]-im.height)//2))
draw.text((25,1040),'上手握柄 · 下手扶剑根 · 左肘较高、右前臂下收',fill=(65,65,65),font=small)
board.save(OUT/'pose_comparison.jpg',quality=94)
print('REVIEW_BOARDS_READY')

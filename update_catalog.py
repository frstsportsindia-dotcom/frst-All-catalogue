from pathlib import Path
from datetime import date
import json,re,shutil
root=Path(__file__).parent
img=root/'images'; img.mkdir(exist_ok=True)
inc=root/'incoming'
config={'cricket':('CR','Cricket'),'football':('FB','Football'),'volleyball':('VB','Volleyball'),'basketball':('BB','Basketball')}
# load existing manifest
p=root/'designs.js'
try:
    raw=p.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';')
    designs=json.loads(raw)
except Exception: designs=[]
    # Remove catalogue entries whose image file no longer exists
designs = [
    d for d in designs
    if (root / d.get("image", "")).exists()
]
existing={d.get('code') for d in designs}
for folder,(prefix,sport) in config.items():
    src=inc/folder
    if not src.exists(): continue
    nums=[int(m.group(1)) for d in designs if (m:=re.fullmatch(prefix+r'-(\d+)',d.get('code','')))]
    n=max(nums,default=0)+1
    for f in sorted([x for x in src.iterdir() if x.is_file() and not x.name.startswith('.')]):
        ext=f.suffix.lower()
        if ext not in {'.webp','.jpg','.jpeg','.png'}: continue
        code=f'{prefix}-{n:03d}'
        dest=img/f'{code.lower()}{ext}'
        while dest.exists() or code in existing:
            n+=1; code=f'{prefix}-{n:03d}'; dest=img/f'{code.lower()}{ext}'
        shutil.move(str(f),str(dest))
        designs.append({'code':code,'sport':sport,'image':f'images/{dest.name}','date':date.today().isoformat()})
        existing.add(code); n+=1
# newest first in manifest too
designs.sort(key=lambda d:(d.get('date',''),d.get('code','')),reverse=True)
p.write_text('window.FRST_DESIGNS = '+json.dumps(designs,indent=2)+';\n',encoding='utf-8')

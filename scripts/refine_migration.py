"""Apply reviewed editorial corrections without changing original memorial articles."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data.json';d=json.loads(p.read_text(encoding='utf-8'))
def fix(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if isinstance(v,str) and k in ['body','preface','conventions','cover']:x[k]=v.replace('\\n','\n')
            else:fix(v)
    elif isinstance(x,list):
        for v in x:fix(v)
fix(d)
for c in d['characters']:
    if c['imagePath'] and not (ROOT/c['imagePath']).is_file():
        c['legacyImagePath']=c['imagePath'];c['imagePath']=''
        c['editorialNotes'].append('旧站头像文件缺失，已采用姓名占位；原路径保存在 legacyImagePath。')
    if c['id']=='person-emma':
        c['imagePath']='';c['editorialNotes']=['旧站存在艾玛图片，但与“改开艾玛”身份对应未核，暂用姓名占位。']
# Volume one has a complete existing body of events, but its own introduction is pending.
d['volumes'][0]['completion']='partial'
d['volumes'][0]['editorialNotes']=['卷内已有纪事，独立卷首概述尚待补写。']
for c in d['characters']:
    if c['id']=='im':
        c['articles'][0]['completion']='partial'
        c['editorialNotes'].append('原稿“复出”小节仅有标题，正文未完。')
# Correct historical roles using only explicit statements from the manuscript.
byname={c['name']:c for c in d['characters']}
for t in d['tenures']:
    if t['characterId']==byname['Imagedunuage']['id'] and t['role']=='manager' and t['groupId']=='main-system':
        t['time'].update(end='2025-12-16',label='起始待考 — 2025.12.16');t['sourceRefs']=[{'sourceId':'source-history','pages':[12]}]
    if t['characterId']==byname['洗涤剂量子']['id'] and t['role']=='manager' and t['time']['start']=='2025-11-18':
        t['time'].update(start=None,label='2025.10.8当选；11.18再次任命，连续性待核')
        t['notes']='PDF第2页记10月8日当选、第9页记11月18日任命；无法据此断定期间是否中断。';t['sourceRefs']=[{'sourceId':'source-history','pages':[2,9]}]
    if '任职范围暂参考旧站备注' in t.get('notes',''):
        t['sourceRefs'].append({'sourceId':'source-legacy','pages':[]})
# PDF also expressly places eggplant in the second-generation management team.
if not any(t['characterId']==byname['茄肉粥']['id'] for t in d['tenures']):
    d['tenures'].append({'id':'term-eggplant','characterId':byname['茄肉粥']['id'],'groupId':'main-system','role':'manager','time':{'label':'心上秋任群主期间增补；珺宁时期退出，精确起止待考','start':None,'end':None,'dates':[],'ongoing':False,'precision':'unknown'},'notes':'据第二代领导集体概述。','generationIds':['gen2'],'publication':'published','sourceRefs':[{'sourceId':'source-history','pages':[17]}]})
for t in d['tenures']:
    if t['characterId']==byname['绩溪soyorin']['id'] and t['groupId']=='main-system' and t['role']=='owner':t['generationIds']=['gen1']
    if t['groupId'] in ['g3','g4','g5','g6','g1','g8','g9','g-backup','g-branch']:t['generationIds']=['gen1']
    if t['characterId']==byname['洗涤剂量子']['id'] and t['role']=='owner':t['generationIds']=['gen2']
    if t['characterId']==byname['心上秋']['id'] and t['role']=='owner' and t['groupId']=='main-system':t['generationIds']=['gen2']
    if t['characterId']==byname['珺宁']['id'] and t['role']=='owner':t['generationIds']=['gen2','gen3']
for e in d['events']:
    e['treatiseIds']=[t['id'] for t in d['treatises'] if {'xicao':'希槽','toucao':'偷槽','pubar':'朴吧','erxicao':'二希槽','maocao':'猫槽','bangcao':'邦系'}[t['id']] in e['body']]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Reviewed migration corrections applied.')

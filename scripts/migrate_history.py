"""Auditable one-time migration: python scripts/migrate_history.py source.pdf."""
import sys,json,re,html,hashlib,shutil,subprocess
from pathlib import Path
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
BASE='60e40f6'
SOURCE=Path(sys.argv[1])
target=ROOT/'data.json'
if json.loads(target.read_text(encoding='utf-8')).get('schemaVersion')==2:
    raise SystemExit('Refusing to overwrite v2 content; explicitly restore the original data before re-running.')
legacy=json.loads(subprocess.check_output(['git','show',f'{BASE}:data.json'],cwd=ROOT))
lines=[]
for pn,page in enumerate(pdfplumber.open(SOURCE).pages,1):
    for ln,line in enumerate(page.extract_text_lines()):
        line.update(page=pn,line=ln);lines.append(line)
def pos(p,l): return next(i for i,x in enumerate(lines) if (x['page'],x['line'])==(p,l))
# Manually verified typography/page boundaries, including continuations across pages.
anchors=[('preface',1,3),('conventions',1,9),('volume-heading',1,12),('gen1-heading',1,13),('gen1',1,15),('foundation',1,23),('first-three',1,33),('election',2,1),('dachui',2,27),('soyo',3,5),('chendie',3,18),('wangmeng',3,33),('november',4,14),('crisis1',4,29),('regency',4,34),('station',5,7),('repression',5,23),('night-talk',6,4),('transition',6,22),('branch',6,32),('retreat',7,2),('embers',7,14),('crisis2',7,25),('reclaim',7,37),('shantou',8,25),('appointments',9,15),('kong-crisis',9,30),('leaders1',9,31),('bio-meng',9,32),('bio-jixi',10,7),('bio-xinxi',10,19),('managers1',10,37),('bio-moon',10,38),('bio-yjd',11,15),('bio-im',11,39),('bio-dachui',12,34),('bio-chendie',13,10),('bio-ml',13,40),('bio-wslf',14,13),('pubar',14,39),('xicao',15,8),('threeletters',15,23),('erxicao',15,36),('bangcao',16,17),('relations',16,19),('toucao',16,26),('maocao',16,37),('gen2-heading',16,39),('gen2',17,0),('leaders2',17,19),('gen3-heading',18,15),('gen3',18,17)]
def body_html(items):
    paragraphs=[];buf=[]
    def flush():
        if buf: paragraphs.append('<p>'+''.join(buf)+'</p>');buf.clear()
    for l in items:
        if l['x0']>104: flush()
        text=html.escape(l['text'])
        red=any(isinstance(c.get('non_stroking_color'),(tuple,list)) and len(c['non_stroking_color'])>=3 and c['non_stroking_color'][0]>.5 and c['non_stroking_color'][1]<.2 for c in l['chars'])
        if red:text='<span class="source-red">'+text+'</span>'
        if l['text'].startswith('【') or l['text']=='复出':flush();paragraphs.append('<h3>'+text+'</h3>')
        else:buf.append(text)
    flush();return '\n'.join(paragraphs)
segments={};coverage=[]
for i,(key,p,l) in enumerate(anchors):
    a=pos(p,l);b=pos(*anchors[i+1][1:]) if i+1<len(anchors) else len(lines);part=lines[a:b]
    segments[key]={'body':body_html(part if key in ['gen1','gen2','gen3'] else part[1:]),'heading':part[0]['text'],'pages':sorted(set(x['page'] for x in part))}
    coverage.append({'key':key,'from':[p,l],'to':[lines[b-1]['page'],lines[b-1]['line']],'lineCount':len(part)})
def refs(key):return [{'sourceId':'source-history','pages':segments[key]['pages']}]
def plain(s):return re.sub('<[^>]+>','',s)
def temporal(label='',start=None,end=None,precision='day',dates=None,ongoing=False):return dict(label=label,start=start,end=end,precision=precision,dates=dates or [],ongoing=ongoing)
def record(id,title,key=None,**kw):
    body=segments[key]['body'] if key else ''
    return dict(id=id,title=title,body=body,summary='',publication='published',completion='complete' if len(plain(body))>30 else 'pending',sourceRefs=refs(key) if key else [],editorialNotes=[],**kw)
d={**legacy,'schemaVersion':2,'siteTitle':'素槽群史','siteSubtitle':'纪·传·表·志｜素槽英灵殿','epigraph':'以纪述其事，以传记其人，以表明其序，以志存其详。','preface':segments['preface']['body'],'conventions':segments['conventions']['body'],'publicationNote':'网站版本经作者确认全文公开。原稿黑红字凡例作为版本史料保留，红字内容亦收录于本版。','updatedAt':'2026-10-27','sources':[{'id':'source-history','title':'长崎素世爱与吐槽吧史','author':'洗涤剂量子','publisher':'素槽群史编纂委员会','path':'sources/history.pdf','pageCount':18,'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},{'id':'source-legacy','title':'改造前英灵殿数据','revision':BASE}],'migration':{'fromCommit':BASE,'originalCharacters':len(legacy['characters']),'originalArticles':sum(len(c['articles']) for c in legacy['characters']),'sections':coverage,'cover':body_html(lines[:3]),'archivedArticles':[]}}
for key in ['generations','volumes','periods','events','groups','groupStages','tenures','treatises','media']:d[key]=[]
for i,(start,end) in enumerate([('2025-10-03','2025-11-21'),('2025-11-21','2026-09-07'),('2026-09-07',None)],1):
    d['generations'].append(record('gen'+str(i),'第'+'一二三'[i-1]+'代领导集体','gen'+str(i),order=i,characterIds=[],time=temporal(f'{start} — {end or "今"}',start,end,ongoing=end is None)))
vols=[('gen1','第一代领导集体纪事','2025-10-03','2025-11-21'),('gen2','洗涤剂量子任群主期间','2025-11-21','2026-01-21'),('gen2','心上秋任群主期间','2026-01-21','2026-05-30'),('gen2','珺宁任群主期间','2026-05-30','2026-09-07'),('gen3','第三代领导集体纪事','2026-09-07',None)]
for i,(g,title,start,end) in enumerate(vols,1):d['volumes'].append(record('vol'+str(i),title,generationId=g,order=i,time=temporal(f'{start} — {end or "今"}',start,end,ongoing=end is None)))
periods=[('first-three','前三群时期',None,'2025-10-03','2025-10-15'),('soyo','SOYO 爱槽吧时期',None,'2025-10-15','2025-10-29'),('november','11 月动荡时期',None,'2025-10-29','2025-11-21'),('crisis1','第一次素槽危机','november','2025-10-29','2025-11-03'),('transition','过渡时期','november','2025-11-01','2025-11-18'),('crisis2','第二次素槽危机','november','2025-11-18','2025-11-21')]
for i,(key,title,parent,start,end) in enumerate(periods):d['periods'].append(record(key,title,key,volumeId='vol1',parentId=parent,order=i,time=temporal(f'{start} — {end}',start,end)))
d['periods'][3]['editorialNotes']=['原稿第一次危机与过渡时期时间交叠，保留原记载。']
events=[('foundation','素槽的建立',None,'2025 年夏—2025.10.3',None,'2025-10-03'),('election','绩溪选举','first-three','2025.10.8','2025-10-08',None),('dachui','肃清大锤哥流毒','first-three','2025.10.8、10.12、10.24','2025-10-08','2025-10-24'),('chendie','肃清陈爹流毒','soyo','2025.10.18','2025-10-18',None),('wangmeng','炒作王梦 cp','soyo','2025 年 10 月',None,None),('regency','眼镜豆摄政','crisis1','2025.10.29','2025-10-29',None),('station','素槽水电站扩大会议成立','crisis1','2025.10.31','2025-10-31',None),('repression','素槽大压抑','crisis1','2025.11.1','2025-11-01',None),('night-talk','山头夜话','crisis1','2025.11.2 凌晨','2025-11-02',None),('branch','改组素槽第二支部','transition','2025.11.2','2025-11-02',None),('retreat','梦指导二次隐退','transition','2025.11.3','2025-11-03',None),('embers','延续火种','transition','2025.11.13','2025-11-13',None),('reclaim','梦指导归来和收群行动','crisis2','2025.11.18','2025-11-18',None),('shantou','山头事变','crisis2','2025.11.18','2025-11-18',None),('appointments','梦指导册封管理','crisis2','2025.11.18','2025-11-18',None),('kong-crisis','空指导危机','crisis2','2025.11.21','2025-11-21',None)]
for i,(key,title,p,label,start,end) in enumerate(events):d['events'].append(record(key,title,key,volumeId='vol1',periodId=p,relatedPeriodIds=['soyo'] if key=='dachui' else [],order=i,time=temporal(label,start,end,'approximate' if not start else 'day',['2025-10-08','2025-10-12','2025-10-24'] if key=='dachui' else []),characterIds=[],groupIds=[],treatiseIds=[]))
aliases={'晚安梦梦梦':['梦指导','梦思腊夫'],'Imagedunuage':['im','Im'],'绩溪soyorin':['绩溪','绩溪 soyorin'],'微笑小月亮':['小月亮'],'眼镜豆':['眼睛豆'],'陕西大锤哥':['大锤哥'],'陈爹':['陈蝶','张vv','张 vv','汗蒸','李舒蕾'],'水银灯':['水指导','王教授梦女','深水静流','政研室来了个年轻教授'],'洗涤剂量子':['洗指导'],'心上秋':['秋'],'Setite Antediluvian':['SA','sa'],'Wanghaotain':['Wanghaotian','奶酪','wangtainhao'],'空割きめ':['空指导'],'高尔夫球爱好者':['高尔夫','高公'],'茄肉粥':['茄公'],'来日方长':['图案'],'平凡森林的虾仁蛋炒饭':['蛋炒饭'],'sangfei':['Sangfei'],'korman233':['Korman233']}
byname={c['name']:c for c in d['characters']}
for id,name,als in [('xinxi','新溪',['吧主']),('wslf','王思洛夫',['wslf','王斯洛夫']),('muqing','沐卿让恋',[]),('yuhua','玉华',[]),('houshunmi','厚顺米',[]),('wangmie','汪咩',[]),('teyi','特异人士',[]),('angel','纯良小天使',[]),('emma','改开艾玛',[]),('ling','铃',[])]:
    c={'id':'person-'+id,'name':name,'imagePath':'images/艾玛.png' if id=='emma' else '','homeSection':'toxic' if id in ['wangmie','teyi'] else 'main','homeRole':'','homeOrder':len(byname)+1,'status':'normal','statusText':'','homeNote':'','articles':[],'banners':[],'sidebarNav':[],'deathDate':'','deathDateLabel':'','bgColorFrom':'#1a2a3a','borderColor':'#b79864','hallTitle':name+' · 人物档案','hallSubtitle':'素槽群史人物列传','coupletLeft':'','coupletRight':'','hasStamp':False,'stampText':'','funeralCommittee':''}
    d['characters'].append(c);byname[name]=c;aliases[name]=als
bio_map={'晚安梦梦梦':'bio-meng','绩溪soyorin':'bio-jixi','新溪':'bio-xinxi','微笑小月亮':'bio-moon','眼镜豆':'bio-yjd','Imagedunuage':'bio-im','陕西大锤哥':'bio-dachui','陈爹':'bio-chendie','水银灯':'bio-ml','王思洛夫':'bio-wslf'}
for c in d['characters']:
    c.update(aliases=aliases.get(c['name'],[]),generationIds=[],publication='published',editorialNotes=[],sourceRefs=[{'sourceId':'source-legacy','pages':[]}])
    for a in c['articles']:
        a.update(publication='published',completion='complete',sourceRefs=[{'sourceId':'source-legacy','pages':[]}])
        if plain(a.get('body','')).strip() in ['', '在此填写正文内容。']:
            a['archived']=True;a['completion']='pending';d['migration']['archivedArticles'].append({'characterId':c['id'],'articleKey':a['key'],'reason':'原空白或占位文章'})
    key=bio_map.get(c['name']);b=segments[key]['body'] if key else ''
    c['articles'].insert(0,{'key':'biography','title':c['name']+'列传','meta':'群史编纂委员会 · 据原稿迁录' if key else '群史编纂委员会 · 待补','body':b,'publication':'published','completion':'complete' if b else 'pending','sourceRefs':refs(key) if key else []})
    c['defaultArticleKey']='biography';c['sidebarNav'].insert(0,{'tag':'列传','label':c['name']+'列传','articleKey':'biography','style':''})
    if key:c['generationIds']=['gen1'];c['sourceRefs']=refs(key)
second=['洗涤剂量子','心上秋','清角吹寒','Setite Antediluvian','珺宁','鑫','不知','Wanghaotain','空割きめ','风水云','矢禾女','sangfei','西园寺','米兰笛小铁匠','拉萨之虎','梦言jacobin','来日方长','平凡森林的虾仁蛋炒饭','圣人帕拉斯','渔歌子','自己互相监督','冯唐','麦列霍夫','林曦','沐卿让恋','KTN','三峡电网','玉华','厚顺米','四羟小娶','korman233','高尔夫球爱好者','茄肉粥','羲和','汪咩','特异人士','Imagedunuage','眼镜豆','微笑小月亮','绩溪soyorin','晚安梦梦梦','改开艾玛']
for gen,names in [('gen2',second),('gen3',['珺宁','清角吹寒','四羟小娶','korman233','玉华','纯良小天使'])]:
    for name in names:
        c=byname[name];c['generationIds'].append(gen)
        if not c['articles'][0]['body']:c['articles'][0]['sourceRefs']=[{'sourceId':'source-history','pages':[17,18]}]
byname['铃']['generationIds']=['gen1']
byname['沐鄉让恋']['editorialNotes']=['旧站为“沐鄉让恋”，PDF为“沐卿让恋”。身份尚未核定，暂不合并。']
byname['沐卿让恋']['editorialNotes']=['与旧站“沐鄉让恋”可能相关，尚未核定，暂单独保留。']
byname['绩溪soyorin']['editorialNotes']=['PDF第10页先记任群主至10月13日，后记10月12日迁群后不再任群主；准确卸任日待核。']
byname['高尔夫球爱好者']['editorialNotes']=['旧站备注为2026.12.20，计时字段为2025-12-20。旧字段留存，新群史按PDF所述2025年12月事件。']
for g in d['generations']:g['characterIds']=[c['id'] for c in d['characters'] if g['id'] in c['generationIds']]
for e in d['events']:
    text=plain(e['body']);e['characterIds']=[c['id'] for c in d['characters'] if any(len(n)>1 and n in text for n in [c['name']]+c['aliases'])]
topics=[('xicao','希槽志',[('xicao','椎名立希吐槽吧'),('threeletters','希槽历史：三字母事件'),('relations','希槽和素槽的关系')]),('maocao','猫槽志',[('maocao','要乐奈吐槽吧')]),('toucao','偷槽志',[('toucao','偷摸零吐槽吧')]),('pubar','朴吧志',[('pubar','朴正熙吧')]),('erxicao','二希槽志',[('erxicao','二阶堂希罗吐槽吧')]),('bangcao','邦系与槽系',[('bangcao','邦系和槽系')])]
for i,(id,title,chapters) in enumerate(topics):
    t=record(id,title,order=i,characterIds=[],eventIds=[],chapters=[record('chapter-'+key,title,key,order=j) for j,(key,title) in enumerate(chapters)])
    t['completion']='partial' if id in ['maocao','bangcao'] else 'complete';d['treatises'].append(t)
def group(id,name,system=False):d['groups'].append({'id':id,'name':name,'aliases':[],'isSystem':system,'publication':'published','notes':'','sourceRefs':[{'sourceId':'source-history','pages':[1,5,6,7,9]}]})
for id,name in [('main-system','素槽主群体系'),('night-system','素槽夜群／水电站体系'),('shantou-system','山头体系')]:group(id,name,True)
for id,name in [('g1','素槽1群／7群'),('g2','素槽2群'),('g3','素槽3群'),('g4','SOYO爱槽吧'),('g5','素槽5群'),('g6','原夜群／素槽6群'),('g8','不知夜群／素槽8群'),('g9','素槽9群'),('g10','素槽10群'),('g-branch','五洲四海／第二支部／中转群'),('g-backup','不知备用群'),('g-shantou','素槽水电站扩大会议／山头'),('g-night2','素槽水电站'),('g-huaming','花明楼水电站')]:group(id,name)
def stage(id,gid,cat,name,start,end,seq=None,notes='',label=None,pages=[1],ongoing=False):
    d['groupStages'].append({'id':id,'groupId':gid,'category':cat,'title':name,'sequence':seq,'order':len(d['groupStages']),'time':temporal(label or f'{start or "待考"} — {end or ("今" if ongoing else "待考")}',start,end,ongoing=ongoing),'notes':notes,'publication':'published','sourceRefs':[{'sourceId':'source-history','pages':pages}],'eventIds':[]})
stage('s1','g1','main','素槽1群','2025-10-03','2025-10-08',1,'转为禁言后备群，11月3日复用为7群。',pages=[1,2,7])
stage('s2','g2','main','素槽2群','2025-10-08','2025-10-12',2,'QQ安全中心警告后迁群。',pages=[1,2])
stage('s3','g3','main','素槽3群','2025-10-12','2025-10-15',3,'与SOYO爱槽吧合流。',pages=[1,3])
stage('s4','g4','main','SOYO 爱槽吧','2025-10-15','2025-10-29',4,'群主新溪；10月29日被封禁。',pages=[3,4,10])
stage('s5','g5','main','素槽5群','2025-10-29','2025-10-29',5,'仅存在约两小时。',pages=[4])
stage('s6','g6','main','素槽6群','2025-10-29','2025-11-03',6,'夜群转正。第6页11.1—11.3指梦指导回归阶段。',pages=[5,6,7])
stage('s7','g1','main','素槽7群','2025-11-03','2025-11-13',7,'复用1群，绩溪任群主。',pages=[6,7])
stage('s8','g8','main','素槽8群','2025-11-13','2025-11-18',8,'不知夜群重新启用。',pages=[6,7])
stage('s9','g9','main','素槽9群','2025-11-18','2025-11-21',9,'空指导危机时解散。',pages=[7])
stage('s10','g10','main','素槽10群','2025-11-21',None,10,'群主交接洗涤剂量子；结束日期未载。',pages=[7])
stage('s-night1','g6','night','素槽夜群',None,'2025-10-29',notes='SOYO时期建立，10月29日转正为6群。',label='2025.10.15—10.29期间建立；10.29转正',pages=[3,5])
stage('s-night-bz','g8','night','新夜群（不知）','2025-10-29','2025-11-13',notes='11月1日起封存，13日转为8群。',pages=[5,7])
stage('s-wuzhou','g-branch','night','五洲四海','2025-10-31','2025-11-02',notes='清角吹寒创建的非官方群。',pages=[6])
stage('s-branch','g-branch','night','素槽第二支部','2025-11-02','2025-11-13',notes='群主交眼镜豆，后改组中转群。',pages=[6,7])
stage('s-transfer','g-branch','night','素槽中转群','2025-11-13','2025-11-18',notes='永久禁言，收群行动时解散。',pages=[7,8])
stage('s-backup','g-backup','night','素槽备用群','2025-11-13','2025-11-18',notes='不知创建，收群行动时解散。',pages=[7,8])
stage('s-night2','g-night2','night','素槽水电站',None,None,notes='清角吹寒长期任群主；群聊起止未载。',label='第二代期间，起止待考',pages=[17])
stage('s-huaming','g-huaming','night','花明楼水电站','2026-04-12',None,notes='名称见PDF；建立日据旧站清角吹寒计时字段。',pages=[17]);d['groupStages'][-1]['sourceRefs'].append({'sourceId':'source-legacy','pages':[]})
stage('s-shantou-pre','g-shantou','shantou','山头前身（封存六人群）','2025-10-29','2025-10-31',notes='31日启用水电站名义。',pages=[5,12])
stage('s-shantou','g-shantou','shantou','素槽水电站扩大会议','2025-10-31','2025-11-18',notes='别称小山头、小汕头；山头事变后独立。',pages=[5,9,12])
stage('s-mall','g-shantou','shantou','新世纪百货商场','2025-11-18',None,notes='沿用同一群聊；后续群名和变更日待补。',label='2025.11.18改名；后续名称起止待考',pages=[9,12])
def tenure(name,gid,role,start=None,end=None,label='',notes='',sourcepages=[17],ongoing=False):
    c=byname[name];d['tenures'].append({'id':'term-'+str(len(d['tenures'])+1),'characterId':c['id'],'groupId':gid,'role':role,'time':temporal(label or f'{start or "待考"} — {end or ("今" if ongoing else "待考")}',start,end,ongoing=ongoing),'notes':notes,'generationIds':list(c['generationIds']),'publication':'published','sourceRefs':[{'sourceId':'source-history','pages':sourcepages}]})
tenure('绩溪soyorin','main-system','owner','2025-10-03',label='2025.10.3—10.12／10.13（待核）',notes='原稿第10页两种卸任日。',sourcepages=[2,10])
for name,gid,start,end in [('晚安梦梦梦','g3','2025-10-12','2025-10-15'),('新溪','g4','2025-10-15','2025-10-29'),('晚安梦梦梦','g5','2025-10-29','2025-10-29'),('眼镜豆','g6','2025-10-29','2025-11-01'),('晚安梦梦梦','g6','2025-11-01','2025-11-03'),('绩溪soyorin','g1','2025-11-03','2025-11-13'),('不知','g8','2025-10-29','2025-11-18'),('晚安梦梦梦','g9','2025-11-18','2025-11-21'),('洗涤剂量子','main-system','2025-11-21','2026-01-21'),('心上秋','main-system','2026-01-21','2026-05-30'),('清角吹寒','g-branch','2025-10-31','2025-11-02'),('眼镜豆','g-branch','2025-11-02','2025-11-18'),('不知','g-backup','2025-11-13','2025-11-18')]:tenure(name,gid,'owner',start,end,sourcepages=[2,4,5,6,7,10,16,17])
tenure('珺宁','main-system','owner','2026-05-30',notes='跨第二、三代连续任职。',sourcepages=[16,17,18],ongoing=True)
tenure('Imagedunuage','g-shantou','owner','2025-10-29','2026-01-31',notes='PDF记1月31日；旧计时1月30日保持原样。',sourcepages=[5,12])
tenure('心上秋','g-shantou','owner','2026-01-31',notes='卸任日期未载，不推定至今。',sourcepages=[12])
tenure('清角吹寒','night-system','owner',label='第二、三代期间，精确起止待考',sourcepages=[17,18])
for name in ['洗涤剂量子','心上秋','清角吹寒','不知','Wanghaotain']:tenure(name,'main-system','manager','2025-11-18',notes='任命见原稿；精确卸任日待补。',sourcepages=[9])
for name in ['Imagedunuage','眼镜豆','微笑小月亮','绩溪soyorin','新溪']:tenure(name,'main-system','manager',label='第一代期间任职，起止待考',sourcepages=[9,10,11,12])
for name in second:
    if name not in ['高尔夫球爱好者','茄肉粥','羲和','汪咩','特异人士','晚安梦梦梦','珺宁'] and not any(t['characterId']==byname[name]['id'] and t['role']=='manager' for t in d['tenures']):
        tenure(name,'shantou-system' if name in ['梦言jacobin','来日方长','圣人帕拉斯','渔歌子','自己互相监督'] else 'main-system','manager',label='第二代期间，具体群聊与起止待核',notes='PDF名单记载，任职范围暂参考旧站备注。',sourcepages=[17,18])
for name in ['四羟小娶','korman233','玉华','纯良小天使']:
    if not any(t['characterId']==byname[name]['id'] for t in d['tenures']):tenure(name,'main-system','manager',label='第三代成员，具体起止待补',sourcepages=[18])
mapping={'election':['g1','g2'],'dachui':['g1','g2','g4'],'regency':['g4','g5','g6'],'station':['g-shantou'],'night-talk':['g-shantou'],'branch':['g-branch'],'retreat':['g6','g1'],'embers':['g1','g8','g-branch','g-backup'],'reclaim':['g8','g-backup','g-branch','g9'],'shantou':['g-shantou'],'appointments':['g9'],'kong-crisis':['g9','g10']}
for e in d['events']:e['groupIds']=mapping.get(e['id'],[])
for s in d['groupStages']:s['eventIds']=[e['id'] for e in d['events'] if s['groupId'] in e['groupIds']]
for p in sorted((ROOT/'images').iterdir()):
    if p.suffix.lower() in ['.jpg','.jpeg','.png','.webp','.gif']:d['media'].append({'id':'media-'+hashlib.sha256(p.name.encode()).hexdigest()[:12],'path':'images/'+p.name,'alt':p.stem,'caption':'','publication':'published'})
d['migration']['notes']=['42个人物、50篇旧文ID和原文字段保留；空白文章归档。','原稿正文按手工确认的边界迁入，原PDF随站提供。']
d['migration']['sourceLists']={k:segments[k]['body'] for k in ['leaders1','managers1','leaders2','gen1-heading','gen2-heading','gen3-heading','volume-heading']}
(ROOT/'sources').mkdir(exist_ok=True);shutil.copyfile(SOURCE,ROOT/'sources/history.pdf')
target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'assets').mkdir(exist_ok=True)
oldhtml=subprocess.check_output(['git','show',f'{BASE}:index.html'],cwd=ROOT).decode('utf-8')
(ROOT/'assets/memorial-legacy.css').write_text(re.search(r'<style>(.*?)</style>',oldhtml,re.S).group(1),encoding='utf-8')
print(json.dumps({k:len(d[k]) for k in ['characters','generations','volumes','periods','events','groupStages','tenures','treatises']},ensure_ascii=False))
print('Mapped lines:',sum(s['lineCount'] for s in coverage),'/',len(lines)-3)

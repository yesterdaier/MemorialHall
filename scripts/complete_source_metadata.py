"""Attach original PDF headings and a readable roster; safe to run repeatedly."""
import json
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'data.json'
data = json.loads(path.read_text(encoding='utf-8'))
with pdfplumber.open(ROOT / 'sources/history.pdf') as pdf:
    pages = [p.extract_text_lines() for p in pdf.pages]
headings = {}
for section in data['migration']['sections']:
    page, line = section['from']
    heading = pages[page-1][line]['text']
    section['sourceHeading'] = heading
    headings[section['key']] = heading
for key in ['events', 'periods']:
    for item in data[key]:
        if item['id'] in headings:
            item['sourceHeading'] = headings[item['id']]
people = {'晚安梦梦梦':'meng','绩溪soyorin':'jixi','新溪':'xinxi','微笑小月亮':'moon',
          '眼镜豆':'yjd','Imagedunuage':'im','陕西大锤哥':'dachui','陈爹':'chendie',
          '水银灯':'ml','王思洛夫':'wslf'}
for person in data['characters']:
    if person['name'] in people:
        person['articles'][0]['sourceHeading'] = headings['bio-'+people[person['name']]]
for treatise in data['treatises']:
    for chapter in treatise['chapters']:
        chapter['sourceHeading'] = headings[chapter['id'].removeprefix('chapter-')]
generation = data['generations'][1]
marker = '<h3>原稿成员名录</h3>'
if marker not in generation['body']:
    generation['body'] += '\n'+marker+'\n<p>主要领导成员：</p>\n'+data['migration']['sourceLists']['leaders2']
generation['sourceRefs'] = [{'sourceId':'source-history','pages':[17,18]}]
data['migration']['notes'] = list(dict.fromkeys(data['migration']['notes']+[
    '原稿各节题名完整保存在 migration.sections.sourceHeading；人物和专题原题附在对应正文来源区。',
    '第二代原始名录在第二代概述全文中保留，包括同一人物在不同原稿类别的重复列名。'
]))
stage = next(s for s in data['groupStages'] if s['id']=='s-huaming')
stage['time'].update(start=None,end=None,label='第二代期间；起止待考',precision='unknown')
stage['notes']='群名见原稿第17页；旧站“花明楼建立”计时字段保留在人物页，不作为本表建群日期依据。'
stage['sourceRefs']=[{'sourceId':'source-history','pages':[17]}]
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Attached',len(headings),'original headings and second-generation roster.')

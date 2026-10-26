export const COLLECTIONS=['generations','volumes','periods','events','characters','groups','groupStages','tenures','treatises','media','sources'];
export const CATEGORY={main:'素槽群聊表',night:'夜群／水电站群聊表',shantou:'山头群聊表',admins:'管理员表'};
export const NAVIGATION=[{route:'chronicle',label:'素槽纪事'},{route:'people',label:'人物列传'},{route:'tables/main',label:'群聊与管理表'},{route:'gazetteers',label:'相关诸志'},{route:'search',label:'搜索'}];
export const h=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const plain=v=>String(v||'').replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ').replace(/&amp;/g,'&').replace(/\s+/g,' ').trim();
export const sort=items=>[...(items||[])].sort((a,b)=>(Number(a.order??a.homeOrder??9999)-Number(b.order??b.homeOrder??9999))||String(a.id).localeCompare(String(b.id)));
export const published=x=>!!x&&x.publication!=='draft'&&!x.archived;
export const find=(d,k,id)=>(d[k]||[]).find(x=>x.id===id);
export const clone=x=>structuredClone(x);
export function chinese(n){if(n<11)return '零一二三四五六七八九十'[n];if(n<20)return '十'+chinese(n%10);if(n<100)return chinese(Math.floor(n/10))+'十'+(n%10?chinese(n%10):'');return String(n);}
export function orderedVolumes(d){const ranks=new Map(sort(d.generations).map((g,i)=>[g.id,i]));return sort(d.volumes).sort((a,b)=>(ranks.get(a.generationId)??999)-(ranks.get(b.generationId)??999));}
export function volumeName(d,v){return '卷'+chinese(orderedVolumes(d).findIndex(x=>x.id===v.id)+1)+' · '+v.title;}
export const timeText=t=>t?.label||(t?.dates?.length?t.dates.join('、'):(t?.start||'时间待考')+(t?.ongoing?' — 今':t?.end?' — '+t.end:''));
export function syncMembership(d,key,id){
    if(key==='characters'){const c=find(d,key,id);for(const g of d.generations)g.characterIds=c.generationIds.includes(g.id)?[...new Set([...(g.characterIds||[]),id])]:(g.characterIds||[]).filter(x=>x!==id);}
    if(key==='generations'){const g=find(d,key,id);for(const c of d.characters)c.generationIds=g.characterIds.includes(c.id)?[...new Set([...(c.generationIds||[]),id])]:(c.generationIds||[]).filter(x=>x!==id);}
}
export function internalTarget(value){
    if(!value.startsWith('#/'))return null;
    try{const [raw,query='']=value.slice(2).replaceAll('&amp;','&').split('?'),p=raw.split('/').map(decodeURIComponent),q=new URLSearchParams(query);
        if(p[0]==='chronicle'&&p[2])return {collection:{generation:'generations',volume:'volumes',period:'periods',event:'events'}[p[1]],id:p[2]};
        if(p[0]==='person')return {collection:'characters',id:p[1],article:p[2]==='article'?p[3]:null};
        if(p[0]==='gazetteers'&&p[1])return {collection:'treatises',id:p[1],chapter:q.get('chapter')};
        if(p[0]==='tables'&&q.has('record'))return {collection:p[1]==='admins'?'tenures':'groupStages',id:q.get('record')};
        if(p[0]==='tables'&&q.has('group'))return {collection:'groups',id:q.get('group')};
        if(p[0]==='tables'&&q.has('person'))return {collection:'characters',id:q.get('person')};
        if(!['chronicle','people','tables','gazetteers','search','about'].includes(p[0]))return {collection:null,id:p[0]};
    }catch{return {collection:null,id:value};}return null;
}
export function contentLinks(x){const links=[];for(const field of ['body','summary','funeralCommittee','preface','conventions'])for(const m of String(x[field]||'').matchAll(/href\s*=\s*["']([^"']+)["']/gi)){const target=internalTarget(m[1]);if(target)links.push(target);}return links;}
export const excerpt=(s,n=100)=>plain(s).slice(0,n)+(plain(s).length>n?'…':'');
export const uid=prefix=>prefix+'-'+crypto.randomUUID().slice(0,12);
export const emptyTime=()=>({label:'',start:null,end:null,precision:'day',dates:[],ongoing:false});
export function safePath(s){return typeof s==='string'&&!s.includes('\\')&&!/(^|\/)\.\.?(\/|$)/.test(s)&&!s.startsWith('/')&&!s.includes(':')&&!/[?#\u0000-\u001f]/.test(s);}
export function imagePath(s){return safePath(s)&&/^images\/.+\.(png|jpe?g|webp|gif)$/i.test(s);}
export function href(s){return /^(#\/|https?:\/\/|mailto:)/i.test(s||'')||safePath(s)?h(s):'#';}
export function sanitize(markup){
    if(!globalThis.DOMPurify)throw new Error('正文清洗组件未加载，请刷新页面。');
    const clean=DOMPurify.sanitize(String(markup||''),{USE_PROFILES:{html:true},FORBID_TAGS:['style','form','input','button','iframe','object','embed'],FORBID_ATTR:['srcset','id','name'],ADD_ATTR:['data-entity']});
    const template=document.createElement('template');template.innerHTML=clean;
    const allowed=['text-align','text-indent','font-weight','font-style','text-decoration','color','background-color','font-size','line-height','margin-bottom','padding','border','border-bottom'];
    for(const el of template.content.querySelectorAll('[style]')){
        const old=el.style.cssText;el.removeAttribute('style');
        const temp=document.createElement('span');temp.style.cssText=old;
        for(const prop of allowed){const v=temp.style.getPropertyValue(prop);if(v&&!/url|expression|var\(/i.test(v))el.style.setProperty(prop,v);}
    }
    for(const el of template.content.querySelectorAll('a')){
        if(!/^(#\/|https?:\/\/|mailto:)/i.test(el.getAttribute('href')||'')&&!safePath(el.getAttribute('href')))el.removeAttribute('href');
        if(el.target==='_blank')el.rel='noopener noreferrer';
    }
    for(const el of template.content.querySelectorAll('img')){const src=el.getAttribute('src')||'';if(!imagePath(src)&&!/^https:\/\//i.test(src))el.removeAttribute('src');el.loading='lazy';}
    return template.innerHTML;
}
export function walk(d,callback){
    for(const k of COLLECTIONS)for(const x of d[k]||[]){callback(x,k,x.id);if(k==='characters')for(const a of x.articles||[])callback(a,'articles',x.id+'/'+a.key);if(k==='treatises')for(const c of x.chapters||[])callback(c,'chapters',x.id+'/'+c.id);}
}
export function validation(d){
    const errors=[],warnings=[];const err=s=>errors.push(s);const warn=s=>warnings.push(s);
    if(!d||d.schemaVersion!==2)return {errors:['仅支持 schemaVersion 2 数据。'],warnings};
    for(const k of COLLECTIONS)if(!Array.isArray(d[k]))err(k+' 必须是数组');
    if(errors.length)return {errors,warnings};
    const maps=Object.fromEntries(COLLECTIONS.map(k=>[k,new Set(d[k].map(x=>x.id))]));
    for(const k of COLLECTIONS){const seen=new Set();for(const x of d[k]){if(!/^[a-zA-Z0-9_-]+$/.test(x.id||''))err(k+' 标识不合法：'+x.id);if(seen.has(x.id))err(k+' 重复标识：'+x.id);seen.add(x.id);}}
    const ref=(k,id,where,optional=false)=>{if(!id&&optional)return;if(!maps[k].has(id))err(where+' 引用不存在：'+k+'/'+id);};
    const refs=(k,ids,where)=>{for(const id of ids||[])ref(k,id,where);};
    const checkContent=(x,at)=>{
        for(const t of contentLinks(x)){if(!maps[t.collection]){err(at+' 站内链接无效：'+t.id);continue;}ref(t.collection,t.id,at);const item=find(d,t.collection,t.id);if(t.article&&!item?.articles?.some(a=>a.key===t.article))err(at+' 文章链接无效：'+t.article);if(t.chapter&&!item?.chapters?.some(c=>c.id===t.chapter))err(at+' 章节链接无效：'+t.chapter);}
        for(const field of ['body','summary','funeralCommittee','preface','conventions'])for(const m of String(x[field]||'').matchAll(/src\s*=\s*["']([^"']+)["']/gi))if(imagePath(m[1])&&!d.media.some(a=>a.path===m[1]))err(at+' 图片未在图库登记：'+m[1]);
    };
    checkContent(d,'站点正文');
    const validDate=s=>/^\d{4}-\d{2}-\d{2}$/.test(s)&&!isNaN(Date.parse(s))&&new Date(s+'T00:00:00Z').toISOString().slice(0,10)===s;
    walk(d,(x,k,id)=>{
        const at=k+'/'+id;
        if(x.time){for(const v of [x.time.start,x.time.end,...(x.time.dates||[])])if(v&&!validDate(v))err(at+' 非法日期：'+v);if(x.time.start&&x.time.end&&x.time.start>x.time.end)err(at+' 结束日期早于开始日期');if(x.time.ongoing&&x.time.end)err(at+' 不能同时设置至今和结束日期');}
        for(const r of x.sourceRefs||[]){ref('sources',r.sourceId,at);if((r.pages||[]).some(p=>!Number.isInteger(p)||p<1||p>(find(d,'sources',r.sourceId)?.pageCount||Infinity)))err(at+' 来源页码无效');}
        if(x.completion&&x.completion!=='complete')warn(at+' 正文'+(x.completion==='pending'?'待补':'未完'));
        for(const note of x.editorialNotes||[])warn(at+'：'+note);
        refs('characters',x.characterIds,at);refs('generations',x.generationIds,at);refs('groups',x.groupIds,at);refs('events',x.eventIds,at);refs('treatises',x.treatiseIds,at);
        checkContent(x,at);
    });
    for(const v of d.volumes)ref('generations',v.generationId,v.id);
    for(const p of d.periods){ref('volumes',p.volumeId,p.id);ref('periods',p.parentId,p.id,true);const seen=new Set([p.id]);let q=p;let depth=0;while(q.parentId){q=find(d,'periods',q.parentId);if(!q)break;if(seen.has(q.id)){err(p.id+' 时期目录循环');break;}seen.add(q.id);depth++;if(q.volumeId!==p.volumeId)err(p.id+' 父子时期必须属于同一卷');}if(depth>1)err(p.id+' 最多支持两层时期');}
    for(const e of d.events){ref('volumes',e.volumeId,e.id);ref('periods',e.periodId,e.id,true);refs('periods',e.relatedPeriodIds,e.id);if(e.periodId&&find(d,'periods',e.periodId)?.volumeId!==e.volumeId)err(e.id+' 所属时期与卷不一致');}
    for(const s of d.groupStages){ref('groups',s.groupId,s.id);if(!['main','night','shantou'].includes(s.category))err(s.id+' 群聊类别无效');}
    for(const t of d.tenures){ref('groups',t.groupId,t.id);ref('characters',t.characterId,t.id);if(!['owner','manager'].includes(t.role))err(t.id+' 职务无效');}
    for(const c of d.characters){
        const keys=new Set();for(const a of c.articles||[]){if(keys.has(a.key)||!/^[a-zA-Z0-9_-]+$/.test(a.key||''))err(c.name+' 文章key重复或无效');keys.add(a.key);}
        if(!keys.has(c.defaultArticleKey))err(c.name+' 默认文章不存在');
        if(c.publication!=='draft'&&!published((c.articles||[]).find(a=>a.key===c.defaultArticleKey)))err(c.name+' 默认文章必须已发布且未归档');
        for(const n of [...(c.banners||[]),...(c.sidebarNav||[])])if(!keys.has(n.articleKey))err(c.name+' 文章导航失效：'+n.articleKey);
        if(c.imagePath&&(!imagePath(c.imagePath)||!d.media.some(m=>m.path===c.imagePath)))err(c.name+' 头像路径无效或未登记');
        if(c.deathDate&&!validDate(c.deathDate))err(c.name+' 计时日期无效');
    }
    const paths=new Set();for(const m of d.media){if(!imagePath(m.path))err('图片路径不合法：'+m.path);if(paths.has(m.path))err('图片路径重复：'+m.path);paths.add(m.path);}
    for(const s of d.sources)if(s.path&&!safePath(s.path))err('史料路径不合法：'+s.path);
    for(const g of d.generations)for(const c of d.characters)if((g.characterIds||[]).includes(c.id)!==(c.generationIds||[]).includes(g.id))err('领导集体成员关联不同步：'+g.id+'/'+c.id);
    if(d.navigation){const routes=NAVIGATION.map(n=>n.route);if(!Array.isArray(d.navigation)||d.navigation.length!==routes.length||new Set(d.navigation.map(n=>n.route)).size!==routes.length||d.navigation.some(n=>!routes.includes(n.route)||!n.label))err('导航须包含纪、传、表、志、搜索五个入口且不能重复');}
    for(const t of d.treatises){const ids=new Set();for(const c of t.chapters||[]){if(!c.id||ids.has(c.id))err(t.title+' 章节ID重复');ids.add(c.id);}}
    return {errors:[...new Set(errors)],warnings:[...new Set(warnings)]};
}
export function publicData(d){
    const out=clone(d);for(const k of COLLECTIONS)out[k]=out[k].filter(x=>x.publication!=='draft');
    for(const c of out.characters){c.articles=c.articles.filter(a=>a.publication!=='draft');const keys=new Set(c.articles.map(a=>a.key));c.banners=(c.banners||[]).filter(x=>keys.has(x.articleKey));c.sidebarNav=(c.sidebarNav||[]).filter(x=>keys.has(x.articleKey));}
    for(const t of out.treatises)t.chapters=(t.chapters||[]).filter(c=>c.publication!=='draft');
    return out;
}
export function inbound(d,collection,id){
    const found=[];const fields={generations:['generationId','generationIds'],volumes:['volumeId'],periods:['parentId','periodId','relatedPeriodIds'],characters:['characterId','characterIds'],groups:['groupId','groupIds'],events:['eventIds'],treatises:['treatiseIds'],sources:['sourceId']}[collection]||[];
    walk(d,(x,k,at)=>{if(k===collection&&x.id===id)return;for(const f of fields)if(x[f]===id||Array.isArray(x[f])&&x[f].includes(id))found.push(k+'/'+at);if(collection==='sources'&&(x.sourceRefs||[]).some(r=>r.sourceId===id))found.push(k+'/'+at);const text=JSON.stringify(x);if(collection==='media'){const path=find(d,'media',id)?.path;if(path&&k!=='media'&&text.includes(path))found.push(k+'/'+at);}if(collection==='characters'&&text.includes('#/person/'+id))found.push(k+'/'+at);if(collection==='events'&&text.includes('#/chronicle/event/'+id))found.push(k+'/'+at);});
    const inspectLinks=(x,at)=>{if(contentLinks(x).some(t=>t.collection===collection&&t.id===id))found.push(at);};
    walk(d,(x,k,at)=>inspectLinks(x,k+'/'+at));inspectLinks(d,'站点正文');
    if(collection==='media'){const path=find(d,'media',id)?.path;if(path&&[d.preface,d.conventions].some(x=>x?.includes(path)))found.push('站点正文');}
    if(collection==='volumes')for(const p of d.periods.filter(x=>x.volumeId===id))found.push('periods/'+p.id);
    return [...new Set(found)];
}
export function searchIndex(d){
    const rows=[];const add=(kind,title,body,url,aliases=[])=>rows.push({kind,title,text:plain(body),url,aliases});
    for(const g of d.generations.filter(published))add('纪',g.title,g.body,'#/chronicle/generation/'+g.id);
    for(const v of d.volumes.filter(published))add('纪',volumeName(d,v),v.body,'#/chronicle/volume/'+v.id);
    for(const e of d.events.filter(published))add('纪',e.title,e.body,'#/chronicle/event/'+e.id);
    for(const p of d.periods.filter(published))add('纪',p.title,p.body,'#/chronicle/period/'+p.id);
    for(const c of d.characters.filter(published)){add('传',c.name,c.articles.find(a=>a.key===c.defaultArticleKey)?.body,'#/person/'+c.id,c.aliases);for(const a of c.articles.filter(published))if(a.key!==c.defaultArticleKey)add('传',a.title,a.body,'#/person/'+c.id+'/article/'+a.key,[c.name]);}
    for(const s of d.groupStages.filter(published)){const g=find(d,'groups',s.groupId);add('表',s.title,s.notes+' '+timeText(s.time),'#/tables/'+s.category+'?record='+s.id,g?.aliases||[]);}
    for(const t of d.tenures.filter(published)){const c=find(d,'characters',t.characterId);add('表',(c?.name||'')+' · '+(t.role==='owner'?'群主':'管理员'),(find(d,'groups',t.groupId)?.name||'')+' '+timeText(t.time),'#/tables/admins?record='+t.id,c?.aliases||[]);}
    for(const t of d.treatises.filter(published)){add('志',t.title,t.body,'#/gazetteers/'+t.id);for(const c of (t.chapters||[]).filter(published))add('志',c.title,c.body,'#/gazetteers/'+t.id+'?chapter='+c.id);}
    return rows;
}
export function search(d,q){q=q.trim().toLowerCase();if(!q)return [];return searchIndex(d).map(r=>({...r,score:(r.title.toLowerCase()===q?100:r.title.toLowerCase().includes(q)?50:0)+(r.aliases.some(a=>a.toLowerCase()===q)?90:r.aliases.some(a=>a.toLowerCase().includes(q))?40:0)+(r.text.toLowerCase().includes(q)?10:0)})).filter(r=>r.score).sort((a,b)=>b.score-a.score);}
export function changeSummary(base,next){return COLLECTIONS.map(k=>{const old=new Map((base[k]||[]).map(x=>[x.id,x]));const add=next[k].filter(x=>!old.has(x.id)).length;const changed=next[k].filter(x=>old.has(x.id)&&JSON.stringify(old.get(x.id))!==JSON.stringify(x)).length;const remove=(base[k]||[]).filter(x=>!next[k].some(y=>y.id===x.id)).length;return {collection:k,added:add,changed,removed:remove};}).filter(x=>x.added||x.changed||x.removed);}

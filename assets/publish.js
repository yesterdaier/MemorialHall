import {publicData,validation,imagePath} from './core.js';
export function githubClient(cfg,fetcher=fetch){
    if(!/^[\w.-]+$/.test(cfg.owner||'')||!/^[\w.-]+$/.test(cfg.repo||'')||!cfg.branch||!cfg.token)throw new Error('请填写仓库、分支与访问令牌。');
    const root='https://api.github.com/repos/'+encodeURIComponent(cfg.owner)+'/'+encodeURIComponent(cfg.repo);
    return async(path,method='GET',body)=>{const res=await fetcher(root+path,{method,headers:{Authorization:'Bearer '+cfg.token,Accept:'application/vnd.github+json','Content-Type':'application/json','X-GitHub-Api-Version':'2022-11-28'},...(body?{body:JSON.stringify(body)}:{})});const data=await res.json().catch(()=>({}));if(!res.ok)throw new Error('GitHub '+res.status+'：'+(data.message||res.statusText));return data;};
}
export const branchPath=b=>b.split('/').map(encodeURIComponent).join('/');
export async function remoteSnapshot(cfg,fetcher=fetch){
    const api=githubClient(cfg,fetcher),ref=await api('/git/ref/heads/'+branchPath(cfg.branch));
    const file=await api('/contents/data.json?ref='+ref.object.sha);
    if(file.encoding!=='base64'||!file.content)throw new Error('远端data.json无法读取，请从GitHub检查文件大小或格式。');
    const bytes=Uint8Array.from(atob(file.content.replace(/\s/g,'')),c=>c.charCodeAt(0));
    return {head:ref.object.sha,data:JSON.parse(new TextDecoder().decode(bytes)),fileSha:file.sha};
}
export async function publishWorkspace(cfg,workspace,message,onProgress=()=>{},fetcher=fetch){
    if(!workspace.baseHead)throw new Error('请先连接远端并确认编辑基线。');
    const data=publicData(workspace.data),check=validation(data);if(check.errors.length)throw new Error(check.errors.join('\n'));
    const api=githubClient(cfg,fetcher);onProgress('检查远端分支…');
    const ref=await api('/git/ref/heads/'+branchPath(cfg.branch));
    if(ref.object.sha!==workspace.baseHead)throw new Error('远端已有新提交。发布已停止，本地草稿保留；请重新加载远端并对比。');
    const commit=await api('/git/commits/'+workspace.baseHead);const tree=[];
    for(const [path,file] of Object.entries(workspace.pendingMedia||{})){
        if(!imagePath(path))throw new Error('图片路径不合法：'+path);
        if(!data.media.some(m=>m.path===path))continue;
        const m=/^data:image\/(?:png|jpeg|webp|gif);base64,([A-Za-z0-9+/=]+)$/.exec(file.dataURL);if(!m)throw new Error('图片编码不合法：'+path);
        onProgress('上传图片：'+path);const blob=await api('/git/blobs','POST',{encoding:'base64',content:m[1]});tree.push({path,mode:'100644',type:'blob',sha:blob.sha});
    }
    onProgress('创建内容版本…');const blob=await api('/git/blobs','POST',{encoding:'utf-8',content:JSON.stringify(data,null,2)+'\n'});tree.push({path:'data.json',mode:'100644',type:'blob',sha:blob.sha});
    const newTree=await api('/git/trees','POST',{base_tree:commit.tree.sha,tree});
    const newCommit=await api('/git/commits','POST',{message:message||'更新素槽群史',tree:newTree.sha,parents:[workspace.baseHead]});
    onProgress('更新分支（禁止强制覆盖）…');await api('/git/refs/heads/'+branchPath(cfg.branch),'PATCH',{sha:newCommit.sha,force:false});
    onProgress('已提交到 GitHub。部署尚待确认。');return {head:newCommit.sha,data,url:newCommit.html_url};
}
export async function deploymentStatus(cfg,sha,fetcher=fetch){
    const api=githubClient(cfg,fetcher),result=await api('/actions/runs?head_sha='+encodeURIComponent(sha)+'&per_page=30');
    const runs=(result.workflow_runs||[]).filter(r=>r.head_sha===sha&&/deploy|pages|部署/i.test(r.name||r.path||''));
    if(!runs.length)return {state:'waiting',message:'尚未发现此提交的部署任务。非部署分支不会更新正式网站。'};
    if(runs.some(r=>r.conclusion&&r.conclusion!=='success'))return {state:'failed',message:'部署失败，请查看 GitHub Actions。',url:runs.find(r=>r.conclusion&&r.conclusion!=='success').html_url};
    if(runs.some(r=>r.status!=='completed'))return {state:'running',message:'已提交，工作流正在运行。',url:runs[0].html_url};
    const jobs=(await Promise.all(runs.map(r=>api('/actions/runs/'+r.id+'/jobs?per_page=100')))).flatMap(r=>r.jobs||[]);
    const deployJobs=jobs.filter(j=>/^(deploy|deployment|deploy[ _-].*|部署.*)$/i.test(j.name||''));
    if(deployJobs.some(j=>j.conclusion==='success'))return {state:'success',message:'部署任务成功，网站已部署。',url:runs[0].html_url};
    if(deployJobs.some(j=>j.status!=='completed'))return {state:'running',message:'部署任务正在运行。',url:runs[0].html_url};
    return {state:'waiting',message:'校验已完成，但此提交没有成功执行网站部署。测试分支只构建预览工件；请检查部署分支与任务。',url:runs[0].html_url};
}

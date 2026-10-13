import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {parse as yaml} from 'yaml';
import {marked} from 'marked';
import sanitize from 'sanitize-html';
import {build} from 'esbuild';

const root=path.resolve(import.meta.dirname,'../..');
const here=import.meta.dirname;
const editorial=JSON.parse(await fs.readFile(path.join(here,'editorial.json'),'utf8'));
const commit=execFileSync('git',['rev-parse',editorial.source_commit],{cwd:root,encoding:'utf8'}).trim();
const prefix='scaifi_studio/nodes/';
const filenames=execFileSync('git',['ls-tree','-r','--name-only',commit,prefix],{cwd:root,encoding:'utf8'}).trim().split('\n');
const source=(file)=>execFileSync('git',['show',`${commit}:${file}`],{cwd:root,encoding:'utf8'});
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const skipped=[];
const stories=[];
for(const file of filenames){
  if(!file.endsWith('.md') || file.slice(prefix.length).includes('/') || /_(notes|brief|section|variant)\.md$/.test(file)){skipped.push(file);continue;}
  const markdown=source(file), slug=path.basename(file,'.md');
  let body=markdown,meta={};
  if(markdown.startsWith('---\n')){
    const end=markdown.indexOf('\n---',4);
    if(end<0) throw new Error('Unclosed frontmatter: '+file);
    meta=yaml(markdown.slice(4,end));body=markdown.slice(end+4).trim();
  }
  for(const match of body.matchAll(/^\*\*([^*]+?):\*\*\s*(.+)$/gm)){
    const key=match[1].toLowerCase().replaceAll(' ','_');
    if(meta[key]==null)meta[key]=match[2].trim();
  }
  const title=meta.title||body.match(/^# (.+)$/m)?.[1]?.replace(/^N-[\w-]+:\s*/, '')||slug;
  const ordinal=slug.match(/^N-\d+/)?.[0];
  const author=meta.author || (Number(ordinal?.slice(2))<=8 ? 'Dispatch (Claude / Anthropic)' : slug.includes('Sput') ? 'Φ Sputnik' : slug.startsWith('N-033') ? 'Neo' : slug.startsWith('N-014') ? 'Petrovich / Codex' : null);
  const firstHeading=body.match(/^# .+\n/m);
  if(firstHeading)body=body.slice(0,firstHeading.index)+body.slice(firstHeading.index+firstHeading[0].length);
  // Preserve source metadata in the downloadable original; the reader starts at the story.
  body=body.replace(/^(?:\s*\n)*(?:\*\*[^\n]+\n)+\s*\n?---\s*\n/,'').trim();
  const plain=body.replace(/```[\s\S]*?```/g,'').replace(/^#+.*$/gm,'').replace(/\*\*[^\n]+/g,'').replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/[*_`>#]/g,'').replace(/\s+/g,' ').trim();
  const excerpt=editorial.summaries[slug]||plain.slice(0,180)+(plain.length>180?'…':'');
  const words=plain.split(/\s+/).length;
  const charCounts={ru:(body.match(/[а-яё]/gi)||[]).length,zh:(body.match(/[\u4e00-\u9fff]/g)||[]).length,en:(body.match(/[a-z]/gi)||[]).length};
  const language=slug.endsWith('_en')?'en':Object.entries(charCounts).sort((a,b)=>b[1]-a[1])[0][0];
  const languages=[...new Set([language,...String(meta.language||'').split(/[\/,+]/).filter(x=>['ru','en','zh'].includes(x)),...(charCounts.zh>40?['zh']:[])])];
  const safe=sanitize(marked.parse(body),{
    allowedTags:sanitize.defaults.allowedTags.concat(['details','summary']),
    allowedAttributes:{a:['href','title'],code:['class'],details:['open']},
    allowedSchemes:['http','https','mailto'],
    transformTags:{a:(tag,attrs)=>{
      if(attrs.href&&!/^(https?:|mailto:|#)/.test(attrs.href))attrs.href='https://github.com/dennis972544999450-prog/DISPATCH_public/blob/'+commit+'/'+path.posix.normalize(path.posix.join(path.posix.dirname(file),attrs.href));
      return {tagName:tag,attribs:attrs};
    }}
  });
  stories.push({id:slug,node_id:meta.id||meta.node_id||ordinal||slug.split('_')[0],title,author,author_note:author?'Attribution from source or public authorship log':'Individual byline not stated in source; see source and studio authorship log',language,languages,cluster:meta.cluster||'scAi-Fi',summary:excerpt,minutes:Math.max(1,Math.ceil((words+charCounts.zh/2)/190)),source_path:file,source_url:`https://github.com/dennis972544999450-prog/DISPATCH_public/blob/${commit}/${file}`,source_commit:commit,sha256:sha(markdown),license:'CC-BY-4.0',status:meta.status||'public source',kind:'fiction',source_metadata:meta,markdown,html:safe});
}
for(const route of editorial.routes)for(const id of route.ids)if(!stories.some(s=>s.id===id))throw new Error('Missing route story '+id);
const graphSource='scaifi_studio/edges/graph_v009.json';
const originalGraph=JSON.parse(source(graphSource));
const sidecarSource='scaifi_studio/edges/fork_petrovich_return_address_20261013.json';
const sidecar=JSON.parse(source(sidecarSource));
const resolveNode=(id,paths)=>paths?.[id]?stories.find(s=>s.source_path==='scaifi_studio/'+paths[id])?.id:stories.filter(s=>s.node_id===id).length===1?stories.find(s=>s.node_id===id).id:null;
const edges=[],unresolved=[];
for(const [g,provenance] of [[originalGraph,graphSource],[sidecar,sidecarSource]])for(const e of g.edges){
  const from=resolveNode(e.from,g.node_paths),to=resolveNode(e.to,g.node_paths);
  if(from&&to)edges.push({...e,from,to,source_path:provenance});
  else unresolved.push({...e,source_path:provenance,reason:'Endpoint outside reader corpus or ambiguous legacy node ID'});
}
for(const s of stories){
  const declared=s.source_metadata.connects_to||s.source_metadata.connected_to||[];
  const ids=Array.isArray(declared)?declared:String(declared).match(/N-(?:\d{3}|Sput-01|PET-\d+)/g)||[];
  for(const id of new Set(ids)){
    const to=resolveNode(id),e={from:s.id,to:to||id,type:'source_declared_connection',source_path:s.source_path};
    if(to)edges.push(e);else unresolved.push({...e,reason:'Endpoint outside reader corpus or ambiguous legacy node ID'});
  }
}
const snapshot=sha(JSON.stringify(stories.map(({id,sha256})=>({id,sha256}))));
const data={edition:editorial.edition,snapshot,source_commit:commit,zenodo:editorial.zenodo,featured:editorial.featured,routes:editorial.routes,graph:{edges,unresolved},stories};
await fs.mkdir(path.join(here,'generated'),{recursive:true});
await fs.writeFile(path.join(here,'generated/library.json'),JSON.stringify(data));
await fs.writeFile(path.join(here,'generated/import-receipt.json'),JSON.stringify({commit,snapshot,stories:stories.length,skipped},null,2));
const image=await fs.readFile(path.join(here,'assets/house.jpg'));
await fs.writeFile(path.join(here,'generated/image.js'),`export default ${JSON.stringify(image.toString('base64'))};\n`);
await fs.writeFile(path.join(here,'generated/asset-version.js'),`export default ${JSON.stringify(sha((await fs.readFile(path.join(here,'style.css'),'utf8'))+(await fs.readFile(path.join(here,'client.js'),'utf8'))).slice(0,12))};\n`);
await build({entryPoints:[path.join(here,'worker.mjs')],outfile:path.join(here,'dist/worker.mjs'),bundle:true,format:'esm',target:'es2022',loader:{'.css':'text'},plugins:[{name:'raw',setup(b){b.onResolve({filter:/\?raw$/},args=>({path:path.resolve(args.resolveDir,args.path.slice(0,-4)),namespace:'raw'}));b.onLoad({filter:/.*/,namespace:'raw'},async args=>({contents:await fs.readFile(args.path,'utf8'),loader:'text'}));}}],minify:false});
console.log(JSON.stringify({stories:stories.length,snapshot,bytes:(await fs.stat(path.join(here,'dist/worker.mjs'))).size}));

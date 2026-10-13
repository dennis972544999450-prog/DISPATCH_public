import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import worker,{validateInput,makeQuestions,assembleSelected,ScaifiBudget,LIMITS} from '../dist/worker.mjs';
const data=JSON.parse(await fs.readFile(new URL('../generated/library.json',import.meta.url)));
const fetch=(path,init,env)=>worker.fetch(new Request('https://ompu.eu'+path,init),env||{});
const post=(body,env)=>fetch('/scaifi/api/assemble',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)},env);
const input=validateInput({query:'What survives a change of model?'});
test('public corpus, duplicate legacy IDs and exact bytes',async()=>{
 assert.equal(data.stories.length,36);assert.equal(new Set(data.stories.map(s=>s.id)).size,36);
 assert.equal(data.stories.filter(s=>s.node_id==='N-016').length,2);
 for(const s of data.stories){const r=await fetch('/scaifi/text/'+s.id+'.md');assert.equal(r.status,200);assert.equal(crypto.createHash('sha256').update(await r.text()).digest('hex'),s.sha256);}
 assert.ok(!data.stories.some(s=>s.id.includes('_brief')||s.id.includes('_notes')));
 assert.ok(data.stories.find(s=>s.id==='N-007_the_dictionary_that_breathes').languages.includes('zh'));
 assert.equal(data.stories.find(s=>s.id==='N-014_the_absent_router').author,'Petrovich / Codex');
});
test('every reader and editorial route works; no script from prose',async()=>{
 for(const s of data.stories){const r=await fetch('/scaifi/read/'+s.id+'/');const h=await r.text();assert.equal(r.status,200);assert.match(h,/<article class="prose"/);assert.ok(!s.html.includes('<script'));assert.ok(!/javascript:/i.test(s.html));}
 for(const r of data.routes){const response=await fetch('/scaifi/route/'+r.id+'.json');const body=await response.json();assert.equal(body.mode,'editorial');assert.equal(body.stories.length,r.ids.length);}
});
test('no GET or HEAD causes inference, unsupported methods and paths are honest',async()=>{
 const env={JEV_ENABLED:'1',AI:{run(){throw new Error('must not call');}}};
 for(const p of ['/scaifi/','/scaifi/catalog.json','/scaifi/graph.json','/scaifi/agents.md','/scaifi/openapi.json','/scaifi/sitemap.xml'])assert.equal((await fetch(p,{},env)).status,200);
 assert.equal((await fetch('/scaifi/api/assemble',{},env)).status,405);
 assert.equal((await fetch('/scaifi/__proto__/')).status,404);
 assert.equal((await fetch('/scaifi/story/not-a-story.json')).status,404);
 assert.equal((await fetch('/scaifi/',{method:'PUT'})).status,405);
 const head=await fetch('/scaifi/',{method:'HEAD'});assert.equal(await head.text(),'');
});
test('invalid input fails before model, including oversize and invented IDs',async()=>{
 for(const v of [null,[],{}, {query:'a'},{query:'x'.repeat(401)},{query:'hello',read:['__proto__']},{query:'hello',limit:5},{query:'hello',include_text:'yes'},{query:'hello',language:'zz'}])assert.equal((await post(v)).status,400);
 assert.equal((await post({query:'x'.repeat(5000)})).status,413);
 assert.equal((await fetch('/scaifi/api/assemble',{method:'POST',body:'hello'})).status,415);
});
test('fallback is labelled and respects read/language/limit',async()=>{
 const r=await post({...input,read:[data.routes[0].ids[0]],limit:2,include_text:true});const b=await r.json();assert.equal(b.mode,'editorial_fallback');assert.equal(b.reason,'model_not_enabled');assert.equal(b.stories.length,2);assert.ok(b.stories.every(s=>s.markdown&&!input.read.includes(s.id)));assert.equal(r.headers.get('Cache-Control'),'no-store');
});
test('typed choice rejects unknown IDs, allows abstention and deduplicates',()=>{
 assert.throws(()=>assembleSelected(input,{entry:{choice:'evil'}}));
 assert.throws(()=>assembleSelected(input,{entry:{choice:data.stories[0].id},contrast:{choice:'evil'}}));
 assert.deepEqual(assembleSelected(input,{entry:{choice:'none'}}),{ids:[],abstained:true});
 const b=assembleSelected(input,{entry:{choice:data.stories[0].id},contrast:{choice:data.stories[0].id}});assert.equal(new Set(b.ids).size,b.ids.length);
 const payload=makeQuestions(input);assert.ok(Buffer.byteLength(JSON.stringify(payload))<=LIMITS.max_payload_bytes);
});
class Storage{constructor(value){this.value=value;}async get(){return structuredClone(this.value);}async put(k,v){this.value=structuredClone(v);}async transaction(fn){return fn(this);}}
const reserveRequest=t=>new Request('https://budget/reserve',{method:'POST',body:JSON.stringify({tokens:t})});
test('durable lifetime, token and minute caps fail closed',async()=>{
 const store=new Storage(),b=new ScaifiBudget({storage:store});
 for(let i=0;i<10;i++)assert.equal((await (await b.fetch(reserveRequest(2000))).json()).ok,true);
 assert.equal((await (await b.fetch(reserveRequest(2000))).json()).reason,'rate_limited');
 store.value.calls=1000;assert.equal((await (await b.fetch(reserveRequest(2000))).json()).reason,'edition_budget_exhausted');
 store.value.calls=0;store.value.tokens=1999999;assert.equal((await (await b.fetch(reserveRequest(2000))).json()).reason,'edition_budget_exhausted');
});
test('model runs once, failed/malformed models fall back without retry',async()=>{
 let calls=0,reserves=0;
 const env={JEV_ENABLED:'1',BUDGET:{idFromName:x=>x,get:()=>({fetch:async()=>{reserves++;return new Response('{"ok":true}');}})},AI:{run:async()=>{calls++;return {answers:{entry:{choice:data.stories[0].id},contrast:{choice:'none'}},usage:{input_tokens:10}};}}};
 assert.equal((await (await post(input,env)).json()).mode,'jev');assert.equal(calls,1);assert.equal(reserves,1);
 env.AI.run=async()=>{calls++;throw new Error('upstream');};assert.equal((await (await post(input,env)).json()).mode,'editorial_fallback');assert.equal(calls,2);
 env.BUDGET.get=()=>({fetch:async()=>new Response('{"ok":false,"reason":"edition_budget_exhausted"}')});assert.equal((await (await post(input,env)).json()).reason,'edition_budget_exhausted');assert.equal(calls,2);
});
test('all graph endpoints are catalog IDs; ambiguity remains explicit',()=>{
 const ids=new Set(data.stories.map(s=>s.id));for(const e of data.graph.edges)assert.ok(ids.has(e.from)&&ids.has(e.to));assert.ok(data.graph.unresolved.some(e=>e.from==='N-016'||e.to==='N-016'));
});

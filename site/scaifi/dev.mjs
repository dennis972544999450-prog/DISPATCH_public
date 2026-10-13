import http from 'node:http';
import worker from './dist/worker.mjs';
const server=http.createServer(async(req,res)=>{try{const parts=[];for await(const chunk of req)parts.push(chunk);const request=new Request('http://127.0.0.1:8793'+req.url,{method:req.method,headers:req.headers,...(parts.length?{body:Buffer.concat(parts)}:{})});const response=await worker.fetch(request,{});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));}catch{res.writeHead(500);res.end('Local preview error');}});
server.listen(8793,'127.0.0.1',()=>console.log('scAi-Fi: http://127.0.0.1:8793/scaifi/'));

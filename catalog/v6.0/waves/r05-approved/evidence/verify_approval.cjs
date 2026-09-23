const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const root='/workspace/scratch/c88c9f6ffc57';
const before=fs.readFileSync(root+'/recovered/r05/GuitarFakeBook_V6.0_DESKTOP_REVIEW_R05/index.html','utf8');
const out=root+'/output/GuitarFakeBook_V6.0_APPROVED_R06';
const after=fs.readFileSync(out+'/index.html','utf8');
const scripts=s=>[...s.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);
const a=scripts(before),b=scripts(after);b.forEach((s,i)=>new vm.Script(s,{filename:'script-'+i+'.js'}));
for(const i of [2,3,4,5])assert.strictEqual(a[i],b[i]);
assert.strictEqual(a[6].replaceAll('desktop-review.r05','approved.r06'),b[6]);
const ctx={window:null,setTimeout,clearTimeout};ctx.window=ctx;vm.createContext(ctx);
for(const i of [0,1,2,3,4])vm.runInContext(b[i],ctx);
const decisionContext={module:{exports:{}}};vm.createContext(decisionContext);vm.runInContext(b[7],decisionContext);
const core=decisionContext.module.exports.decisionCore(ctx.GFB_REVIEW_DATA);
const input=JSON.parse(fs.readFileSync(out+'/OWNER_DECISIONS_R06_NORMALIZED.json'));
assert.strictEqual(core.validate(input).decisions.filter(s=>s.status==='keep').length,317);
const oldData=JSON.parse(fs.readFileSync(root+'/recovered/r05/GuitarFakeBook_V6.0_DESKTOP_REVIEW_R05/review-dataset.json'));
const oldCore=decisionContext.module.exports.decisionCore(oldData);
assert.strictEqual(oldCore.validate(JSON.parse(fs.readFileSync(out+'/OWNER_DECISIONS_R05_ORIGINAL.json'))).decisions.length,317);
const cat=ctx.GFBCatalog.createCatalog({index:ctx.GFB_CATALOG_DATA.index,embedded:ctx.GFB_CATALOG_DATA.embedded,fetcher:()=>{throw Error('unexpected network request')}});
(async()=>{
let loaded=0;
for(const expected of ctx.GFB_CATALOG_DATA.embedded){const s=await cat.loadSong(expected.id);assert.strictEqual(s.title,expected.title);assert.strictEqual(s.artist,expected.artist);assert.strictEqual(s.content,expected.content);loaded++;}
const result={scriptSyntaxChecks:b.length,unchangedCoreModules:4,applicationCodeUnchangedExceptIsolatedStorageKey:true,offlineLoaderSongs:loaded,normalizedKeepDecisions:317,originalDatasetKeepDecisions:317,networkRequests:0,scope:'Actual existing catalog loader and decision validators in Node VM; not browser visual certification'};
fs.writeFileSync(out+'/RUNTIME_VERIFICATION_R06.json',JSON.stringify(result,null,2)+'\n');
fs.writeFileSync(out+'/catalog/v6.0/waves/r05-approved/RUNTIME_VERIFICATION_R06.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exit(1)});

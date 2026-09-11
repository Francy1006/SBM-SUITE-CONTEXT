import assert from 'node:assert/strict';import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {spawn} from 'node:child_process';import {pathToFileURL,fileURLToPath} from 'node:url';
export const gates=['GEN-ATOMIC-01'];
export const gateCases={'GEN-ATOMIC-01':'two real concurrent processes use the same execution_id and produce exactly one SUCCESS plus one SCAFFOLD_EXISTS without mixed output'};
function child(script,env){return new Promise(resolve=>{const p=spawn(process.execPath,['--input-type=module','-e',script],{env:{...process.env,...env},stdio:['ignore','pipe','pipe']});let out='',err='';p.stdout.on('data',d=>out+=d);p.stderr.on('data',d=>err+=d);p.on('close',code=>resolve({code,out,err}));});}
export async function run(){const base=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-concurrent-'));const app=pathToFileURL(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../generators/app/index.js')).href;const script=`import fs from 'node:fs';process.env.SBM_GENERATOR_QA='1';const m=await import(${JSON.stringify(app)});try{m.atomicCommitScaffold(${JSON.stringify(base)},'same-id',t=>{fs.writeFileSync(t+'/winner','complete');Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,250);});process.exit(0);}catch(e){if(e.code==='SCAFFOLD_EXISTS')process.exit(3);console.error(e);process.exit(4);}`;const [a,b]=await Promise.all([child(script,{SBM_GENERATOR_QA:'1'}),child(script,{SBM_GENERATOR_QA:'1'})]);assert.deepEqual([a.code,b.code].sort((x,y)=>x-y),[0,3]);const final=path.join(base,'build/scaffolds/same-id');assert.equal(fs.readFileSync(path.join(final,'winner'),'utf8'),'complete');const names=fs.readdirSync(path.join(base,'build/scaffolds'));assert.equal(names.filter(x=>x.startsWith('.lock-same-id')||x.startsWith('.tmp-same-id-')).length,0);}

/* SBM_CHECKLIST_269_LOCK_OWNERSHIP_BARRIER */
{
  const assert=await import('node:assert/strict');
  const fs=await import('node:fs');
  const os=await import('node:os');
  const path=await import('node:path');
  const crypto=await import('node:crypto');
  const child=await import('node:child_process');
  const url=await import('node:url');
  const {atomicCommitScaffold}=await import('../../generators/app/index.js');

  const root=fs.mkdtempSync(path.join(os.tmpdir(),'sbm-lock-owner-'));
  const base=path.join(root,'base');
  const control=path.join(root,'control');

  fs.mkdirSync(base,{recursive:true});
  fs.mkdirSync(control,{recursive:true});

  const id='atomic-shared-id';
  const ready=path.join(control,'winner-ready');
  const release=path.join(control,'winner-release');
  const childFile=path.join(control,'atomic-child.mjs');
  const coreUrl=new URL('../../generators/app/index.js',import.meta.url).href;

  fs.writeFileSync(childFile,`
import fs from 'node:fs';
import path from 'node:path';
const {atomicCommitScaffold}=await import(${JSON.stringify(coreUrl)});
const [role,base,id,ready,release]=process.argv.slice(2);
const sleeper=new Int32Array(new SharedArrayBuffer(4));

try{
  atomicCommitScaffold(base,id,(tmp)=>{
    fs.mkdirSync(path.join(tmp,'.sbm'),{recursive:true});
    fs.writeFileSync(path.join(tmp,'AGENT_PROPOSAL.yaml'),role+'-proposal\\n');
    fs.writeFileSync(path.join(tmp,'.sbm','scaffold.json'),JSON.stringify({role})+'\\n');

    if(role==='winner'){
      fs.writeFileSync(ready,'READY\\n');
      const deadline=Date.now()+10000;
      while(!fs.existsSync(release)){
        if(Date.now()>deadline) throw new Error('WINNER_RELEASE_TIMEOUT');
        Atomics.wait(sleeper,0,0,25);
      }
    }
  });

  console.log('SUCCESS');
  process.exit(0);
}catch(error){
  console.log('ERROR:'+String(error?.code??error?.message));
  if(error?.code==='SCAFFOLD_EXISTS') process.exit(23);
  console.error(error);
  process.exit(24);
}
`);

  const winner=child.spawn(
    process.execPath,
    [childFile,'winner',base,id,ready,release],
    {stdio:['ignore','pipe','pipe']}
  );

  const sleeper=new Int32Array(new SharedArrayBuffer(4));
  const deadline=Date.now()+10000;

  while(!fs.existsSync(ready)){
    if(Date.now()>deadline) throw new Error('WINNER_READY_TIMEOUT');
    Atomics.wait(sleeper,0,0,25);
  }

  const lockPath=path.join(base,'build','scaffolds',`.lock-${id}`);
  assert.equal(fs.existsSync(lockPath),true);

  const loser=child.spawnSync(
    process.execPath,
    [childFile,'loser',base,id,ready,release],
    {encoding:'utf8'}
  );

  assert.equal(loser.status,23);
  assert.match(loser.stdout,/ERROR:SCAFFOLD_EXISTS/);

  assert.equal(
    fs.existsSync(lockPath),
    true,
    'loser must not remove winner lock'
  );

  fs.writeFileSync(release,'RELEASE\n');

  const winnerResult=await new Promise((resolve,reject)=>{
    const out=[];
    const err=[];
    winner.stdout.on('data',d=>out.push(d));
    winner.stderr.on('data',d=>err.push(d));
    winner.on('error',reject);
    winner.on('close',(code)=>resolve({
      code,
      stdout:Buffer.concat(out).toString('utf8'),
      stderr:Buffer.concat(err).toString('utf8')
    }));
  });

  assert.equal(winnerResult.code,0);
  assert.match(winnerResult.stdout,/SUCCESS/);

  const finalPath=path.join(base,'build','scaffolds',id);
  assert.equal(fs.existsSync(finalPath),true);

  const proposal=fs.readFileSync(path.join(finalPath,'AGENT_PROPOSAL.yaml'),'utf8');
  const metadata=JSON.parse(
    fs.readFileSync(path.join(finalPath,'.sbm','scaffold.json'),'utf8')
  );

  assert.equal(proposal,'winner-proposal\n');
  assert.equal(metadata.role,'winner');

  const residual=fs.readdirSync(path.join(base,'build','scaffolds'));
  assert.equal(residual.some(n=>n===`.lock-${id}`),false);
  assert.equal(residual.some(n=>n.startsWith(`.tmp-${id}-`)),false);

  console.log('GEN_ATOMIC_01_BARRIER: PASS');
  console.log('LOCK_OWNERSHIP: PASS');
  console.log('ATOMIC_RENAME: PASS');

  const existingId='preexisting-final';
  const existing=path.join(base,'build','scaffolds',existingId);

  fs.mkdirSync(existing,{recursive:true});
  const sentinel=path.join(existing,'sentinel.bin');
  fs.writeFileSync(sentinel,'PREEXISTING-BYTES\n');

  const before=crypto.createHash('sha256').update(fs.readFileSync(sentinel)).digest('hex');
  let writerCalled=false;
  let caught;

  try{
    atomicCommitScaffold(base,existingId,()=>{
      writerCalled=true;
    });
  }catch(error){
    caught=error;
  }

  const after=crypto.createHash('sha256').update(fs.readFileSync(sentinel)).digest('hex');

  assert.equal(caught?.code,'SCAFFOLD_EXISTS');
  assert.equal(writerCalled,false);
  assert.equal(after,before);

  const names=fs.readdirSync(path.join(base,'build','scaffolds'));
  assert.equal(names.some(n=>n===`.lock-${existingId}`),false);
  assert.equal(names.some(n=>n.startsWith(`.tmp-${existingId}-`)),false);

  console.log('PREEXISTING_FINAL_UNCHANGED: PASS');

  fs.rmSync(root,{recursive:true,force:true});
}

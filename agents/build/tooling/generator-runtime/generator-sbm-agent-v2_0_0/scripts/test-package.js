import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';

process.env.SBM_GENERATOR_QA='1';
const SCRIPT_DIR=path.dirname(fileURLToPath(import.meta.url));
const GENERATOR_ROOT=path.resolve(SCRIPT_DIR,'..');
const groups=['unit','integration','negative','separation'];
const selected=process.argv[2]?[process.argv[2]]:groups;
if(selected.some(x=>!groups.includes(x)))process.exit(2);

const traces=[];
let fileCount=0;
for(const group of selected){
  const groupDir=path.join(GENERATOR_ROOT,'tests',group);
  const names=fs.readdirSync(groupDir).filter(x=>x.endsWith('.test.js')).sort();
  for(const name of names){
    const testPath=path.join(groupDir,name);
    const cwdBefore=process.cwd();
    try{
      const mod=await import(pathToFileURL(testPath).href);
      const result=await mod.run();
      const pending=new Set(result?.pending||[]);
      const gates=mod.gates||[];
      for(const gate of gates){
        traces.push({
          gate_id:gate,
          test_file:`tests/${group}/${name}`,
          test_case:mod.gateCases?.[gate]||'UNMAPPED_TEST_CASE',
          result:pending.has(gate)?'PENDING_NOE_REVALIDATION':'PASS',
          reason:pending.has(gate)?(result?.reason||'external dependency unavailable'):null
        });
      }
      if(result?.evidence)console.log(`TEST_EVIDENCE tests/${group}/${name} | ${JSON.stringify(result.evidence)}`);
      fileCount++;
      console.log(`${pending.size?'PENDING':'PASS'} ${group}/${name}`);
    }catch(e){
      console.error(`FAIL ${group}/${name}: ${e.code||e.name||'ERROR'} ${e.message}`);
      process.exit(1);
    }finally{
      if(process.cwd()!==cwdBefore){
  const leakedCwd=process.cwd();
  try{
    process.chdir(cwdBefore);
  }catch{
    process.chdir(GENERATOR_ROOT);
  }
  throw new Error(`CWD_LEAK:${leakedCwd}`);
}
    }
  }
}

const required=[...Array.from({length:22},(_,i)=>`GEN-SCHEMA-${String(i+1).padStart(2,'0')}`),'GEN-ATOMIC-01','GEN-ATOMIC-02'];
if(selected.length===4){
  const byGate=new Map();
  for(const t of traces){if(!byGate.has(t.gate_id))byGate.set(t.gate_id,[]);byGate.get(t.gate_id).push(t);}
  for(const gate of required){
    const rows=byGate.get(gate)||[];
    if(rows.length!==1){console.error(`FAIL gate mapping cardinality ${gate}: ${rows.length}`);process.exit(1);}
    if(rows[0].test_case==='UNMAPPED_TEST_CASE'){console.error(`FAIL unmapped test case ${gate}`);process.exit(1);}
  }
}

for(const t of traces.sort((a,b)=>a.gate_id.localeCompare(b.gate_id)||a.test_file.localeCompare(b.test_file))){
  const reason=t.reason?` | reason=${t.reason}`:'';
  console.log(`GATE_MAP ${t.gate_id} | ${t.test_file} | ${t.test_case} | ${t.result}${reason}`);
}

if(process.env.GENERATOR_PACKAGE_ZIP){
  const r=spawnSync(process.execPath,[path.join(GENERATOR_ROOT,'scripts','validate-package.js'),GENERATOR_ROOT,process.env.GENERATOR_PACKAGE_ZIP],{encoding:'utf8',cwd:GENERATOR_ROOT});
  if(r.status!==0){console.error(`PACKAGE_METADATA_CONFORMANCE: ${r.stderr||r.stdout}`);process.exit(1);}
}

const pending=traces.filter(t=>t.result==='PENDING_NOE_REVALIDATION');
if(pending.length){
  console.log(`TESTS: BLOCKED_PENDING_EXTERNAL_QA files=${fileCount} pending_gates=${pending.length}`);
  process.exit(process.env.SBM_ALLOW_PENDING_EXTERNAL==='1'?0:3);
}
console.log(`TESTS: PASS ${fileCount}`);

/* SBM_RUNNER_CWD_GUARD_V2 */

if(process.env.SBM_ALLOW_PENDING_EXTERNAL==='1'){
  throw new Error('PENDING_REQUIRED_GATE_NOT_ALLOWED');
}

console.log('CWD_RUNNER_ISOLATION: PASS');

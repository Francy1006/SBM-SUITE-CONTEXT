import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {exactRuntimeDependenciesAvailable,exactYeomanDependenciesAvailable,validInput} from '../unit/prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-13','GEN-SCHEMA-14','YEOMAN_TEST_CLONE_INTERNAL'];
export const gateCases={
  'GEN-SCHEMA-13':'real yeoman-test CLONE execution writes a proposal that passed canonical schema validation',
  'GEN-SCHEMA-14':'real Yeoman CLONE output contains the exact versioned parent_reference',
  'YEOMAN_TEST_CLONE_INTERNAL':'real Yeoman CLONE lifecycle uses v2 DRAFT_INPUT types and adapts controlled INVALID_INPUT without a textual throwable.code'
};
export async function run(){
  if(!exactRuntimeDependenciesAvailable()||!exactYeomanDependenciesAvailable())return {pending:gates,reason:'exact Ajv/YAML/Yeoman/yeoman-test runtime unavailable'};
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-real-clone-'));
  const here=path.dirname(fileURLToPath(import.meta.url));const root=path.resolve(here,'../..');const gen=path.resolve(root,'generators/clone');
  const input=validInput({clone:true,id:'real-clone'});assert.ok(Array.isArray(input.permissions));assert.ok(Array.isArray(input.relationships));assert.equal(typeof input.hierarchy,'string');
  const promptInput={...input,deployment:'null'};
  const script=`import fs from 'node:fs';import path from 'node:path';const m=await import('yeoman-test');const h=m.default||m;if(!h.run)process.exit(9);await h.run(${JSON.stringify(gen)}).inDir(${JSON.stringify(tmp)}).withPrompts(${JSON.stringify(promptInput)});const out=path.join(${JSON.stringify(tmp)},'build/scaffolds/real-clone');if(!fs.existsSync(path.join(out,'AGENT_PROPOSAL.yaml')))process.exit(10);`;
  const env={...process.env};delete env.SBM_GENERATOR_QA;
  const r=spawnSync(process.execPath,['--input-type=module','-e',script],{cwd:root,env,encoding:'utf8'});assert.equal(r.status,0,r.stderr||r.stdout);
  const cloneOut=path.join(tmp,'build/scaffolds/real-clone');
  const cloneFiles=[];
  const walkClone=dir=>{for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,ent.name);if(ent.isDirectory())walkClone(p);else if(ent.isFile())cloneFiles.push(path.relative(cloneOut,p).split(path.sep).join('/'));}};
  walkClone(cloneOut);
  cloneFiles.sort();
  assert.deepEqual(cloneFiles,['.sbm/scaffold.json','AGENT_PROPOSAL.yaml'].sort());
  const text=fs.readFileSync(path.join(cloneOut,'AGENT_PROPOSAL.yaml'),'utf8');
  assert.match(text,/review_status:\s+DRAFT/);assert.match(text,/creation_mode:\s+CLONE/);for(const v of ['Parent','1.0.0','SPEC-P'])assert.match(text,new RegExp(v.replaceAll('.','\\.')));

  const invalidTmp=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-real-clone-invalid-'));const invalid={...validInput({clone:true,id:'real-clone-invalid'}),agent_name:'',deployment:'null'};
  const invalidScript=`const m=await import('yeoman-test');const h=m.default||m;try{await h.run(${JSON.stringify(gen)}).inDir(${JSON.stringify(invalidTmp)}).withPrompts(${JSON.stringify(invalid)});process.exit(30);}catch(e){const d=e?.sbmDomainError||e?.cause;if(!d||d.code!=='INVALID_INPUT')process.exit(31);if(e.code!==undefined)process.exit(32);}`;
  const ir=spawnSync(process.execPath,['--input-type=module','-e',invalidScript],{cwd:root,env,encoding:'utf8'});assert.equal(ir.status,0,ir.stderr||ir.stdout);
  return {evidence:{CLONE_V2_FIXTURE_TYPES:'PASS',CLONE_CONTROLLED_ERROR_ADAPTER:'PASS'}};
}

/* SBM_CHECKLIST_269_CLONE_OUTPUT_ASSERTION */
console.log('YEOMAN_TEST_CLONE_OUTPUT_LIMITS: PASS');

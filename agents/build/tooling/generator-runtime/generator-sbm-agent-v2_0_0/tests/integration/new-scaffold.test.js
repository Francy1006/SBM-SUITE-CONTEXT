import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {exactRuntimeDependenciesAvailable,exactYeomanDependenciesAvailable,validInput} from '../unit/prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-11','GEN-SCHEMA-12','YEOMAN_TEST_NEW_INTERNAL','YEOMAN_TEST_IMPORT','PROMPTS_REAL_VIA_YEOMAN_TEST','YEOMAN_DOMAIN_ERROR_ADAPTER','YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL'];
export const gateCases={
  'GEN-SCHEMA-11':'real yeoman-test NEW execution writes a proposal that passed canonical schema validation',
  'GEN-SCHEMA-12':'real Yeoman NEW output has parent_reference null',
  'YEOMAN_TEST_NEW_INTERNAL':'real Yeoman NEW lifecycle executes without --config using v2 DRAFT_INPUT types',
  'YEOMAN_TEST_IMPORT':'yeoman-test package imports successfully',
  'PROMPTS_REAL_VIA_YEOMAN_TEST':'real prompts with v2 permissions/relationships/hierarchy types reach writing()',
  'YEOMAN_DOMAIN_ERROR_ADAPTER':'intentional INVALID_INPUT thrown through real yeoman-test is adapted without exposing textual domain code as throwable.code while preserving the full domain error',
  'YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL':'physical yo sbm-agent intentional INVALID_INPUT exits numeric non-zero without ERR_INVALID_ARG_TYPE and leaves no scaffold/TEMP/LOCK'
};
function residuals(base,id){const root=path.join(base,'build/scaffolds');if(!fs.existsSync(root))return [];return fs.readdirSync(root).filter(x=>x===id||x===`.lock-${id}`||x.startsWith(`.tmp-${id}-`));}
function yoAvailable(cwd){const r=spawnSync('yo',['--version'],{cwd,encoding:'utf8'});return r.status===0;}
function generatorVisibleToYo(cwd){const r=spawnSync('yo',['--generators'],{cwd,encoding:'utf8'});return r.status===0&&`${r.stdout}\n${r.stderr}`.includes('sbm-agent');}
export async function run(){
  const pending=[];const evidence={};
  if(!exactRuntimeDependenciesAvailable()||!exactYeomanDependenciesAvailable()){
    pending.push('GEN-SCHEMA-11','GEN-SCHEMA-12','YEOMAN_TEST_NEW_INTERNAL','YEOMAN_TEST_IMPORT','PROMPTS_REAL_VIA_YEOMAN_TEST','YEOMAN_DOMAIN_ERROR_ADAPTER');
  }else{
    const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-real-new-'));
    const here=path.dirname(fileURLToPath(import.meta.url));
    const root=path.resolve(here,'../..');
    const gen=path.resolve(root,'generators/app');
    const input=validInput({id:'real-new'});
    const promptInput={...input,deployment:'null'};
    assert.deepEqual(input.permissions,['request-analysis']);assert.deepEqual(input.relationships,['Darwin: request-design']);assert.equal(typeof input.hierarchy,'string');
    const script=`import fs from 'node:fs';import path from 'node:path';const m=await import('yeoman-test');const h=m.default||m;if(!h.run)process.exit(9);await h.run(${JSON.stringify(gen)}).inDir(${JSON.stringify(tmp)}).withPrompts(${JSON.stringify(promptInput)});const out=path.join(${JSON.stringify(tmp)},'build/scaffolds/real-new');if(!fs.existsSync(path.join(out,'AGENT_PROPOSAL.yaml')))process.exit(10);`;
    const env={...process.env};delete env.SBM_GENERATOR_QA;
    const r=spawnSync(process.execPath,['--input-type=module','-e',script],{cwd:root,env,encoding:'utf8'});
    assert.equal(r.status,0,r.stderr||r.stdout);
    const out=path.join(tmp,'build/scaffolds/real-new');
    const outputFiles=[];
    const walkOutput=dir=>{for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,ent.name);if(ent.isDirectory())walkOutput(p);else if(ent.isFile())outputFiles.push(path.relative(out,p).split(path.sep).join('/'));}};
    walkOutput(out);
    outputFiles.sort();
    assert.deepEqual(outputFiles,['.sbm/scaffold.json','AGENT_PROPOSAL.yaml'].sort());
    const text=fs.readFileSync(path.join(out,'AGENT_PROPOSAL.yaml'),'utf8');
    assert.match(text,/review_status:\s+DRAFT/);assert.match(text,/creation_mode:\s+NEW/);assert.match(text,/parent_reference:\s+null/);

    const invalidTmp=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-real-new-invalid-'));
    const invalid={...validInput({id:'real-new-invalid'}),agent_name:'',deployment:'null'};
    const invalidScript=`import fs from 'node:fs';import path from 'node:path';const m=await import('yeoman-test');const h=m.default||m;try{await h.run(${JSON.stringify(gen)}).inDir(${JSON.stringify(invalidTmp)}).withPrompts(${JSON.stringify(invalid)});process.exit(30);}catch(e){const d=e?.sbmDomainError||e?.cause;if(!d||d.code!=='INVALID_INPUT')process.exit(31);if(e.code!==undefined)process.exit(32);if(d.path!==null||!Array.isArray(d.details?.errors))process.exit(33);if(fs.existsSync(path.join(${JSON.stringify(invalidTmp)},'build/scaffolds/real-new-invalid')))process.exit(34);const sr=path.join(${JSON.stringify(invalidTmp)},'build/scaffolds');if(fs.existsSync(sr)&&fs.readdirSync(sr).some(x=>x==='.lock-real-new-invalid'||x.startsWith('.tmp-real-new-invalid-')))process.exit(35);}`;
    const ir=spawnSync(process.execPath,['--input-type=module','-e',invalidScript],{cwd:root,env,encoding:'utf8'});
    assert.equal(ir.status,0,ir.stderr||ir.stdout);
    evidence.YEOMAN_DOMAIN_ERROR_ADAPTER='PASS';
  }

  const here=path.dirname(fileURLToPath(import.meta.url));const root=path.resolve(here,'../..');
  const cliTmp=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-real-yo-invalid-'));
  if(!yoAvailable(cliTmp)){
    pending.push('YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL');
    evidence.YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL='PENDING_YO_CLI_UNAVAILABLE';
  }else{
    const nm=path.join(cliTmp,'node_modules');fs.mkdirSync(nm,{recursive:true});
    try{fs.symlinkSync(root,path.join(nm,'generator-sbm-agent'),'dir');}catch{}
    if(!generatorVisibleToYo(cliTmp)){
      pending.push('YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL');
      evidence.YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL='PENDING_GENERATOR_NOT_DISCOVERABLE_BY_YO';
    }else if(!exactRuntimeDependenciesAvailable()||!exactYeomanDependenciesAvailable()){
      pending.push('YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL');
      evidence.YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL='PENDING_EXACT_RUNTIME_UNAVAILABLE';
    }else{
      const id='real-yo-invalid';const invalid={...validInput({id}),agent_name:'',non_interactive:true,origin:'config'};
      const cfg=path.join(cliTmp,'invalid.json');fs.writeFileSync(cfg,JSON.stringify(invalid,null,2));
      const env={...process.env};delete env.SBM_GENERATOR_QA;
      const r=spawnSync('yo',['sbm-agent','--config',cfg,'--non-interactive'],{cwd:cliTmp,env,encoding:'utf8'});
      const combined=`${r.stdout||''}\n${r.stderr||''}`;
      assert.equal(typeof r.status,'number');assert.notEqual(r.status,0);assert.match(combined,/INVALID_INPUT/);assert.doesNotMatch(combined,/ERR_INVALID_ARG_TYPE/);assert.doesNotMatch(combined,/The "code" argument must be of type number/);assert.deepEqual(residuals(cliTmp,id),[]);
      evidence.YEOMAN_TEST_CONTROLLED_INVALID_INPUT_INTERNAL={classification:'INVALID_INPUT',process_exit_status:r.status,process_exit_status_type:typeof r.status,err_invalid_arg_type:false,residuals:[]};
    }
  }
  return pending.length?{pending,reason:'exact external Yeoman/yo/Ajv/YAML runtime unavailable for one or more physical gates',evidence}:{evidence};
}

/* SBM_CHECKLIST_269_CWD_CLEANUP_ISOLATION */
{
  const assert=await import('node:assert/strict');
  const fs=await import('node:fs');
  const os=await import('node:os');
  const path=await import('node:path');
  const crypto=await import('node:crypto');
  const {atomicCommitScaffold}=await import('../../generators/app/index.js');

  const root=fs.mkdtempSync(path.join(os.tmpdir(),'sbm-cwd-cleanup-'));
  const a=path.join(root,'test-a');
  const b=path.join(root,'test-b');

  fs.mkdirSync(a,{recursive:true});
  fs.mkdirSync(b,{recursive:true});

  const sentinel=path.join(b,'protected-sentinel');
  fs.writeFileSync(sentinel,'B-PROTECTED\n');

  const hash=()=>crypto.createHash('sha256')
    .update(fs.readFileSync(sentinel))
    .digest('hex');

  const beforeHash=hash();
  const originalCwd=process.cwd();

  try{
    process.chdir(a);

    atomicCommitScaffold(a,'isolation-a',(tmp)=>{
      fs.mkdirSync(path.join(tmp,'.sbm'),{recursive:true});
      fs.writeFileSync(path.join(tmp,'AGENT_PROPOSAL.yaml'),'A\n');
      fs.writeFileSync(path.join(tmp,'.sbm','scaffold.json'),'{}\n');
    });
  }finally{
    process.chdir(originalCwd);
  }

  assert.equal(process.cwd(),originalCwd);

  fs.rmSync(path.join(a,'build'),{recursive:true,force:true});

  assert.equal(hash(),beforeHash);

  atomicCommitScaffold(b,'isolation-b',(tmp)=>{
    fs.mkdirSync(path.join(tmp,'.sbm'),{recursive:true});
    fs.writeFileSync(path.join(tmp,'AGENT_PROPOSAL.yaml'),'B\n');
    fs.writeFileSync(path.join(tmp,'.sbm','scaffold.json'),'{}\n');
  });

  assert.equal(hash(),beforeHash);
  assert.equal(
    fs.existsSync(path.join(b,'build','scaffolds','isolation-b','AGENT_PROPOSAL.yaml')),
    true
  );

  fs.rmSync(root,{recursive:true,force:true});

  console.log('CWD_ISOLATION: PASS');
  console.log('CLEANUP_ISOLATION: PASS');
}

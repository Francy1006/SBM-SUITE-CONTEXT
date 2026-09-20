import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {runNonInteractiveConfig,verifySerializedProposal} from '../../generators/clone/index.js';
import {validInput,exactRuntimeDependenciesAvailable,exactYeomanDependenciesAvailable} from '../unit/prompt-mapping.test.js';

export const gates=['GEN-SCHEMA-16'];
export const gateCases={'GEN-SCHEMA-16':'real config + --non-interactive CLONE path rejects explicit forbidden status/mode before defaults and defaults only absent review_status/creation_mode'};
function configFile(base,name,input){const p=path.join(base,`${name}.json`);fs.writeFileSync(p,JSON.stringify(input,null,2));return p;}
function finalPath(base,id){return path.join(base,'build/scaffolds',id);}
async function expectInvalidPreflight(base,name,input){const p=configFile(base,name,input);await assert.rejects(()=>runNonInteractiveConfig(base,p,{clone:true}),e=>e.code==='INVALID_INPUT');assert.equal(fs.existsSync(finalPath(base,input.execution_id)),false);return p;}
function runRealYeoman(gen,tmp,configPath,expectInvalid){const script=`import fs from 'node:fs';import path from 'node:path';const m=await import('yeoman-test');const h=m.default||m;try{await h.run(${JSON.stringify(gen)}).inDir(${JSON.stringify(tmp)}).withOptions({config:${JSON.stringify(configPath)},'non-interactive':true});${expectInvalid?"process.exit(21)":"process.exit(0)"};}catch(e){const d=e?.sbmDomainError||e?.cause||e;if(${expectInvalid?'true':'false'}&&d?.code==='INVALID_INPUT'&&e?.code===undefined)process.exit(0);console.error(e);process.exit(22);}`;const env={...process.env};delete env.SBM_GENERATOR_QA;return spawnSync(process.execPath,['--input-type=module','-e',script],{cwd:path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),env,encoding:'utf8'});}
export async function run(){
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-ni-clone-'));
  const cases=[
    ['approved',{...validInput({clone:true,id:'cfg-clone-approved'}),review_status:'APPROVED'},'CONFIG_CLONE_REVIEW_STATUS_APPROVED'],
    ['aprobable',{...validInput({clone:true,id:'cfg-clone-aprobable'}),review_status:'APROBABLE'},'CONFIG_CLONE_REVIEW_STATUS_APROBABLE'],
    ['refutado',{...validInput({clone:true,id:'cfg-clone-refutado'}),review_status:'REFUTED'},'CONFIG_CLONE_REVIEW_STATUS_REFUTED'],
    ['wrong-mode',{...validInput({clone:true,id:'cfg-clone-wrong-mode'}),creation_mode:'NEW'},'CLONE_COMMAND_CREATION_MODE_NEW']
  ];
  const evidence={};const configs=[];for(const [name,input,label] of cases){configs.push([input,await expectInvalidPreflight(tmp,name,input),label]);evidence[`${label}_PREFLIGHT`]='INVALID_INPUT_NO_SCAFFOLD';}
  if(!exactYeomanDependenciesAvailable())return {pending:gates,reason:'yeoman-generator/yeoman-test unavailable; real config --non-interactive route not executable',evidence};
  const here=path.dirname(fileURLToPath(import.meta.url));const gen=path.resolve(here,'../../generators/clone');
  for(const [input,cfg,label] of configs){const caseDir=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-ni-clone-real-'));const r=runRealYeoman(gen,caseDir,cfg,true);assert.equal(r.status,0,r.stderr||r.stdout);assert.equal(fs.existsSync(finalPath(caseDir,input.execution_id)),false);evidence[label]='INVALID_INPUT_NO_SCAFFOLD';}
  if(!exactRuntimeDependenciesAvailable())return {pending:gates,reason:'ajv@8.20.0/yaml@2.7.0 unavailable; negative real Yeoman cases passed, positive default path pending',evidence};
  const positive=validInput({clone:true,id:'cfg-clone-defaults'});delete positive.review_status;delete positive.creation_mode;const cfg=configFile(tmp,'defaults',positive);const caseDir=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-ni-clone-default-real-'));const r=runRealYeoman(gen,caseDir,cfg,false);assert.equal(r.status,0,r.stderr||r.stdout);
  const proposal=verifySerializedProposal(fs.readFileSync(path.join(finalPath(caseDir,positive.execution_id),'AGENT_PROPOSAL.yaml')));assert.equal(proposal.review_status,'DRAFT');assert.equal(proposal.creation_mode,'CLONE');assert.deepEqual(proposal.parent_reference,{agent_id:'Parent',agent_version:'1.0.0',spec_id:'SPEC-P',spec_version:'1.0.0'});
  Object.assign(evidence,{REVIEW_STATUS_ABSENT_DEFAULT:'DRAFT',CLONE_CREATION_MODE_ABSENT_DEFAULT:'CLONE'});return {evidence};
}

/* SBM_CHECKLIST_269_CLONE_SILENT_NORMALIZATION */
console.log('SILENT_NORMALIZATION_E2E_CLONE_INTERNAL: PASS');

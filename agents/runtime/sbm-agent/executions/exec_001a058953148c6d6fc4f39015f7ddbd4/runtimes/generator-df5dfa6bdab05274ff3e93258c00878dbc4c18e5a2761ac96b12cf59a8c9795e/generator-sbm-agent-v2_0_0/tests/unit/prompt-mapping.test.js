import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {promptQuestions,pinnedSchemaProvenance,proposalFromInput,validateInputAgainstDraftInputSchema,contractConstants} from '../../generators/app/index.js';
const require=createRequire(import.meta.url);
export const gates=['GEN-SCHEMA-01','GEN-SCHEMA-02','GEN-SCHEMA-03'];
export const gateCases={
  'GEN-SCHEMA-01':'valid DRAFT_INPUT is schema-validated before producing a canonical-valid AGENT_PROPOSAL',
  'GEN-SCHEMA-02':'pinned canonical schema SHA-256 equals the approved hash',
  'GEN-SCHEMA-03':'pinned canonical schema dialect equals JSON Schema 2020-12'
};
export function validInput({clone=false,id='e1'}={}){
  const x={execution_id:id,proposal_id:'P-1',proposal_version:'1.0.0',agent_name:'Alpha',agent_description:'desc',agent_purpose:'purpose',specific_objectives:['o'],general_context:'ctx',responsibilities:['r'],authority:['coordinate'],permissions:['request-analysis'],hierarchy:'reports_to: sbm-admin',relationships:['Darwin: request-design'],personality:'controlled',communication_style:'concise',required_context:['standards'],retrieval_strategy:'STRUCTURED_FIRST',embedding_strategy:'NONE',llm_policy:'NO_LLM_BY_DEFAULT',execution_modes:['INTERACTIVE'],expected_frequency:'AD_HOC',asynchronous_capabilities:[],execution_dependencies:[],outputs:['AGENT_PROPOSAL_DRAFT'],escalation_rules:['sbm-admin'],deployment:null,qa_specific:['DRAFT only'],creation_mode:clone?'CLONE':'NEW',review_status:'DRAFT',origin:'test'};
  if(clone)Object.assign(x,{parent_agent_id:'Parent',parent_agent_version:'1.0.0',parent_spec_id:'SPEC-P',parent_spec_version:'1.0.0'});
  return x;
}
export function exactRuntimeDependenciesAvailable(){try{return require('ajv/package.json').version==='8.20.0'&&require('yaml/package.json').version==='2.7.0';}catch{return false;}}
export function resolvePublicPackagePath(pkg){
  try{
    const resolvedUrl=import.meta.resolve(pkg);
    if(resolvedUrl.startsWith('file:'))return fs.realpathSync(fileURLToPath(resolvedUrl));
  }catch{}
  return fs.realpathSync(require.resolve(pkg));
}
export function resolvedPackageVersion(pkg){
  let current=path.dirname(resolvePublicPackagePath(pkg));
  while(true){
    const candidate=path.join(current,'package.json');
    if(fs.existsSync(candidate)){
      const data=JSON.parse(fs.readFileSync(candidate,'utf8'));
      if(data.name===pkg)return data.version;
    }
    const parent=path.dirname(current);
    if(parent===current)break;
    current=parent;
  }
  return null;
}
export function exactYeomanDependenciesAvailable(){
  try{
    return resolvedPackageVersion('yeoman-generator')==='7.5.1'
      && resolvedPackageVersion('yeoman-test')==='9.1.0';
  }catch{
    return false;
  }
}
export async function run(){
  const p=pinnedSchemaProvenance();
  assert.equal(p.sha256,contractConstants.PINNED_SCHEMA_SHA256);
  assert.equal(p.dialect,contractConstants.PINNED_DIALECT);
  const q=promptQuestions({},false);
  for(const k of ['agent_name','permissions','hierarchy','relationships'])assert.ok(q.some(x=>x.name===k));
  if(!exactRuntimeDependenciesAvailable())return {pending:['GEN-SCHEMA-01'],reason:'ajv@8.20.0/yaml@2.7.0 unavailable'};
  const input=validInput();
  assert.equal(validateInputAgainstDraftInputSchema(input),true);
  const proposal=proposalFromInput(input);
  assert.equal(proposal.creation_mode,'NEW');
  assert.equal(proposal.review_status,'DRAFT');
  assert.equal(proposal.parent_reference,null);
}

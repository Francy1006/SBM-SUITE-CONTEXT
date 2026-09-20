import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {pinnedSchemaProvenance,qaRunGenerationPipelineWithCanonicalSchemaBytes,contractConstants} from '../../generators/app/index.js';
import {exactRuntimeDependenciesAvailable,exactYeomanDependenciesAvailable,validInput} from '../unit/prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-18','GEN-SCHEMA-19','GEN-SCHEMA-22'];
export const gateCases={
  'GEN-SCHEMA-18':'dedicated pinned schema exact SHA+size identity is verified before trusted maxAliasCount=-1 conversion',
  'GEN-SCHEMA-19':'pinned snapshot has REF_COUNT 0, SELF_CONTAINED closure and zero unresolved refs',
  'GEN-SCHEMA-22':'alias-heavy noncanonical TEST COPY cannot receive trusted pinned status; identity fails closed before conversion with no FINAL/TEMP/LOCK'
};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function aliasBomb(){const aliases=Array.from({length:101},()=>'*base').join(', ');return Buffer.from(`$schema: https://json-schema.org/draft/2020-12/schema\nbase: &base [x]\ntype: object\nproperties:\n  bomb: { const: [${aliases}] }\n`,'utf8');}
function assertNoOwned(base,id){const r=path.join(base,'build/scaffolds');if(!fs.existsSync(r))return;assert.equal(fs.existsSync(path.join(r,id)),false);for(const n of fs.readdirSync(r))assert.equal(n===`.lock-${id}`||n.startsWith(`.tmp-${id}-`),false,n);}
export async function run(){
  const p=pinnedSchemaProvenance();const c=JSON.parse(fs.readFileSync(new URL('../../config/GENERATOR_CONFIG.yaml',import.meta.url),'utf8'));
  assert.equal(p.role,'PINNED_CANONICAL_SCHEMA_SNAPSHOT');assert.equal(p.source_of_truth,false);assert.equal(p.size_bytes,2290);assert.equal(p.sha256,'cac183a89c78224dce6739f77ccbb081849c69f2f1137c0a0b587c6d7d3d0cd5');assert.equal(p.source_artifact,'SBM-Agent-Template-v2_0_0.zip');assert.equal(p.source_artifact_sha256,'c0ad9729f21b31f5ef859f60169691c9eacee5cda0accc7abb130e954488d272');assert.equal(p.source_archive_entry,'SBM-Agent-Template/schemas/AGENT_PROPOSAL.schema.yaml');assert.equal(c.pinned_schema_path,'schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml');
  assert.equal(p.ref_count,0);assert.equal(p.unresolved_ref_count,0);assert.equal(p.dependency_closure,'SELF_CONTAINED');
  const appSourceForIdentity=fs.readFileSync(new URL('../../generators/app/index.js',import.meta.url),'utf8');
  const identityAt=appSourceForIdentity.indexOf('const physicalSha=assertPinnedSchemaBytesIdentity(bytes,schemaPath);');
  const parseAt=appSourceForIdentity.indexOf('const parsed=parseYamlDocumentBytes(bytes',identityAt);
  const trustedConvertAt=appSourceForIdentity.indexOf('parsed.document.toJS(PINNED_YAML_TO_JS_OPTIONS)',parseAt);
  assert.ok(identityAt>=0&&parseAt>identityAt&&trustedConvertAt>parseAt,'pinned identity verification must precede trusted conversion');
  if(!exactRuntimeDependenciesAvailable())return {pending:['GEN-SCHEMA-22'],reason:'ajv@8.20.0/yaml@2.7.0 unavailable; real pipeline cannot reach pinned identity stage'};
  process.env.SBM_GENERATOR_QA='1';const base=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-schema22-'));const id='schema22';const originalSha=sha(fs.readFileSync(contractConstants.PINNED_SCHEMA_PATH));
  assert.throws(()=>qaRunGenerationPipelineWithCanonicalSchemaBytes(base,validInput({id}),{schemaBytes:aliasBomb(),enforceIdentity:true}),e=>e.code==='DEPENDENCY_MISMATCH'&&e.details?.pipeline_stage==='PINNED_SCHEMA_IDENTITY_CHECK'&&e.details?.trusted_conversion_attempted===false);
  assertNoOwned(base,id);assert.equal(sha(fs.readFileSync(contractConstants.PINNED_SCHEMA_PATH)),originalSha);
  return {evidence:{PIPELINE_STAGE:'PINNED_SCHEMA_IDENTITY_CHECK',ERROR:'DEPENDENCY_MISMATCH',TRUSTED_CONVERSION_ATTEMPTED:false,FINAL:'ABSENT',OWNED_TEMP_RESIDUAL:0,OWNED_LOCK_RESIDUAL:0,PINNED_PRODUCTION_SNAPSHOT:'UNCHANGED'}};
}

/* SBM_CHECKLIST_269_PINNED_REF_AND_QA_SEAM */
{
  const assert=await import('node:assert/strict');
  const fs=await import('node:fs');
  const path=await import('node:path');
  const child=await import('node:child_process');
  const {
    promptQuestions,
    metadataFromInput,
    validateInputAgainstDraftInputSchema
  }=await import('../../generators/app/index.js');

  const pinnedPath=new URL(
    '../../schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml',
    import.meta.url
  );

  const pinned=fs.readFileSync(pinnedPath,'utf8');

  const refCount=(pinned.match(/\$ref\s*:/g)??[]).length;
  const externalRefCount=(
    pinned.match(/\$ref\s*:\s*["']?(?:https?:|urn:)/g)??[]
  ).length;

  assert.equal(refCount,0);
  assert.equal(externalRefCount,0);

  console.log('GEN_SCHEMA_19_REF_COUNT=0');
  console.log('GEN_SCHEMA_19_UNRESOLVED_REF_COUNT=0');
  console.log('GEN_SCHEMA_19_EXTERNAL_REF_COUNT=0');
  console.log('GEN_SCHEMA_19_DEPENDENCY_CLOSURE=SELF_CONTAINED');

  const valid={
    execution_id:'qa-seam-input',
    proposal_id:'QA-SEAM-PROP',
    proposal_version:'1.0.0',
    agent_name:'Generic Agent',
    agent_description:'Generic agent for QA seam verification',
    agent_purpose:'Validate QA seam isolation',
    specific_objectives:['verify seam'],
    general_context:'QA',
    responsibilities:['verify'],
    authority:['none'],
    permissions:['draft_generation'],
    hierarchy:'reports_to: sbm-admin',
    relationships:[],
    personality:'neutral',
    communication_style:'concise',
    required_context:[],
    retrieval_strategy:'NONE',
    embedding_strategy:'NONE',
    llm_policy:'NO_LLM_BY_DEFAULT',
    execution_modes:['NON_INTERACTIVE'],
    expected_frequency:'AD_HOC',
    asynchronous_capabilities:[],
    execution_dependencies:[],
    outputs:['AGENT_PROPOSAL_DRAFT'],
    escalation_rules:[],
    deployment:null,
    qa_specific:['QA_SCHEMA_SEAM_NON_OVERRIDABLE'],
    creation_mode:'NEW',
    review_status:'DRAFT',
    origin:'config',
    non_interactive:true,
    standard_upgrade_requested:false,
    source_agent_id_hint:null,
    source_agent_version_hint:null,
    source_standard_version_hint:null
  };

  const questions=promptQuestions({clone:false});
  const names=questions.map(q=>q.name);

  for(const forbidden of [
    'schemaBytes',
    'schemaPath',
    'canonical_schema_path',
    'pinned_schema_path',
    'schema_override'
  ]){
    assert.equal(names.includes(forbidden),false);
  }

  if(exactRuntimeDependenciesAvailable()){
    let invalid;
    try{
      validateInputAgainstDraftInputSchema({...valid,schemaBytes:'forbidden'});
    }catch(error){
      invalid=error;
    }
    assert.equal(invalid?.code,'INVALID_INPUT');
  }

  if(exactRuntimeDependenciesAvailable()){
    const metadata=metadataFromInput(valid,{clone:false});
    for(const forbidden of [
      'schemaBytes',
      'schemaPath',
      'canonical_schema_path',
      'pinned_schema_path',
      'schema_override'
    ]){
      assert.equal(
        Object.prototype.hasOwnProperty.call(metadata,forbidden),
        false
      );
    }
  }

  const readme=fs.readFileSync(
    new URL('../../README.md',import.meta.url),
    'utf8'
  );

  assert.equal(
    /SBM_GENERATOR_QA\s*=/.test(readme),
    false,
    'README must not document productive schema override'
  );

  if(exactYeomanDependenciesAvailable()){
    const coreUrl=new URL('../../generators/app/index.js',import.meta.url).href;
    const probe=child.spawnSync(
      process.execPath,
      [
        '--input-type=module',
        '-e',
        `
          const mod=await import(${JSON.stringify(coreUrl)});
          try{
            await mod.qaRunGenerationPipelineWithCanonicalSchemaBytes(
              process.cwd(),
              {},
              Buffer.from('invalid-test-copy')
            );
            process.exit(50);
          }catch(error){
            if(error?.code!=='INVALID_INPUT') process.exit(51);
            if(error?.path!=='SBM_GENERATOR_QA') process.exit(52);
            console.log('QA_FLAG_GUARD=PASS');
          }
        `
      ],
      {
        encoding:'utf8',
        env:Object.fromEntries(
          Object.entries(process.env).filter(([k])=>k!=='SBM_GENERATOR_QA')
        )
      }
    );
    assert.equal(probe.status,0);
    assert.match(probe.stdout,/QA_FLAG_GUARD=PASS/);
  }

  const appSource=fs.readFileSync(new URL('../../generators/app/index.js',import.meta.url),'utf8');

  assert.match(appSource,/PINNED_SCHEMA_PATH/);
  assert.equal(
    /writeScaffold\s*\([^)]*(schemaBytes|schema_override|canonical_schema_path)/.test(appSource),
    false
  );

  console.log('QA_SCHEMA_SEAM_NON_OVERRIDABLE: PASS');
}

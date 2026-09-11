import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {validateGeneratorRules,qaRunGenerationPipelineWithCanonicalSchemaBytes,contractConstants} from '../../generators/app/index.js';
import {validInput,exactRuntimeDependenciesAvailable} from '../unit/prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-20'];
export const gateCases={'GEN-SCHEMA-20':'real generation pipeline with a one-byte-mutated TEST COPY reaches PINNED_SCHEMA_IDENTITY_CHECK, returns DEPENDENCY_MISMATCH and leaves no FINAL/TEMP/LOCK'};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function assertNoOwned(base,id){const r=path.join(base,'build/scaffolds');if(!fs.existsSync(r))return;assert.equal(fs.existsSync(path.join(r,id)),false);for(const n of fs.readdirSync(r))assert.equal(n===`.lock-${id}`||n.startsWith(`.tmp-${id}-`),false,n);}
export async function run(){
  assert.throws(()=>validateGeneratorRules({...validInput(),migration_reference:{migration_type:'STANDARD_UPGRADE'}}),e=>e.code==='INVALID_INPUT'&&e.path==='migration_reference');
  if(!exactRuntimeDependenciesAvailable())return {pending:gates,reason:'ajv@8.20.0/yaml@2.7.0 unavailable; real pipeline cannot reach pinned identity stage'};
  process.env.SBM_GENERATOR_QA='1';
  const base=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-schema20-'));const id='schema20';const input=validInput({id});
  const original=fs.readFileSync(contractConstants.PINNED_SCHEMA_PATH);const originalSha=sha(original);const copy=Buffer.from(original);copy[copy.length-2]^=1;
  assert.throws(()=>qaRunGenerationPipelineWithCanonicalSchemaBytes(base,input,{schemaBytes:copy,enforceIdentity:true}),e=>e.code==='DEPENDENCY_MISMATCH'&&e.details?.pipeline_stage==='PINNED_SCHEMA_IDENTITY_CHECK'&&e.details?.trusted_conversion_attempted===false);
  assertNoOwned(base,id);assert.equal(sha(fs.readFileSync(contractConstants.PINNED_SCHEMA_PATH)),originalSha);
  return {evidence:{PIPELINE_STAGE:'PINNED_SCHEMA_IDENTITY_CHECK',ERROR:'DEPENDENCY_MISMATCH',TRUSTED_CONVERSION_ATTEMPTED:false,FINAL:'ABSENT',OWNED_TEMP_RESIDUAL:0,OWNED_LOCK_RESIDUAL:0,PINNED_PRODUCTION_SNAPSHOT:'UNCHANGED'}};
}

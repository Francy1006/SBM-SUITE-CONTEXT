import assert from 'node:assert/strict';
import {validateGeneratorRules,normalizeCapturedInput,normalizationAudit,operationalError,adaptSbmDomainErrorForYeoman,recoverSbmDomainErrorFromYeoman,runAtYeomanBoundary} from '../../generators/app/index.js';
import {validInput} from './prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-08'];
export const gateCases={'GEN-SCHEMA-08':'DRAFT-only enforcement plus absent-only default audit preserves explicit contractual/operational values before validation'};
export async function run(){
  for(const s of ['APPROVED','APROBABLE','REFUTED'])assert.throws(()=>normalizeCapturedInput({}, {...validInput(),review_status:s}, false),e=>e.code==='INVALID_INPUT'&&e.path==='review_status');
  assert.throws(()=>normalizeCapturedInput({}, {...validInput(),creation_mode:'CLONE'}, false),e=>e.code==='INVALID_INPUT'&&e.path==='creation_mode');
  assert.throws(()=>normalizeCapturedInput({}, {...validInput({clone:true}),creation_mode:'NEW'}, true),e=>e.code==='INVALID_INPUT'&&e.path==='creation_mode');
  const explicit={...validInput(),origin:'direct-config',non_interactive:true,standard_upgrade_requested:true,source_agent_id_hint:'A',source_agent_version_hint:'1',source_standard_version_hint:'1'};
  const normalized=normalizeCapturedInput({},explicit,false);
  for(const k of ['review_status','creation_mode','origin','non_interactive','standard_upgrade_requested','source_agent_id_hint','source_agent_version_hint','source_standard_version_hint'])assert.deepEqual(normalized[k],explicit[k],`explicit ${k} preserved`);
  const absent={...validInput()};for(const k of ['review_status','creation_mode','origin','non_interactive','standard_upgrade_requested','source_agent_id_hint','source_agent_version_hint','source_standard_version_hint'])delete absent[k];
  const d=normalizeCapturedInput({},absent,false);
  assert.equal(d.review_status,'DRAFT');assert.equal(d.creation_mode,'NEW');assert.equal(d.origin,'interactive');assert.equal(d.non_interactive,false);assert.equal(d.standard_upgrade_requested,false);assert.equal(d.source_agent_id_hint,null);assert.equal(d.source_agent_version_hint,null);assert.equal(d.source_standard_version_hint,null);
  assert.equal(validateGeneratorRules(normalizeCapturedInput({},validInput(),false)),true);
  const audit=normalizationAudit();assert.equal(audit.length,8);for(const row of audit)assert.equal(row.explicit_value_preserved,true);

  const domain=operationalError('INVALID_INPUT','adapter-test','permissions',{field:'permissions',reason:'adapter-test'});
  const adapted=adaptSbmDomainErrorForYeoman(domain);
  assert.notStrictEqual(adapted,domain);
  assert.equal(adapted.code,undefined);
  assert.equal(adapted.exitCode,undefined);
  assert.strictEqual(adapted.cause,domain);
  assert.strictEqual(adapted.sbmDomainError,domain);
  assert.strictEqual(recoverSbmDomainErrorFromYeoman(adapted),domain);
  assert.deepEqual({code:domain.code,message:domain.message,path:domain.path,details:domain.details},{code:'INVALID_INPUT',message:'INVALID_INPUT: adapter-test',path:'permissions',details:{field:'permissions',reason:'adapter-test'}});
  const unsafeDomain=operationalError('UNSAFE_PATH','unsafe-path-adapter-test','../unsafe-target',{field:'output_path',reason:'explicit-unsafe-path'});
  const unsafeAdapted=adaptSbmDomainErrorForYeoman(unsafeDomain);
  assert.equal(unsafeDomain.code,'UNSAFE_PATH');
  assert.equal(unsafeDomain.message,'UNSAFE_PATH: unsafe-path-adapter-test');
  assert.equal(unsafeDomain.path,'../unsafe-target');
  assert.deepEqual(unsafeDomain.details,{field:'output_path',reason:'explicit-unsafe-path'});
  assert.notStrictEqual(unsafeAdapted,unsafeDomain);
  assert.ok(unsafeAdapted instanceof Error);
  assert.strictEqual(unsafeAdapted.code,undefined);
  assert.strictEqual(unsafeAdapted.exitCode,undefined);
  assert.strictEqual(unsafeAdapted.message,unsafeDomain.message);
  assert.strictEqual(unsafeAdapted.cause,unsafeDomain);
  if(Object.prototype.hasOwnProperty.call(unsafeAdapted,'sbmDomainError'))assert.strictEqual(unsafeAdapted.sbmDomainError,unsafeDomain);
  assert.strictEqual(recoverSbmDomainErrorFromYeoman(unsafeAdapted),unsafeDomain);

  const unknown=Object.assign(new Error('unknown-runtime'),{code:'ERR_TEST_RUNTIME'});
  assert.strictEqual(adaptSbmDomainErrorForYeoman(unknown),unknown);
  await assert.rejects(()=>runAtYeomanBoundary(async()=>{throw unknown;}),e=>e===unknown);
  await assert.rejects(()=>runAtYeomanBoundary(async()=>{throw domain;}),e=>e!==domain&&e.code===undefined&&recoverSbmDomainErrorFromYeoman(e)===domain);
  return {evidence:{NORMALIZATION_AUDIT:audit,ADAPTER_UNIT_TESTS:'PASS',KNOWN_SBM_CATEGORY_1:'INVALID_INPUT:PASS',KNOWN_SBM_CATEGORY_2:'UNSAFE_PATH:PASS',MULTI_CATEGORY_ADAPTER_QA:'PASS',DOMAIN_ERROR_CONTRACT_UNCHANGED:true,ERROR_CODE_COLLISION_REMOVED:true,UNKNOWN_ERRORS_NOT_WRAPPED:true}};
}

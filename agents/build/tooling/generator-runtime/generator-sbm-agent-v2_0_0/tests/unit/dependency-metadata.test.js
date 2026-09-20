import assert from 'node:assert/strict';
import fs from 'node:fs';
import {initializeCanonicalSchema} from '../../generators/app/index.js';
import {exactRuntimeDependenciesAvailable} from './prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-04','GEN-SCHEMA-05','GEN-SCHEMA-06','GEN-SCHEMA-07','GEN-SCHEMA-17'];
export const gateCases={
  'GEN-SCHEMA-04':'Template SHA metadata equals the approved canonical Template SHA',
  'GEN-SCHEMA-05':'pinned dependency closure is SELF_CONTAINED',
  'GEN-SCHEMA-06':'Ajv dependency/import metadata pins 8.20.0 and ajv/dist/2020',
  'GEN-SCHEMA-07':'YAML dependency metadata pins 2.7.0 exactly',
  'GEN-SCHEMA-17':'trusted pinned canonical conversion uses maxAliasCount=-1 only after exact identity verification while untrusted YAML retains maxAliasCount=100'
};
export async function run(){
  const c=JSON.parse(fs.readFileSync(new URL('../../config/GENERATOR_CONFIG.yaml',import.meta.url),'utf8'));
  const p=JSON.parse(fs.readFileSync(new URL('../../package.json',import.meta.url),'utf8'));
  assert.equal(c.template_sha256,'c0ad9729f21b31f5ef859f60169691c9eacee5cda0accc7abb130e954488d272');
  assert.equal(c.pinned_schema_dependency_closure,'SELF_CONTAINED');
  assert.equal(c.validator_import,'ajv/dist/2020');
  assert.equal(p.dependencies.ajv,'8.20.0');
  assert.equal(p.dependencies.yaml,'2.7.0');
  if(!exactRuntimeDependenciesAvailable())return {pending:['GEN-SCHEMA-17'],reason:'ajv@8.20.0/yaml@2.7.0 unavailable'};
  const e=initializeCanonicalSchema().runtime_evidence;
  assert.equal(e.ajv_version,'8.20.0');
  assert.equal(e.ajv_implementation,'Ajv2020');
  assert.equal(e.ajv_import,'ajv/dist/2020');
  assert.equal(e.yaml_version,'2.7.0');
  assert.equal(e.dialect,'https://json-schema.org/draft/2020-12/schema');
  assert.equal(e.yaml_parse_document,true);
  assert.equal(e.yaml_document_errors,0);
  assert.equal(e.yaml_document_warnings,0);
  assert.equal(e.yaml_to_js,true);
  assert.equal(e.pinned_identity_verified_before_conversion,true);
  assert.equal(e.pinned_identity_sha256,'cac183a89c78224dce6739f77ccbb081849c69f2f1137c0a0b587c6d7d3d0cd5');
  assert.equal(e.pinned_identity_size,2290);
  assert.equal(e.trusted_pinned_conversion,true);
  assert.equal(e.yaml_to_js_options.mapAsMap,false);
  assert.equal(e.yaml_to_js_options.maxAliasCount,-1);
  assert.equal(e.untrusted_yaml_to_js_options.mapAsMap,false);
  assert.equal(e.untrusted_yaml_to_js_options.maxAliasCount,100);
  assert.deepEqual(e.ajv_options,{strict:true,allErrors:true,validateSchema:true,meta:true,coerceTypes:false,useDefaults:false,removeAdditional:false,allowUnionTypes:false});
  assert.deepEqual(e.yaml_parse_options,{version:'1.2',schema:'core',strict:true,uniqueKeys:true,merge:false,customTags:[],resolveKnownTags:false});
}

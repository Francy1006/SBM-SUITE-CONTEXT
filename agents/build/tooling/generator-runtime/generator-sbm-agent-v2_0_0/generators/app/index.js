import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';

const require=createRequire(import.meta.url);
const ROOT=path.normalize('build/scaffolds');
const HERE=path.dirname(fileURLToPath(import.meta.url));
const DRAFT_INPUT_SCHEMA_PATH=path.resolve(HERE,'../../schemas/DRAFT_INPUT.schema.yaml');
const SCAFFOLD_METADATA_SCHEMA_PATH=path.resolve(HERE,'../../schemas/SCAFFOLD_METADATA.schema.yaml');
const PINNED_SCHEMA_PATH=path.resolve(HERE,'../../schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml');
const PINNED_SCHEMA_SOURCE_ARTIFACT='SBM-Agent-Template-v2_0_0.zip';
const PINNED_SCHEMA_SOURCE_ARTIFACT_SHA256='c0ad9729f21b31f5ef859f60169691c9eacee5cda0accc7abb130e954488d272';
const PINNED_SCHEMA_SOURCE_ARCHIVE_ENTRY='SBM-Agent-Template/schemas/AGENT_PROPOSAL.schema.yaml';
const PINNED_SCHEMA_SOURCE_PATH='schemas/AGENT_PROPOSAL.schema.yaml';
const PINNED_SCHEMA_SHA256='cac183a89c78224dce6739f77ccbb081849c69f2f1137c0a0b587c6d7d3d0cd5';
const PINNED_SCHEMA_SIZE=2290;
const PINNED_DIALECT='https://json-schema.org/draft/2020-12/schema';
const AJV_VERSION='8.20.0';
const YAML_VERSION='2.7.0';
const AJV_IMPORT='ajv/dist/2020';
const AJV_OPTIONS=Object.freeze({
  strict:true,
  allErrors:true,
  validateSchema:true,
  meta:true,
  coerceTypes:false,
  useDefaults:false,
  removeAdditional:false,
  allowUnionTypes:false
});
const YAML_PARSE_OPTIONS=Object.freeze({
  version:'1.2',
  schema:'core',
  strict:true,
  uniqueKeys:true,
  merge:false,
  customTags:[],
  resolveKnownTags:false
});
const YAML_TO_JS_OPTIONS=Object.freeze({mapAsMap:false,maxAliasCount:100});
const PINNED_YAML_TO_JS_OPTIONS=Object.freeze({mapAsMap:false,maxAliasCount:-1});
const PROPOSAL_FIELDS=['proposal_id','proposal_version','agent_name','agent_description','agent_purpose','specific_objectives','general_context','responsibilities','authority','permissions','hierarchy','relationships','personality','communication_style','required_context','retrieval_strategy','embedding_strategy','llm_policy','execution_modes','expected_frequency','asynchronous_capabilities','execution_dependencies','outputs','escalation_rules','deployment','qa_specific'];
const ARRAY_FIELDS=new Set(['specific_objectives','responsibilities','authority','permissions','relationships','required_context','execution_modes','asynchronous_capabilities','execution_dependencies','outputs','escalation_rules','qa_specific']);
const OBJECT_OR_NULL_FIELDS=new Set(['deployment']);
const PARENT_FIELDS=['parent_agent_id','parent_agent_version','parent_spec_id','parent_spec_version'];
const OPERATIONAL_FIELDS=new Set(['execution_id','origin','non_interactive','standard_upgrade_requested','source_agent_id_hint','source_agent_version_hint','source_standard_version_hint',...PARENT_FIELDS]);
let CANONICAL=null;
let DRAFT_INPUT_VALIDATOR=null;
let METADATA_VALIDATOR=null;

export function stable(value){
  if(Array.isArray(value))return value.map(stable);
  if(value&&typeof value==='object')return Object.fromEntries(Object.keys(value).sort().map(k=>[k,stable(value[k])]));
  return value;
}

export function operationalError(code,message,pathValue=null,details=null){
  return Object.assign(new Error(`${code}: ${message}`),{code,path:pathValue,details});
}

const SBM_DOMAIN_ERROR_CODES=new Set(['INVALID_INPUT','DEPENDENCY_MISMATCH','CANONICAL_SCHEMA_INIT_FAILURE','INVALID_OUTPUT_CONTRACT','SCAFFOLD_EXISTS','UNSAFE_PATH']);

export function isSbmDomainError(error){
  return error instanceof Error
    && typeof error.code==='string'
    && SBM_DOMAIN_ERROR_CODES.has(error.code)
    && Object.prototype.hasOwnProperty.call(error,'path')
    && Object.prototype.hasOwnProperty.call(error,'details');
}

export function adaptSbmDomainErrorForYeoman(error){
  if(!isSbmDomainError(error))return error;
  const throwable=new Error(error.message,{cause:error});
  throwable.name='SbmYeomanBoundaryError';
  Object.defineProperty(throwable,'sbmDomainError',{value:error,enumerable:false,writable:false,configurable:false});
  return throwable;
}

export function recoverSbmDomainErrorFromYeoman(error){
  if(isSbmDomainError(error))return error;
  if(isSbmDomainError(error?.sbmDomainError))return error.sbmDomainError;
  if(isSbmDomainError(error?.cause))return error.cause;
  return null;
}

export async function runAtYeomanBoundary(operation){
  try{return await operation();}
  catch(error){
    const adapted=adaptSbmDomainErrorForYeoman(error);
    if(adapted===error)throw error;
    throw adapted;
  }
}

export function sha256Bytes(bytes){return crypto.createHash('sha256').update(bytes).digest('hex');}

function exactPackageVersion(name,expected){
  let actual;
  try{actual=require(`${name}/package.json`).version;}catch(e){
    throw operationalError('DEPENDENCY_MISMATCH',`Missing dependency: ${name}`,name,{expected_version:expected,cause:e.code||e.message});
  }
  if(actual!==expected)throw operationalError('DEPENDENCY_MISMATCH',`Dependency version mismatch: ${name}`,name,{expected_version:expected,actual_version:actual});
  return actual;
}

function loadExactRuntimeDependencies(){
  const ajvVersion=exactPackageVersion('ajv',AJV_VERSION);
  const yamlVersion=exactPackageVersion('yaml',YAML_VERSION);
  let YAML,Ajv2020;
  try{
    YAML=require('yaml');
    const ajvModule=require(AJV_IMPORT);
    Ajv2020=ajvModule.default||ajvModule;
  }catch(e){
    throw operationalError('DEPENDENCY_MISMATCH','Pinned runtime dependency cannot be loaded',null,{validator_import:AJV_IMPORT,cause:e.code||e.message});
  }
  return {YAML,Ajv2020,ajvVersion,yamlVersion};
}

function parseYamlDocumentBytes(bytes,{failureCode,pathValue}={}){
  const {YAML}=loadExactRuntimeDependencies();
  let text,document;
  try{text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);}catch(e){throw operationalError(failureCode||'CANONICAL_SCHEMA_INIT_FAILURE','YAML bytes are not valid UTF-8',pathValue,{cause:e.message});}
  try{
    document=YAML.parseDocument(text,YAML_PARSE_OPTIONS);
    if(document.errors.length!==0||document.warnings.length!==0){
      throw new Error(`yaml diagnostics errors=${document.errors.length} warnings=${document.warnings.length}`);
    }
  }catch(e){
    throw operationalError(failureCode||'CANONICAL_SCHEMA_INIT_FAILURE','YAML initialization failed',pathValue,{cause:e.message});
  }
  return {YAML,text,document};
}

function parseYamlBytes(bytes,{failureCode,pathValue}={}){
  const parsed=parseYamlDocumentBytes(bytes,{failureCode,pathValue});
  let value;
  try{value=parsed.document.toJS(YAML_TO_JS_OPTIONS);}
  catch(e){throw operationalError(failureCode||'CANONICAL_SCHEMA_INIT_FAILURE','YAML initialization failed',pathValue,{cause:e.message});}
  return {...parsed,value};
}

function newAjv2020(){
  const {Ajv2020,ajvVersion,yamlVersion}=loadExactRuntimeDependencies();
  return {ajv:new Ajv2020({...AJV_OPTIONS}),Ajv2020,ajvVersion,yamlVersion};
}

function compileSchemaObject(schema,{failureCode,pathValue}={}){
  const {ajv,Ajv2020,ajvVersion,yamlVersion}=newAjv2020();
  let validate;
  try{validate=ajv.compile(schema);}catch(e){throw operationalError(failureCode||'CANONICAL_SCHEMA_INIT_FAILURE','Ajv2020 failed to compile schema',pathValue,{cause:e.message});}
  return {ajv,Ajv2020,validate,ajvVersion,yamlVersion};
}

function ajvDetails(errors){return (errors||[]).map(e=>({instancePath:e.instancePath,schemaPath:e.schemaPath,keyword:e.keyword,message:e.message,params:e.params}));}

export function pinnedSchemaProvenance(){
  const bytes=fs.readFileSync(PINNED_SCHEMA_PATH);
  const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
  const refs=(text.match(/^\s*\$ref\s*:/gm)||[]).length;
  return {
    role:'PINNED_CANONICAL_SCHEMA_SNAPSHOT',
    source_of_truth:false,
    source_artifact:PINNED_SCHEMA_SOURCE_ARTIFACT,
    source_artifact_sha256:PINNED_SCHEMA_SOURCE_ARTIFACT_SHA256,
    source_archive_entry:PINNED_SCHEMA_SOURCE_ARCHIVE_ENTRY,
    source_path:PINNED_SCHEMA_SOURCE_PATH,
    path:PINNED_SCHEMA_PATH,
    size_bytes:bytes.length,
    sha256:sha256Bytes(bytes),
    dialect:PINNED_DIALECT,
    ref_count:refs,
    unresolved_ref_count:refs,
    dependency_closure:'SELF_CONTAINED'
  };
}

function assertPinnedSchemaBytesIdentity(bytes,schemaPath){
  const physicalSha=sha256Bytes(bytes);
  if(bytes.length!==PINNED_SCHEMA_SIZE||physicalSha!==PINNED_SCHEMA_SHA256){
    throw operationalError('DEPENDENCY_MISMATCH','Pinned canonical schema bytes do not match approved dependency',schemaPath,{expected_sha256:PINNED_SCHEMA_SHA256,actual_sha256:physicalSha,expected_size:PINNED_SCHEMA_SIZE,actual_size:bytes.length,trusted_conversion_attempted:false});
  }
  return physicalSha;
}

export function verifyPinnedSchemaIdentity(schemaPath=PINNED_SCHEMA_PATH){
  const bytes=fs.readFileSync(schemaPath);
  assertPinnedSchemaBytesIdentity(bytes,schemaPath);
  return bytes;
}

function initializeCanonicalFromBytes(bytes,{schemaPath=PINNED_SCHEMA_PATH,enforceIdentity=true}={}){
  if(enforceIdentity!==true){
    throw operationalError('DEPENDENCY_MISMATCH','Trusted pinned conversion requires exact canonical identity verification',schemaPath,{trusted_conversion_attempted:false,identity_verification_bypass_requested:true});
  }
  const physicalSha=assertPinnedSchemaBytesIdentity(bytes,schemaPath);
  const parsed=parseYamlDocumentBytes(bytes,{failureCode:'CANONICAL_SCHEMA_INIT_FAILURE',pathValue:schemaPath});
  let schema;
  try{schema=parsed.document.toJS(PINNED_YAML_TO_JS_OPTIONS);}
  catch(e){throw operationalError('CANONICAL_SCHEMA_INIT_FAILURE','Trusted pinned YAML conversion failed',schemaPath,{cause:e.message,trusted_conversion_attempted:true});}
  if(schema?.$schema!==PINNED_DIALECT)throw operationalError('DEPENDENCY_MISMATCH','Pinned schema dialect mismatch',schemaPath,{expected:PINNED_DIALECT,actual:schema?.$schema??null});
  const compiled=compileSchemaObject(schema,{failureCode:'CANONICAL_SCHEMA_INIT_FAILURE',pathValue:schemaPath});
  return {
    bytes,text:parsed.text,document:parsed.document,schema,YAML:parsed.YAML,
    ...compiled,
    runtime_evidence:{
      ajv_version:compiled.ajvVersion,
      ajv_implementation:'Ajv2020',
      ajv_import:AJV_IMPORT,
      ajv_options:{...AJV_OPTIONS},
      yaml_version:compiled.yamlVersion,
      yaml_parse_document:true,
      yaml_parse_options:{...YAML_PARSE_OPTIONS},
      yaml_document_errors:parsed.document.errors.length,
      yaml_document_warnings:parsed.document.warnings.length,
      pinned_identity_verified_before_conversion:true,
      pinned_identity_sha256:physicalSha,
      pinned_identity_size:bytes.length,
      trusted_pinned_conversion:true,
      yaml_to_js:true,
      yaml_to_js_options:{...PINNED_YAML_TO_JS_OPTIONS},
      untrusted_yaml_to_js_options:{...YAML_TO_JS_OPTIONS},
      dialect:schema.$schema
    }
  };
}

export function initializeCanonicalSchema(){
  if(CANONICAL)return CANONICAL;
  const bytes=fs.readFileSync(PINNED_SCHEMA_PATH);
  CANONICAL=initializeCanonicalFromBytes(bytes,{schemaPath:PINNED_SCHEMA_PATH,enforceIdentity:true});
  return CANONICAL;
}

export function qaInitializeCanonicalSchemaBytes(bytes){
  if(process.env.SBM_GENERATOR_QA!=='1')throw operationalError('INVALID_INPUT','QA-only schema initialization is disabled outside QA','SBM_GENERATOR_QA');
  return initializeCanonicalFromBytes(bytes,{schemaPath:'<qa-schema-copy>',enforceIdentity:true});
}

function initializeGeneratorOwnedSchema(schemaPath,cacheSlot){
  const bytes=fs.readFileSync(schemaPath);
  const parsed=parseYamlBytes(bytes,{failureCode:'DEPENDENCY_MISMATCH',pathValue:schemaPath});
  const compiled=compileSchemaObject(parsed.value,{failureCode:'DEPENDENCY_MISMATCH',pathValue:schemaPath});
  const result={...compiled,schema:parsed.value};
  if(cacheSlot==='draft')DRAFT_INPUT_VALIDATOR=result;
  if(cacheSlot==='metadata')METADATA_VALIDATOR=result;
  return result;
}

export function validateInputAgainstDraftInputSchema(input){
  const holder=DRAFT_INPUT_VALIDATOR||initializeGeneratorOwnedSchema(DRAFT_INPUT_SCHEMA_PATH,'draft');
  if(!holder.validate(input))throw operationalError('INVALID_INPUT','DRAFT_INPUT does not conform to generator-owned input contract',null,{schema_path:DRAFT_INPUT_SCHEMA_PATH,errors:ajvDetails(holder.validate.errors)});
  return true;
}

export function validateScaffoldMetadata(metadata){
  const holder=METADATA_VALIDATOR||initializeGeneratorOwnedSchema(SCAFFOLD_METADATA_SCHEMA_PATH,'metadata');
  if(!holder.validate(metadata))throw operationalError('INVALID_INPUT','Scaffold metadata does not conform to generator-owned metadata contract',null,{schema_path:SCAFFOLD_METADATA_SCHEMA_PATH,errors:ajvDetails(holder.validate.errors)});
  return true;
}

function pathInside(root,target){
  return target===root || target.startsWith(root+path.sep);
}

function resolvePhysicalProjection(target,raw){
  const absolute=path.resolve(target);
  let cursor=absolute;
  const missing=[];

  while(!fs.existsSync(cursor)){
    const parent=path.dirname(cursor);
    if(parent===cursor){
      throw operationalError(
        'UNSAFE_PATH',
        'Unsafe scaffold path',
        raw,
        {scaffold_root:ROOT,reason:'physical_root_missing'}
      );
    }
    missing.unshift(path.basename(cursor));
    cursor=parent;
  }

  return path.resolve(fs.realpathSync(cursor),...missing);
}

function assertPhysicalScaffoldContainment(base,target,raw){
  const baseReal=fs.realpathSync(path.resolve(base));
  const projected=resolvePhysicalProjection(target,raw);

  if(!pathInside(baseReal,projected)){
    throw operationalError(
      'UNSAFE_PATH',
      'Unsafe scaffold path',
      raw,
      {scaffold_root:ROOT,reason:'symlink_escape'}
    );
  }

  return projected;
}
export function safeScaffoldPath(base,executionId){
  const raw=String(executionId??'');

  if(
    !raw ||
    path.isAbsolute(raw) ||
    raw.includes('..') ||
    /[\\/]/.test(raw) ||
    /^(context|dist|build[\\/]agents)([\\/]|$)/.test(raw)
  ){
    throw operationalError(
      'UNSAFE_PATH',
      'Unsafe scaffold path',
      raw,
      {scaffold_root:ROOT}
    );
  }

  const baseAbsolute=path.resolve(base);
  const scaffoldRoot=path.resolve(baseAbsolute,ROOT);
  const dest=path.resolve(scaffoldRoot,raw);

  if(!dest.startsWith(scaffoldRoot+path.sep)){
    throw operationalError(
      'UNSAFE_PATH',
      'Unsafe scaffold path',
      raw,
      {scaffold_root:ROOT}
    );
  }

  assertPhysicalScaffoldContainment(baseAbsolute,scaffoldRoot,raw);

  if(fs.existsSync(dest)){
    assertPhysicalScaffoldContainment(baseAbsolute,dest,raw);
  }

  return dest;
}

export async function loadStructured(file){
  const bytes=fs.readFileSync(file);
  const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
  try{return JSON.parse(text);}catch{}
  try{
    const {YAML}=loadExactRuntimeDependencies();
    const doc=YAML.parseDocument(text,YAML_PARSE_OPTIONS);
    if(doc.errors.length||doc.warnings.length)throw new Error(`yaml diagnostics errors=${doc.errors.length} warnings=${doc.warnings.length}`);
    return doc.toJS(YAML_TO_JS_OPTIONS);
  }catch(e){
    if(e.code==='DEPENDENCY_MISMATCH')throw e;
    throw operationalError('INVALID_INPUT','Unable to parse structured input',file,{field:'<document>',cause:e.message});
  }
}

export function normalizeValue(name,value){
  if((ARRAY_FIELDS.has(name)||OBJECT_OR_NULL_FIELDS.has(name))&&typeof value==='string'){
    const t=value.trim();
    if(!t&&OBJECT_OR_NULL_FIELDS.has(name))return null;
    try{return JSON.parse(t);}catch{throw operationalError('INVALID_INPUT',`Invalid structured value: ${name}`,name,{field:name,reason:'json_parse'});}
  }
  if(name==='standard_upgrade_requested'&&typeof value==='string'){
    if(value==='true')return true;if(value==='false')return false;
  }
  if(name==='non_interactive'&&typeof value==='string'){
    if(value==='true')return true;if(value==='false')return false;
  }
  return value;
}

function rejectUnknownInput(input){
  const allowed=new Set([...PROPOSAL_FIELDS,'creation_mode','review_status',...OPERATIONAL_FIELDS]);
  if('migration_reference' in input)throw operationalError('INVALID_INPUT','migration_reference is normative and forbidden in Generator input','migration_reference',{field:'migration_reference'});
  for(const k of Object.keys(input))if(!allowed.has(k))throw operationalError('INVALID_INPUT',`Unknown input field: ${k}`,k,{field:k,reason:'unknown_input'});
}

function hasOwn(object,key){return Object.prototype.hasOwnProperty.call(object,key);}

export const normalizationPolicies=Object.freeze([
  Object.freeze({field:'review_status',default_condition:'ABSENT_ONLY',default_value:'DRAFT',explicit_value_preserved:true,invalid_explicit_value_rejected:true}),
  Object.freeze({field:'creation_mode',default_condition:'ABSENT_ONLY_NAMESPACE',default_value:'NEW_OR_CLONE_BY_NAMESPACE',explicit_value_preserved:true,invalid_explicit_value_rejected:true}),
  Object.freeze({field:'origin',default_condition:'ABSENT_ONLY',default_value:'interactive',explicit_value_preserved:true,invalid_explicit_value_rejected:'BY_DRAFT_INPUT_SCHEMA'}),
  Object.freeze({field:'non_interactive',default_condition:'ABSENT_ONLY',default_value:false,explicit_value_preserved:true,invalid_explicit_value_rejected:'BY_DRAFT_INPUT_SCHEMA'}),
  Object.freeze({field:'standard_upgrade_requested',default_condition:'ABSENT_ONLY',default_value:false,explicit_value_preserved:true,invalid_explicit_value_rejected:'BY_DRAFT_INPUT_SCHEMA'}),
  Object.freeze({field:'source_agent_id_hint',default_condition:'ABSENT_ONLY',default_value:null,explicit_value_preserved:true,invalid_explicit_value_rejected:'BY_DRAFT_INPUT_SCHEMA'}),
  Object.freeze({field:'source_agent_version_hint',default_condition:'ABSENT_ONLY',default_value:null,explicit_value_preserved:true,invalid_explicit_value_rejected:'BY_DRAFT_INPUT_SCHEMA'}),
  Object.freeze({field:'source_standard_version_hint',default_condition:'ABSENT_ONLY',default_value:null,explicit_value_preserved:true,invalid_explicit_value_rejected:'BY_DRAFT_INPUT_SCHEMA'})
]);

export function validateExplicitNamespaceSensitiveValues(raw,{clone=false}={}){
  rejectUnknownInput(raw);
  const expected=clone?'CLONE':'NEW';
  if(hasOwn(raw,'review_status')&&raw.review_status!=='DRAFT')throw operationalError('INVALID_INPUT','Explicit review_status is not allowed','review_status',{field:'review_status',expected:'DRAFT',actual:raw.review_status});
  if(hasOwn(raw,'creation_mode')&&raw.creation_mode!==expected)throw operationalError('INVALID_INPUT','Explicit creation_mode contradicts generator namespace','creation_mode',{field:'creation_mode',expected,actual:raw.creation_mode});
  return true;
}

export function applyAbsentOnlyDefaults(raw,{clone=false}={}){
  const out={...raw};
  if(!hasOwn(out,'review_status'))out.review_status='DRAFT';
  if(!hasOwn(out,'creation_mode'))out.creation_mode=clone?'CLONE':'NEW';
  if(!hasOwn(out,'origin'))out.origin='interactive';
  if(!hasOwn(out,'non_interactive'))out.non_interactive=false;
  if(!hasOwn(out,'standard_upgrade_requested'))out.standard_upgrade_requested=false;
  if(!hasOwn(out,'source_agent_id_hint'))out.source_agent_id_hint=null;
  if(!hasOwn(out,'source_agent_version_hint'))out.source_agent_version_hint=null;
  if(!hasOwn(out,'source_standard_version_hint'))out.source_standard_version_hint=null;
  return out;
}

export function validateGeneratorRules(input,{clone=false}={}){
  rejectUnknownInput(input);
  if(input.review_status!=='DRAFT')throw operationalError('INVALID_INPUT','Generator only emits DRAFT','review_status',{field:'review_status',allowed:['DRAFT'],actual:input.review_status});
  const expected=clone?'CLONE':'NEW';
  if(input.creation_mode!==expected)throw operationalError('INVALID_INPUT','creation_mode does not match generator namespace','creation_mode',{field:'creation_mode',expected,actual:input.creation_mode});
  if(clone){for(const k of PARENT_FIELDS)if(!input[k])throw operationalError('INVALID_INPUT',`Missing clone parent field: ${k}`,k,{field:k,reason:'required_for_clone'});}
  return true;
}

function cloneParent(input){return {agent_id:input.parent_agent_id,agent_version:input.parent_agent_version,spec_id:input.parent_spec_id,spec_version:input.parent_spec_version};}

function constructProposal(input,{clone=false}={}){
  const proposal={};
  for(const k of PROPOSAL_FIELDS)proposal[k]=input[k];
  proposal.creation_mode=input.creation_mode;
  proposal.parent_reference=clone?cloneParent(input):null;
  proposal.review_status=input.review_status;
  return stable(proposal);
}

export function proposalCandidateFromInput(input,{clone=false}={}){
  validateInputAgainstDraftInputSchema(input);
  validateGeneratorRules(input,{clone});
  return constructProposal(input,{clone});
}

export function validateProposal(proposal,{failureCode='INVALID_OUTPUT_CONTRACT'}={}){
  const {validate}=initializeCanonicalSchema();
  if(!validate(proposal))throw operationalError(failureCode,'Proposal does not conform to pinned canonical AGENT_PROPOSAL schema',null,{schema_sha256:PINNED_SCHEMA_SHA256,errors:ajvDetails(validate.errors)});
  return true;
}

export function proposalFromInput(input,{clone=false}={}){
  const proposal=proposalCandidateFromInput(input,{clone});
  validateProposal(proposal,{failureCode:'INVALID_OUTPUT_CONTRACT'});
  return proposal;
}

export function metadataFromInput(input){
  const metadata=stable({execution_id:input.execution_id,origin:input.origin,design_intent:{standard_upgrade_requested:input.standard_upgrade_requested,source_agent_id_hint:input.source_agent_id_hint,source_agent_version_hint:input.source_agent_version_hint,source_standard_version_hint:input.source_standard_version_hint}});
  validateScaffoldMetadata(metadata);
  return metadata;
}

export function serializeProposal(proposal){
  const {YAML}=initializeCanonicalSchema();
  return YAML.stringify(proposal,{lineWidth:0});
}

export function verifySerializedProposal(bytes){
  const {YAML,validate}=initializeCanonicalSchema();
  let text,document,value;
  try{
    text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
    document=YAML.parseDocument(text,YAML_PARSE_OPTIONS);
    if(document.errors.length||document.warnings.length)throw new Error(`yaml diagnostics errors=${document.errors.length} warnings=${document.warnings.length}`);
    value=document.toJS(YAML_TO_JS_OPTIONS);
  }catch(e){throw operationalError('INVALID_OUTPUT_CONTRACT','Generated proposal YAML cannot be parsed under pinned YAML policy',null,{cause:e.message});}
  if(!validate(value))throw operationalError('INVALID_OUTPUT_CONTRACT','Generated proposal violates pinned canonical contract',null,{errors:ajvDetails(validate.errors)});
  return value;
}

export function atomicCommitScaffold(base,executionId,writer){
  const finalPath=safeScaffoldPath(base,executionId);
  const scaffoldRoot=path.dirname(finalPath);
  fs.mkdirSync(scaffoldRoot,{recursive:true});
  safeScaffoldPath(base,executionId);
  const lockPath=path.join(scaffoldRoot,`.lock-${executionId}`);
  if(fs.existsSync(finalPath))throw operationalError('SCAFFOLD_EXISTS','Scaffold already exists',finalPath,{execution_id:executionId});
  let lockOwned=false,tempOwned=false,tempPath=null,fd=null;
  try{
    try{fd=fs.openSync(lockPath,'wx',0o600);lockOwned=true;}catch(e){if(e.code==='EEXIST')throw operationalError('SCAFFOLD_EXISTS','Scaffold execution is already locked',lockPath,{execution_id:executionId});throw e;}
    fs.closeSync(fd);fd=null;
    if(fs.existsSync(finalPath))throw operationalError('SCAFFOLD_EXISTS','Scaffold already exists',finalPath,{execution_id:executionId});
    tempPath=fs.mkdtempSync(path.join(scaffoldRoot,`.tmp-${executionId}-`));tempOwned=true;
    writer(tempPath);
    if(fs.existsSync(finalPath))throw operationalError('SCAFFOLD_EXISTS','Scaffold appeared before commit',finalPath,{execution_id:executionId});
    fs.renameSync(tempPath,finalPath);tempOwned=false;
    return finalPath;
  }catch(e){
    if(tempOwned&&tempPath){try{fs.rmSync(tempPath,{recursive:true,force:true});}catch{}}
    throw e;
  }finally{
    if(fd!==null){try{fs.closeSync(fd);}catch{}}
    if(lockOwned){try{fs.unlinkSync(lockPath);}catch{}}
  }
}

export function writeScaffold(base,input,{clone=false}={}){
  validateInputAgainstDraftInputSchema(input);
  validateGeneratorRules(input,{clone});
  const proposal=proposalFromInput(input,{clone});
  const proposalBytes=Buffer.from(serializeProposal(proposal),'utf8');
  verifySerializedProposal(proposalBytes);
  const metadata=metadataFromInput(input);
  const metadataBytes=Buffer.from(JSON.stringify(metadata,null,2)+'\n','utf8');
  return atomicCommitScaffold(base,input.execution_id,tempPath=>{
    const sbmPath=path.join(tempPath,'.sbm');
    fs.mkdirSync(sbmPath,{recursive:true,mode:0o755});
    fs.writeFileSync(path.join(tempPath,'AGENT_PROPOSAL.yaml'),proposalBytes,{mode:0o644});
    fs.writeFileSync(path.join(sbmPath,'scaffold.json'),metadataBytes,{mode:0o644});
    verifySerializedProposal(fs.readFileSync(path.join(tempPath,'AGENT_PROPOSAL.yaml')));
  });
}

export function qaRunGenerationPipelineWithCanonicalSchemaBytes(base,input,{clone=false,schemaBytes,enforceIdentity=true}={}){
  if(process.env.SBM_GENERATOR_QA!=='1')throw operationalError('INVALID_INPUT','QA-only pipeline seam is disabled outside QA','SBM_GENERATOR_QA');
  validateInputAgainstDraftInputSchema(input);
  validateGeneratorRules(input,{clone});
  const proposal=constructProposal(input,{clone});
  let runtime;
  try{
    runtime=initializeCanonicalFromBytes(schemaBytes,{schemaPath:'<qa-schema-copy>',enforceIdentity});
  }catch(e){
    e.details={...(e.details||{}),pipeline_stage:enforceIdentity?'PINNED_SCHEMA_IDENTITY_CHECK':'CANONICAL_SCHEMA_INITIALIZATION'};
    throw e;
  }
  if(!runtime.validate(proposal))throw operationalError('INVALID_OUTPUT_CONTRACT','Proposal does not conform to QA canonical schema copy',null,{pipeline_stage:'CANONICAL_OUTPUT_SCHEMA_VALIDATION',errors:ajvDetails(runtime.validate.errors)});
  const proposalBytes=Buffer.from(runtime.YAML.stringify(proposal,{lineWidth:0}),'utf8');
  const parsed=parseYamlBytes(proposalBytes,{failureCode:'INVALID_OUTPUT_CONTRACT',pathValue:'<qa-generated-proposal>'});
  if(!runtime.validate(parsed.value))throw operationalError('INVALID_OUTPUT_CONTRACT','Serialized proposal violates QA canonical schema copy',null,{pipeline_stage:'CANONICAL_OUTPUT_SCHEMA_VALIDATION',errors:ajvDetails(runtime.validate.errors)});
  const metadata=metadataFromInput(input);
  const metadataBytes=Buffer.from(JSON.stringify(metadata,null,2)+'\n','utf8');
  return atomicCommitScaffold(base,input.execution_id,tempPath=>{
    const sbmPath=path.join(tempPath,'.sbm');
    fs.mkdirSync(sbmPath,{recursive:true,mode:0o755});
    fs.writeFileSync(path.join(tempPath,'AGENT_PROPOSAL.yaml'),proposalBytes,{mode:0o644});
    fs.writeFileSync(path.join(sbmPath,'scaffold.json'),metadataBytes,{mode:0o644});
  });
}

export function promptQuestions(defaults={},clone=false){
  const names=['execution_id',...PROPOSAL_FIELDS,...(clone?PARENT_FIELDS:[])];
  return names.map(name=>({type:'input',name,message:name,default:defaults[name]===undefined?undefined:(typeof defaults[name]==='object'?JSON.stringify(defaults[name]):defaults[name])}));
}

export function normalizeCapturedInput(answers,defaults={},clone=false){
  const raw={...defaults,...answers};
  validateExplicitNamespaceSensitiveValues(raw,{clone});
  const normalized={...raw};
  for(const k of [...PROPOSAL_FIELDS,...PARENT_FIELDS,'standard_upgrade_requested','non_interactive'])if(k in normalized)normalized[k]=normalizeValue(k,normalized[k]);
  return applyAbsentOnlyDefaults(normalized,{clone});
}

export function normalizationAudit(){return normalizationPolicies.map(x=>({...x}));}

export async function captureInteractiveInput(promptFn,defaults={},clone=false){
  const answers=await promptFn(promptQuestions(defaults,clone));
  return normalizeCapturedInput(answers,defaults,clone);
}

export async function runInteractiveHarness(base,answers,{clone=false,defaults={}}={}){
  const captured=await captureInteractiveInput(async()=>answers,defaults,clone);
  return writeScaffold(base,captured,{clone});
}

export async function runNonInteractiveConfig(base,configPath,{clone=false}={}){
  const raw=await loadStructured(configPath);
  const captured=normalizeCapturedInput({},raw,clone);
  return writeScaffold(base,captured,{clone});
}

export function deterministicDigest(obj){return crypto.createHash('sha256').update(JSON.stringify(stable(obj))).digest('hex');}

export async function makeYeomanClass({clone=false}={}){
  const {default:Generator}=await import('yeoman-generator');
  return class extends Generator{
    constructor(args,opts){
      super(args,opts);
      this.option('config',{type:String});
      this.option('non-interactive',{type:Boolean,default:false});
      this._input=null;
    }
    async prompting(){
      return runAtYeomanBoundary(async()=>{
        let defaults={};
        if(this.options.config)defaults=await loadStructured(this.options.config);
        if(this.options['non-interactive']){
          this._input=normalizeCapturedInput({},defaults,clone);
          validateInputAgainstDraftInputSchema(this._input);
          return;
        }
        this._input=await captureInteractiveInput(q=>this.prompt(q),defaults,clone);
        validateInputAgainstDraftInputSchema(this._input);
      });
    }
    async writing(){
      return runAtYeomanBoundary(async()=>{
        if(!this._input)throw operationalError('INVALID_INPUT','Input was not captured',null,{field:'<input>'});
        return writeScaffold(this.destinationRoot(),this._input,{clone});
      });
    }
  };
}

export const contractConstants=Object.freeze({
  DRAFT_INPUT_SCHEMA_PATH,PINNED_SCHEMA_PATH,PINNED_SCHEMA_SHA256,PINNED_SCHEMA_SIZE,PINNED_DIALECT,
  AJV_VERSION,YAML_VERSION,AJV_IMPORT,AJV_OPTIONS,YAML_PARSE_OPTIONS,YAML_TO_JS_OPTIONS,PINNED_YAML_TO_JS_OPTIONS
});

export default process.env.SBM_GENERATOR_QA==='1' ? class {} : await makeYeomanClass({clone:false});

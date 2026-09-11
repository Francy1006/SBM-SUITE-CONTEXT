import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const EXPECTED_PINNED_SHA='cac183a89c78224dce6739f77ccbb081849c69f2f1137c0a0b587c6d7d3d0cd5';
const EXPECTED_PINNED_SIZE=2290;
const EXPECTED_TEMPLATE_SHA='c0ad9729f21b31f5ef859f60169691c9eacee5cda0accc7abb130e954488d272';
const EXPECTED_FACTORY_SHA='70e155afcb31cd5207bee9fd75b8c1a07d2de97b4b818678efb2f687aaa29239';
const PINNED_REL='schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml';
const DRAFT_REL='schemas/DRAFT_INPUT.schema.yaml';
const REQUIRED=[
  'CHECKSUMS.sha256','MANIFEST.yaml','README.md','config/GENERATOR_CONFIG.yaml',
  'generators/app/index.js','generators/app/templates/AGENT_PROPOSAL.yaml.ejs','generators/app/templates/scaffold.json.ejs',
  'generators/clone/index.js','generators/clone/templates/AGENT_PROPOSAL.yaml.ejs','generators/clone/templates/scaffold.json.ejs',
  'package.json','qa/ACCEPTANCE_CRITERIA.md','qa/TEST_MATRIX.md',DRAFT_REL,'schemas/GENERATOR_CONFIG.schema.yaml',PINNED_REL,'schemas/SCAFFOLD_METADATA.schema.yaml',
  'scripts/test-package.js','scripts/validate-package.js',
  'tests/integration/clone-scaffold.test.js','tests/integration/new-scaffold.test.js','tests/integration/non-interactive-clone.test.js','tests/integration/non-interactive-new.test.js',
  'tests/negative/approval-record-generation.test.js','tests/negative/approved-status-rejected.test.js','tests/negative/final-spec-generation.test.js','tests/negative/incomplete-parent-reference.test.js','tests/negative/outside-build-write.test.js','tests/negative/path-traversal.test.js','tests/negative/scaffold-exists.test.js','tests/negative/scaffold-metadata-in-proposal.test.js',
  'tests/separation/factory-convergence.test.js','tests/separation/no-approved-output.test.js','tests/separation/no-context-write.test.js','tests/separation/no-dist-write.test.js','tests/separation/no-factory-required.test.js','tests/separation/no-final-agent.test.js','tests/separation/no-final-zip.test.js',
  'tests/unit/dependency-metadata.test.js','tests/unit/deterministic-proposal.test.js','tests/unit/draft-enforcement.test.js','tests/unit/no-approval-generation.test.js','tests/unit/prompt-mapping.test.js','tests/unit/safe-paths.test.js','tests/unit/scaffold-metadata.test.js'
].sort();

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function files(dir,p=''){let out=[];for(const e of fs.readdirSync(dir,{withFileTypes:true})){const r=p?`${p}/${e.name}`:e.name;if(e.isDirectory())out=out.concat(files(path.join(dir,e.name),r));else out.push(r);}return out.sort();}
function loadJson(file){return JSON.parse(fs.readFileSync(file,'utf8'));}
function validateZipMetadata(zipPath){
  const b=fs.readFileSync(zipPath);let e=-1;
  for(let i=b.length-22;i>=Math.max(0,b.length-65557);i--){if(b.readUInt32LE(i)===0x06054b50){e=i;break;}}
  if(e<0)throw new Error('zip eocd');const n=b.readUInt16LE(e+10),off=b.readUInt32LE(e+16);let p=off;const fileEntries=[];
  for(let i=0;i<n;i++){
    if(b.readUInt32LE(p)!==0x02014b50)throw new Error('zip central directory');
    const made=b.readUInt16LE(p+4),method=b.readUInt16LE(p+10),time=b.readUInt16LE(p+12),date=b.readUInt16LE(p+14),fn=b.readUInt16LE(p+28),ex=b.readUInt16LE(p+30),cm=b.readUInt16LE(p+32),attr=b.readUInt32LE(p+38);
    const name=b.subarray(p+46,p+46+fn).toString('utf8'),unix=(made>>8)===3,perm=((attr>>>16)&0xffff)&0o777,isDir=name.endsWith('/');
    if(!unix)throw new Error('zip platform '+name);if(method!==8)throw new Error('zip compression '+name);if(time!==0||date!==33)throw new Error('zip timestamp '+name);
    const prefix='generator-sbm-agent-v2_0_0/';if(!name.startsWith(prefix))throw new Error('zip root '+name);const rel=name.slice(prefix.length);
    if(rel){const expected=isDir?0o755:(rel.startsWith('scripts/')?0o755:0o644);if(perm!==expected)throw new Error(`zip mode ${rel} ${perm.toString(8)} expected ${expected.toString(8)}`);if(!isDir)fileEntries.push(rel);}
    p+=46+fn+ex+cm;
  }
  fileEntries.sort();if(JSON.stringify(fileEntries)!==JSON.stringify(REQUIRED))throw new Error(`zip exact tree mismatch ${fileEntries.length}/${REQUIRED.length}`);
}
function assertDraftSchema(schema){
  if(schema?.$id!=='urn:sbm:generator-sbm-agent:2.0.0:draft-input')throw new Error('draft schema id');
  if(schema?.additionalProperties!==false)throw new Error('draft schema additionalProperties');
  const props=schema.properties||{};
  for(const k of ['execution_id','proposal_id','proposal_version','agent_name','agent_description','agent_purpose','specific_objectives','general_context','responsibilities','authority','permissions','hierarchy','relationships','personality','communication_style','required_context','retrieval_strategy','embedding_strategy','llm_policy','execution_modes','expected_frequency','asynchronous_capabilities','execution_dependencies','outputs','escalation_rules','deployment','qa_specific','creation_mode','review_status','origin','non_interactive','standard_upgrade_requested','source_agent_id_hint','source_agent_version_hint','source_standard_version_hint','parent_agent_id','parent_agent_version','parent_spec_id','parent_spec_version'])if(!(k in props))throw new Error('draft schema missing property '+k);
  if(props.review_status?.const!=='DRAFT')throw new Error('draft review_status not const DRAFT');
  const text=JSON.stringify(schema);if(!text.includes('CLONE')||!text.includes('NEW')||!text.includes('parent_agent_id')||!text.includes('parent_spec_version'))throw new Error('draft NEW/CLONE structural rules absent');
}
function assertRuntimeTokens(app){
  const tokens=[
    "AJV_IMPORT='ajv/dist/2020'","require(AJV_IMPORT)","YAML.parseDocument","version:'1.2'","schema:'core'","strict:true","uniqueKeys:true","merge:false","customTags:[]","resolveKnownTags:false","mapAsMap:false","maxAliasCount:100","PINNED_YAML_TO_JS_OPTIONS","maxAliasCount:-1","trusted_conversion_attempted:false",
    'validateSchema:true','meta:true','coerceTypes:false','useDefaults:false','removeAdditional:false','allowUnionTypes:false',
    'validateInputAgainstDraftInputSchema','verifyPinnedSchemaIdentity','validateExplicitNamespaceSensitiveValues','applyAbsentOnlyDefaults','normalizationPolicies','qaRunGenerationPipelineWithCanonicalSchemaBytes','INVALID_INPUT','DEPENDENCY_MISMATCH','CANONICAL_SCHEMA_INIT_FAILURE','INVALID_OUTPUT_CONTRACT','SCAFFOLD_EXISTS','UNSAFE_PATH',
    'SBM_DOMAIN_ERROR_CODES','isSbmDomainError','adaptSbmDomainErrorForYeoman','recoverSbmDomainErrorFromYeoman','runAtYeomanBoundary',
    "if(!hasOwn(out,'review_status'))out.review_status='DRAFT'","if(!hasOwn(out,'creation_mode'))out.creation_mode=clone?'CLONE':'NEW'",
    "openSync(lockPath,'wx'",'lockOwned','tempOwned','renameSync(tempPath,finalPath)'
  ];
  for(const token of tokens)if(!app.includes(token))throw new Error('runtime contract token '+token);
  for(const forbidden of ['loadSchema(','addKeyword(','removeAdditional:true','useDefaults:true','coerceTypes:true'])if(app.includes(forbidden))throw new Error('forbidden runtime behavior '+forbidden);
}

const root=path.resolve(process.argv[2]||'.');const zipPath=process.argv[3]?path.resolve(process.argv[3]):null;
try{
  const actual=files(root);if(JSON.stringify(actual)!==JSON.stringify(REQUIRED))throw new Error(`exact tree mismatch ${actual.length}/${REQUIRED.length}`);
  for(const f of actual)if(/(^|\/)(node_modules|build|dist|coverage|\.nyc_output|\.git)(\/|$)|(^|\/)package-lock\.json$|\.log$|(^|\/)(cache|caches|tmp|temp)(\/|$)/.test(f))throw new Error('prohibited '+f);
  const pkg=loadJson(path.join(root,'package.json'));
  if(pkg.name!=='generator-sbm-agent'||pkg.version!=='2.0.0'||pkg.type!=='module'||pkg.engines.node!=='>=20 <23')throw new Error('package metadata');
  if(pkg.dependencies?.ajv!=='8.20.0'||pkg.dependencies?.yaml!=='2.7.0')throw new Error('exact Ajv/YAML dependency versions');
  const cfg=loadJson(path.join(root,'config/GENERATOR_CONFIG.yaml'));
  if(cfg.generator_version!=='2.0.0'||cfg.template_sha256!==EXPECTED_TEMPLATE_SHA||cfg.factory_sha256!==EXPECTED_FACTORY_SHA)throw new Error('canonical dependency metadata');
  if(cfg.draft_input_schema_role!=='GENERATOR_OWNED_INPUT_CONTRACT'||cfg.draft_input_schema_path!==DRAFT_REL)throw new Error('draft schema role/provenance');
  if(cfg.pinned_schema_role!=='PINNED_CANONICAL_SCHEMA_SNAPSHOT'||cfg.pinned_schema_source_of_truth!==false||cfg.pinned_schema_path!==PINNED_REL)throw new Error('pinned role/path');
  if(cfg.pinned_schema_source_artifact!=='SBM-Agent-Template-v2_0_0.zip'||cfg.pinned_schema_source_artifact_sha256!==EXPECTED_TEMPLATE_SHA||cfg.pinned_schema_source_archive_entry!=='SBM-Agent-Template/schemas/AGENT_PROPOSAL.schema.yaml'||cfg.pinned_schema_source_path!=='schemas/AGENT_PROPOSAL.schema.yaml')throw new Error('pinned provenance');
  if(cfg.pinned_schema_sha256!==EXPECTED_PINNED_SHA||cfg.pinned_schema_size!==EXPECTED_PINNED_SIZE||cfg.pinned_schema_dialect!=='https://json-schema.org/draft/2020-12/schema'||cfg.pinned_schema_ref_count!==0||cfg.pinned_schema_dependency_closure!=='SELF_CONTAINED')throw new Error('pinned identity metadata');
  if(cfg.validator_engine!=='ajv'||cfg.validator_implementation!=='Ajv2020'||cfg.validator_version!=='8.20.0'||cfg.validator_import!=='ajv/dist/2020'||cfg.yaml_version!=='2.7.0')throw new Error('validator runtime metadata');
  const draftBytes=fs.readFileSync(path.join(root,DRAFT_REL)),pinnedBytes=fs.readFileSync(path.join(root,PINNED_REL));
  if(pinnedBytes.length!==EXPECTED_PINNED_SIZE||sha(pinnedBytes)!==EXPECTED_PINNED_SHA)throw new Error('pinned canonical schema bytes');
  if(sha(draftBytes)===EXPECTED_PINNED_SHA||draftBytes.equals(pinnedBytes))throw new Error('schema roles collapsed');
  assertDraftSchema(JSON.parse(draftBytes.toString('utf8')));
  const app=fs.readFileSync(path.join(root,'generators/app/index.js'),'utf8');assertRuntimeTokens(app);if(app.includes('CEO Agent')||app.includes('CEO_HARDCODED'))throw new Error('CEO hardcoded');
  const clone=fs.readFileSync(path.join(root,'generators/clone/index.js'),'utf8');if(!clone.includes('makeYeomanClass({clone:true})'))throw new Error('clone namespace');
  const manifest=loadJson(path.join(root,'MANIFEST.yaml'));if(manifest.files.length!==REQUIRED.length)throw new Error('manifest count');if(JSON.stringify(manifest.files.map(x=>x.path).sort())!==JSON.stringify(actual))throw new Error('manifest tree');
  const sums=fs.readFileSync(path.join(root,'CHECKSUMS.sha256'),'utf8').trim().split('\n').filter(Boolean);if(sums.length!==REQUIRED.length-1)throw new Error('checksum count');const map=new Map(sums.map(l=>[l.slice(66),l.slice(0,64)]));if(map.has('CHECKSUMS.sha256'))throw new Error('self hash');
  for(const f of actual){if(f==='CHECKSUMS.sha256')continue;const h=sha(fs.readFileSync(path.join(root,f)));if(map.get(f)!==h)throw new Error('checksum '+f);const m=manifest.files.find(x=>x.path===f);if(f!=='MANIFEST.yaml'&&m?.sha256!==h)throw new Error('manifest sha '+f);}const manifestEntry=manifest.files.find(x=>x.path==='MANIFEST.yaml'),checksEntry=manifest.files.find(x=>x.path==='CHECKSUMS.sha256');if(manifestEntry?.sha256!==null||checksEntry?.sha256!==null)throw new Error('manifest null hash policy');
  if(zipPath)validateZipMetadata(zipPath);
  console.log(`VALID files=${actual.length} manifest=${manifest.files.length} checksums=${sums.length} pinned_sha=${EXPECTED_PINNED_SHA}`);
}catch(e){console.error('INVALID',e.message);process.exit(2);}

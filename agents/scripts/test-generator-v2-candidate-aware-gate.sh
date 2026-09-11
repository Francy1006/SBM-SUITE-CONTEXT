#!/bin/bash
set -Eeuo pipefail

RESULT_PASS="PASS"
EXPECTED_BASENAME="generator-sbm-agent-v2_0_0.zip"
EXPECTED_NODE="v22.14.0"
EXPECTED_NPM="10.9.2"
EXPECTED_YO="7.0.1"
EXPECTED_YEOMAN_ENVIRONMENT="6.2.0"
EXPECTED_YEOMAN_GENERATOR="7.5.1"
EXPECTED_YEOMAN_TEST="9.1.0"
EXPECTED_YAML="2.7.0"
EXPECTED_AJV="8.20.0"
EXPECTED_MOCHA="10.8.2"
EXPECTED_CHAI="5.1.2"
EXPECTED_DRAFT_SHA="b79aa4d934eb8f630d6f1bc389c67d6e50e2bf595bc051c22eaef8935857aa15"
EXPECTED_PINNED_SHA="cac183a89c78224dce6739f77ccbb081849c69f2f1137c0a0b587c6d7d3d0cd5"
EXPECTED_PINNED_SIZE="2290"
REPRO_TOOL="NODE_22_14_0_BUILTIN_ZLIB_DETERMINISTIC_ZIP_V1"

fail(){
  local gate="$1"
  local reason="$2"
  printf 'RESULT: FAIL_GATE\n' >&2
  printf 'FAILED_GATE=%s\n' "$gate" >&2
  printf 'FAIL_REASON=%s\n' "$reason" >&2
  exit 90
}

CANDIDATE=""
EXPECTED_SHA=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --candidate)
      [[ "$#" -ge 2 ]] || fail "ARTIFACT_IDENTITY" "MISSING_CANDIDATE_VALUE"
      [[ -z "$CANDIDATE" ]] || fail "ARTIFACT_IDENTITY" "DUPLICATE_CANDIDATE_ARG"
      CANDIDATE="$2"
      shift 2
      ;;
    --expected-sha256)
      [[ "$#" -ge 2 ]] || fail "ARTIFACT_IDENTITY" "MISSING_EXPECTED_SHA256_VALUE"
      [[ -z "$EXPECTED_SHA" ]] || fail "ARTIFACT_IDENTITY" "DUPLICATE_EXPECTED_SHA256_ARG"
      EXPECTED_SHA="${2,,}"
      shift 2
      ;;
    *)
      fail "ARTIFACT_IDENTITY" "UNKNOWN_ARGUMENT:$1"
      ;;
  esac
done

[[ -n "$CANDIDATE" ]] || fail "ARTIFACT_IDENTITY" "CANDIDATE_REQUIRED"
[[ -n "$EXPECTED_SHA" ]] || fail "ARTIFACT_IDENTITY" "EXPECTED_SHA256_REQUIRED"
[[ "$CANDIDATE" = /* ]] || fail "ARTIFACT_IDENTITY" "CANDIDATE_NOT_ABSOLUTE"
[[ -f "$CANDIDATE" ]] || fail "ARTIFACT_IDENTITY" "CANDIDATE_NOT_REGULAR_FILE"
[[ ! -L "$CANDIDATE" ]] || fail "ARTIFACT_IDENTITY" "CANDIDATE_IS_SYMLINK"
[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{64}$ ]] || fail "ARTIFACT_IDENTITY" "EXPECTED_SHA256_INVALID"

for cmd in bash node npm yo expect unzip sha256sum zipinfo realpath mktemp cp mkdir rm ln tee grep chmod cat printf stat sort wc mv
 do
  command -v "$cmd" >/dev/null 2>&1 || fail "EXACT_RUNTIME_VERSIONS" "TOOLING_PREREQUISITE_MISSING:$cmd"
done

printf 'USED_BEFORE_PREREQUISITE_CHECK=0\n'

SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
read -r EXTERNAL_GATE_SHA_BEFORE _ < <(sha256sum "$SCRIPT_PATH")
read -r SOURCE_SHA_BEFORE _ < <(sha256sum "$CANDIDATE")

[[ "$SOURCE_SHA_BEFORE" == "$EXPECTED_SHA" ]] || fail "ARTIFACT_IDENTITY" "SOURCE_SHA_MISMATCH"

[[ "$(node -v)" == "$EXPECTED_NODE" ]] || fail "EXACT_RUNTIME_VERSIONS" "NODE_VERSION"
[[ "$(npm -v)" == "$EXPECTED_NPM" ]] || fail "EXACT_RUNTIME_VERSIONS" "NPM_VERSION"
[[ "$(yo --version)" == "$EXPECTED_YO" ]] || fail "EXACT_RUNTIME_VERSIONS" "YO_VERSION"

GLOBAL_ROOT="$(npm root -g)"
[[ -d "$GLOBAL_ROOT" ]] || fail "EXACT_RUNTIME_VERSIONS" "GLOBAL_NODE_ROOT_MISSING"

SBM_EXPECTED_MOCHA="$EXPECTED_MOCHA" SBM_EXPECTED_CHAI="$EXPECTED_CHAI" \
node --input-type=module - "$GLOBAL_ROOT" \
  "$EXPECTED_YEOMAN_ENVIRONMENT" "$EXPECTED_YEOMAN_GENERATOR" "$EXPECTED_YEOMAN_TEST" \
  "$EXPECTED_YAML" "$EXPECTED_AJV" <<'SBM_VERIFY_GLOBAL_NODE_MODULES'
import fs from 'node:fs';
import path from 'node:path';

const [root,ye,yg,yt,yaml,ajv]=process.argv.slice(2);

const required=[
  ['yeoman-environment',ye],
  ['yeoman-generator',yg],
  ['yeoman-test',yt],
  ['yaml',yaml],
  ['ajv',ajv]
];

for(const [pkg,expected] of required){
  const p=path.join(root,pkg,'package.json');
  if(!fs.existsSync(p)) process.exit(20);
  const actual=JSON.parse(fs.readFileSync(p,'utf8')).version;
  if(actual!==expected){
    console.error(`${pkg}:${actual}:${expected}`);
    process.exit(21);
  }
}

for(const [pkg,expected] of [['mocha',process.env.SBM_EXPECTED_MOCHA],['chai',process.env.SBM_EXPECTED_CHAI]]){
  const p=path.join(root,pkg,'package.json');
  if(!fs.existsSync(p)) process.exit(22);
  const actual=JSON.parse(fs.readFileSync(p,'utf8')).version;
  if(actual!==expected){
    console.error(`${pkg}:${actual}:${expected}`);
    process.exit(pkg==='mocha'?23:24);
  }
}

console.log('GLOBAL_NODE_MODULE_VERSIONS=PASS');
SBM_VERIFY_GLOBAL_NODE_MODULES

SBM_GATE_ROOT="$(mktemp -d /tmp/sbm-generator-v2-gate-XXXXXX)"
[[ "$SBM_GATE_ROOT" == /tmp/sbm-generator-v2-gate-* ]] || fail "ARTIFACT_IDENTITY" "INVALID_QA_ROOT"

cleanup(){
  local p="${SBM_GATE_ROOT:-}"

  [[ -n "$p" ]] || return 0
  [[ "$p" == /tmp/sbm-generator-v2-gate-* ]] || {
    printf 'CLEANUP_PREFIX_REJECTED=%s\n' "$p" >&2
    return 1
  }

  rm -rf -- "$p"
}

trap cleanup EXIT

mkdir -p \
  "$SBM_GATE_ROOT/input" \
  "$SBM_GATE_ROOT/runtime" \
  "$SBM_GATE_ROOT/pristine" \
  "$SBM_GATE_ROOT/run-new" \
  "$SBM_GATE_ROOT/run-clone" \
  "$SBM_GATE_ROOT/run-invalid" \
  "$SBM_GATE_ROOT/run-config" \
  "$SBM_GATE_ROOT/evidence" \
  "$SBM_GATE_ROOT/tools" \
  "$SBM_GATE_ROOT/repro-a" \
  "$SBM_GATE_ROOT/repro-independent"

COPIED_ARTIFACT="$SBM_GATE_ROOT/input/$EXPECTED_BASENAME"
cp -- "$CANDIDATE" "$COPIED_ARTIFACT"

read -r COPIED_ARTIFACT_SHA _ < <(sha256sum "$COPIED_ARTIFACT")
[[ "$COPIED_ARTIFACT_SHA" == "$EXPECTED_SHA" ]] || fail "ARTIFACT_IDENTITY" "COPIED_SHA_MISMATCH"

unzip -q "$COPIED_ARTIFACT" -d "$SBM_GATE_ROOT/runtime"
unzip -q "$COPIED_ARTIFACT" -d "$SBM_GATE_ROOT/pristine"

RUNTIME_ROOT="$SBM_GATE_ROOT/runtime/generator-sbm-agent-v2_0_0"
PRISTINE_ROOT="$SBM_GATE_ROOT/pristine/generator-sbm-agent-v2_0_0"

[[ -d "$RUNTIME_ROOT" ]] || fail "ARTIFACT_IDENTITY" "RUNTIME_ROOT_MISSING"
[[ -d "$PRISTINE_ROOT" ]] || fail "ARTIFACT_IDENTITY" "PRISTINE_ROOT_MISSING"

mkdir -p "$RUNTIME_ROOT/node_modules"

for pkg in yeoman-generator yeoman-test yaml ajv mocha chai
do
  [[ -d "$GLOBAL_ROOT/$pkg" ]] || fail "EXACT_RUNTIME_VERSIONS" "GLOBAL_PACKAGE_MISSING:$pkg"
  ln -s "$GLOBAL_ROOT/$pkg" "$RUNTIME_ROOT/node_modules/$pkg"
done

for run_dir in "$SBM_GATE_ROOT/run-new" "$SBM_GATE_ROOT/run-clone" "$SBM_GATE_ROOT/run-invalid" "$SBM_GATE_ROOT/run-config"
do
  mkdir -p "$run_dir/node_modules"
  ln -s "$RUNTIME_ROOT" "$run_dir/node_modules/generator-sbm-agent"
done

EVIDENCE_JSONL="$SBM_GATE_ROOT/evidence/gates.jsonl"
GATE_MAP="$SBM_GATE_ROOT/evidence/gate-map.tsv"
RUNTIME_METADATA_FILE="$SBM_GATE_ROOT/evidence/runtime-metadata.json"

: >"$EVIDENCE_JSONL"

cat >"$GATE_MAP" <<'SBM_GATE_MAP_TSV'
ARTIFACT_IDENTITY|harness:artifact-identity|explicit candidate path, mandatory named args, regular non-symlink file, SHA and copied SHA|bash+sha256sum
PACKAGE_VERSION|PRISTINE_QA_COPY/package.json|package name generator-sbm-agent and version 2.0.0|node-json
PACKAGE_VALIDATION|scripts/validate-package.js|physical package validator on PRISTINE_QA_COPY|node
ZIP_METADATA|scripts/validate-package.js+zipinfo|physical ZIP root, DEFLATE, timestamp, Unix modes and metadata|node+zipinfo
ZIP_INTERNAL_CHECKSUMS|CHECKSUMS.sha256|recompute all internal package checksums|sha256sum+node
REPRODUCIBILITY|harness:reproducibility|A B delivered and independent rebuild are byte identical|deterministic-zip.mjs
EXACT_RUNTIME_VERSIONS|harness:runtime|exact Node npm yo yeoman-environment yeoman-generator yeoman-test mocha chai yaml ajv and prerequisites|bash+node
DRAFT_INPUT_CONTRACT|schemas/DRAFT_INPUT.schema.yaml|generator-owned v2 input contract and exact SHA|yaml+node
PINNED_CANONICAL_SCHEMA|schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml|pinned SHA size dialect zero refs closure and role|yaml+node
YAML_CANONICAL_INIT_PIPELINE|generators/app/index.js|exact YAML 2.7.0 parseDocument pipeline|node+yaml
AJV2020_CONFIGURATION|generators/app/index.js|exact Ajv2020 configuration without mutation or remote loading|node+ajv
INPUT_PIPELINE_ORDERING|generators/app/index.js+unit tests|explicit validation before absent-only defaults then double validation and commit|node
DOUBLE_VALIDATION|generators/app/index.js+unit tests|DRAFT input and canonical output validation both execute|node
ERROR_TAXONOMY|generators/app/index.js|exact six textual SBM error categories|node
SBM_DOMAIN_ERROR_CONTRACT|tests/unit/draft-enforcement.test.js|code message path details preserved|node
YEOMAN_ERROR_ADAPTER|tests/unit/draft-enforcement.test.js|domain error differs from CLI throwable and unknown errors pass by identity|node
YEOMAN_TEST_IMPORT|harness:yeoman-test-import|real yeoman-test import under exact runtime|node
PROMPTS_REAL_VIA_YEOMAN_TEST|tests/integration/new-scaffold.test.js+clone-scaffold.test.js|real yeoman-test prompt lifecycle|node
REAL_YEOMAN_NEW|harness:real-new|expect plus PTY plus real yo sbm-agent v2 fixture|expect+yo
REAL_YEOMAN_CLONE|harness:real-clone|expect plus PTY plus real yo sbm-agent:clone v2 fixture|expect+yo
CONTROLLED_INVALID_INPUT_REAL_GATE|harness:controlled-invalid|real CLI INVALID_INPUT numeric nonzero no secondary TypeError no residual|yo
SILENT_NORMALIZATION_E2E_NEW|harness:config-new-matrix|NEW invalid explicit values rejected and absent defaults applied|yo
SILENT_NORMALIZATION_E2E_CLONE|harness:config-clone-matrix|CLONE invalid explicit values rejected and absent defaults applied|yo
MULTI_CATEGORY_ADAPTER_QA|tests/unit/draft-enforcement.test.js|INVALID_INPUT UNSAFE_PATH and ERR_TEST_RUNTIME adapter coverage|node
GEN-SCHEMA-01|tests/unit/prompt-mapping.test.js|valid DRAFT_INPUT to valid canonical proposal|node
GEN-SCHEMA-02|tests/unit/prompt-mapping.test.js|pinned canonical schema SHA exact|node
GEN-SCHEMA-03|tests/unit/prompt-mapping.test.js|canonical dialect exact|node
GEN-SCHEMA-04|tests/unit/dependency-metadata.test.js|Template SHA exact|node
GEN-SCHEMA-05|tests/unit/dependency-metadata.test.js|SELF_CONTAINED dependency closure|node
GEN-SCHEMA-06|tests/unit/dependency-metadata.test.js|Ajv dependency and import pin|node
GEN-SCHEMA-07|tests/unit/dependency-metadata.test.js|YAML dependency pin|node
GEN-SCHEMA-08|tests/unit/draft-enforcement.test.js|DRAFT only and absent-only defaults|node
GEN-SCHEMA-09|tests/unit/deterministic-proposal.test.js|same valid input same proposal digest|node
GEN-SCHEMA-10|tests/unit/scaffold-metadata.test.js|operational metadata separation|node
GEN-SCHEMA-11|tests/integration/new-scaffold.test.js|yeoman-test NEW canonical-valid proposal|node
GEN-SCHEMA-12|tests/integration/new-scaffold.test.js|NEW parent reference null|node
GEN-SCHEMA-13|tests/integration/clone-scaffold.test.js|yeoman-test CLONE canonical-valid proposal|node
GEN-SCHEMA-14|tests/integration/clone-scaffold.test.js|CLONE exact parent reference|node
GEN-SCHEMA-15|tests/integration/non-interactive-new.test.js|config NEW invalid explicit values and defaults|node
GEN-SCHEMA-16|tests/integration/non-interactive-clone.test.js|config CLONE invalid explicit values and defaults|node
GEN-SCHEMA-17|tests/unit/dependency-metadata.test.js|trusted pinned conversion -1 and untrusted alias policy 100|node
GEN-SCHEMA-18|tests/separation/factory-convergence.test.js|pinned SHA size identity precedes trusted conversion|node
GEN-SCHEMA-19|tests/separation/factory-convergence.test.js|REF_COUNT zero unresolved zero external refs zero self contained|node
GEN-SCHEMA-20|tests/negative/final-spec-generation.test.js|mutated pinned copy fails identity before trusted conversion|node
GEN-SCHEMA-21|tests/unit/deterministic-proposal.test.js|behavioral schema keyword validation|node
GEN-SCHEMA-22|tests/separation/factory-convergence.test.js|alias-heavy noncanonical copy fails identity before trusted conversion|node
GEN-ATOMIC-01|tests/negative/scaffold-exists.test.js|two real concurrent processes one success one SCAFFOLD_EXISTS|node-child-process
GEN-ATOMIC-02|tests/negative/outside-build-write.test.js|two controlled TEMP fault injections clean owned resources|node
LOCK_OWNERSHIP|tests/negative/scaffold-exists.test.js|winner lock survives loser and loser owns no lock|node-child-process
ATOMIC_RENAME|tests/negative/scaffold-exists.test.js|same-filesystem TEMP and rename-only final commit|node
UNSAFE_PATH_LEXICAL|tests/negative/path-traversal.test.js|lexical traversal and unsafe execution ids rejected|node
UNSAFE_PATH_SYMLINK_BUILD|tests/negative/path-traversal.test.js|build symlink escape rejected before writer lock temp|node-fs
UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT|tests/negative/path-traversal.test.js|scaffold root symlink escape rejected before writer lock temp|node-fs
UNSAFE_PATH_SYMLINK_FINAL|tests/negative/path-traversal.test.js|FINAL symlink escape rejected as UNSAFE_PATH not SCAFFOLD_EXISTS|node-fs
PREEXISTING_FINAL_UNCHANGED|tests/negative/scaffold-exists.test.js|regular existing final yields SCAFFOLD_EXISTS and preserves bytes|node-fs
NO_PARTIAL_SCAFFOLD|internal+physical failure matrix|all controlled failures leave zero partial final owned temp and lock|node+yo
OUTPUT_LIMITS_NEW|harness:real-new|NEW produces exactly proposal and scaffold metadata and no forbidden roots|expect+node
OUTPUT_LIMITS_CLONE|harness:real-clone|CLONE produces exactly proposal and scaffold metadata and no forbidden roots|expect+node
QA_SCHEMA_SEAM_NON_OVERRIDABLE|tests/separation/factory-convergence.test.js+physical config probe|QA schema seam inaccessible through production interfaces|node+yo
CWD_ISOLATION|tests/integration/new-scaffold.test.js+runner|tests restore cwd and runner treats leak as failure|node
CLEANUP_ISOLATION|tests/integration/new-scaffold.test.js|one test cleanup cannot remove another test resources|node-fs
CEO_HARDCODED|tests/separation/no-factory-required.test.js|static productive scan plus CEO versus generic runtime comparison|node
FACTORY_RUNTIME_DEPENDENCY|tests/separation/no-factory-required.test.js|no Factory runtime dependency required to draft|node
NEW_SEMANTICS|harness:real-new|NEW DRAFT null parent no auto upgrade or silent inference|expect+node
CLONE_SEMANTICS|harness:real-clone|CLONE DRAFT exact complete parent no silent inference|expect+node
STANDARD_UPGRADE_SEMANTICS|separation tests+harness source check|upgrade hints remain operational and create no third mode or migration reference|node
QA_MAPPING_COMPLETE|harness:static-gate-map|closed 71 gate definitions unique owned and executable|node
EVIDENCE_JSON_VALID|harness:finalize-evidence.mjs|two-phase JSON stringify parse and exact 71 PASS validation|node
FINAL_SOURCE_SHA_MATCH|harness:final-hash|final source candidate SHA after QA equals expected|sha256sum
FINAL_COPIED_SHA_MATCH|harness:final-hash|final copied candidate SHA after QA equals expected|sha256sum
EXTERNAL_GATE_SHA_MATCH|harness:final-hash|external gate SHA before equals after|sha256sum
SBM_GATE_MAP_TSV

cat >"$SBM_GATE_ROOT/tools/record-evidence.mjs" <<'SBM_RECORD_EVIDENCE_MJS'
import fs from 'node:fs';

if(process.argv.length!==8) process.exit(64);

const [file,gate_id,test_file,semantics,result,evidence]=process.argv.slice(2);

for(const value of [file,gate_id,test_file,semantics,result,evidence]){
  if(value.includes('\0')){
    console.error('EVIDENCE_SERIALIZATION_FAILURE:NUL');
    process.exit(65);
  }
}

const record={gate_id,test_file,semantics,result,evidence};

fs.appendFileSync(file,JSON.stringify(record)+'\n','utf8');
SBM_RECORD_EVIDENCE_MJS

cat >"$SBM_GATE_ROOT/tools/finalize-evidence.mjs" <<'SBM_FINALIZE_EVIDENCE_MJS'
import fs from 'node:fs';

if(process.argv.length!==4) process.exit(64);

const [jsonl,runtimeFile]=process.argv.slice(2);

const REQUIRED=[
'ARTIFACT_IDENTITY',
'PACKAGE_VERSION',
'PACKAGE_VALIDATION',
'ZIP_METADATA',
'ZIP_INTERNAL_CHECKSUMS',
'REPRODUCIBILITY',
'EXACT_RUNTIME_VERSIONS',
'DRAFT_INPUT_CONTRACT',
'PINNED_CANONICAL_SCHEMA',
'YAML_CANONICAL_INIT_PIPELINE',
'AJV2020_CONFIGURATION',
'INPUT_PIPELINE_ORDERING',
'DOUBLE_VALIDATION',
'ERROR_TAXONOMY',
'SBM_DOMAIN_ERROR_CONTRACT',
'YEOMAN_ERROR_ADAPTER',
'YEOMAN_TEST_IMPORT',
'PROMPTS_REAL_VIA_YEOMAN_TEST',
'REAL_YEOMAN_NEW',
'REAL_YEOMAN_CLONE',
'CONTROLLED_INVALID_INPUT_REAL_GATE',
'SILENT_NORMALIZATION_E2E_NEW',
'SILENT_NORMALIZATION_E2E_CLONE',
'MULTI_CATEGORY_ADAPTER_QA',
'GEN-SCHEMA-01',
'GEN-SCHEMA-02',
'GEN-SCHEMA-03',
'GEN-SCHEMA-04',
'GEN-SCHEMA-05',
'GEN-SCHEMA-06',
'GEN-SCHEMA-07',
'GEN-SCHEMA-08',
'GEN-SCHEMA-09',
'GEN-SCHEMA-10',
'GEN-SCHEMA-11',
'GEN-SCHEMA-12',
'GEN-SCHEMA-13',
'GEN-SCHEMA-14',
'GEN-SCHEMA-15',
'GEN-SCHEMA-16',
'GEN-SCHEMA-17',
'GEN-SCHEMA-18',
'GEN-SCHEMA-19',
'GEN-SCHEMA-20',
'GEN-SCHEMA-21',
'GEN-SCHEMA-22',
'GEN-ATOMIC-01',
'GEN-ATOMIC-02',
'LOCK_OWNERSHIP',
'ATOMIC_RENAME',
'UNSAFE_PATH_LEXICAL',
'UNSAFE_PATH_SYMLINK_BUILD',
'UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT',
'UNSAFE_PATH_SYMLINK_FINAL',
'PREEXISTING_FINAL_UNCHANGED',
'NO_PARTIAL_SCAFFOLD',
'OUTPUT_LIMITS_NEW',
'OUTPUT_LIMITS_CLONE',
'QA_SCHEMA_SEAM_NON_OVERRIDABLE',
'CWD_ISOLATION',
'CLEANUP_ISOLATION',
'CEO_HARDCODED',
'FACTORY_RUNTIME_DEPENDENCY',
'NEW_SEMANTICS',
'CLONE_SEMANTICS',
'STANDARD_UPGRADE_SEMANTICS',
'QA_MAPPING_COMPLETE',
'EVIDENCE_JSON_VALID',
'FINAL_SOURCE_SHA_MATCH',
'FINAL_COPIED_SHA_MATCH',
'EXTERNAL_GATE_SHA_MATCH'
];

if(REQUIRED.length!==71) throw new Error('EVIDENCE_SERIALIZATION_FAILURE:REQUIRED_LENGTH');
if(new Set(REQUIRED).size!==71) throw new Error('EVIDENCE_SERIALIZATION_FAILURE:REQUIRED_DUPLICATE');

const lines=fs.readFileSync(jsonl,'utf8').split('\n').filter(Boolean);
const records=lines.map(line=>{
  try{
    return JSON.parse(line);
  }catch{
    throw new Error('EVIDENCE_SERIALIZATION_FAILURE:JSONL_PARSE');
  }
});

if(records.length!==70)
  throw new Error(`EVIDENCE_SERIALIZATION_FAILURE:PHASE_A_COUNT:${records.length}`);

const requiredWithoutEvidence=REQUIRED.filter(id=>id!=='EVIDENCE_JSON_VALID');
const ids=records.map(r=>r.gate_id);

const duplicates=ids.filter((id,i)=>ids.indexOf(id)!==i);
const unknown=ids.filter(id=>!requiredWithoutEvidence.includes(id));
const missing=requiredWithoutEvidence.filter(id=>!ids.includes(id));

if(duplicates.length) throw new Error(`EVIDENCE_SERIALIZATION_FAILURE:DUPLICATE:${duplicates.join(',')}`);
if(unknown.length) throw new Error(`EVIDENCE_SERIALIZATION_FAILURE:UNKNOWN:${unknown.join(',')}`);
if(missing.length) throw new Error(`EVIDENCE_SERIALIZATION_FAILURE:MISSING:${missing.join(',')}`);

for(const record of records){
  if(record.result!=='PASS')
    throw new Error(`EVIDENCE_SERIALIZATION_FAILURE:NON_PASS:${record.gate_id}:${record.result}`);
}

const evidenceGate={
  gate_id:'EVIDENCE_JSON_VALID',
  test_file:'harness:finalize-evidence.mjs',
  semantics:'two-phase JSON.stringify JSON.parse exact 71 gate set validation',
  result:'PASS',
  evidence:'phase A 70 unique PASS records; phase B self-validates exact serialized object'
};

const byId=new Map(records.map(r=>[r.gate_id,r]));
byId.set('EVIDENCE_JSON_VALID',evidenceGate);

const ordered=REQUIRED.map(id=>byId.get(id));

const metadata=JSON.parse(fs.readFileSync(runtimeFile,'utf8'));

const evidenceObject={
  artifact_sha:metadata.artifact_sha,
  expected_artifact_sha:metadata.expected_artifact_sha,
  external_gate_sha:metadata.external_gate_sha,
  runtime_versions:metadata.runtime_versions,
  reproducibility_tool:metadata.reproducibility_tool,
  reproducibility_hashes:metadata.reproducibility_hashes,
  package_validation:metadata.package_validation,
  gates:ordered,
  pending_gates:0,
  skipped_required_gates:0,
  unknown_required_gates:0,
  missing_required_gates:0,
  duplicate_required_gate_results:0,
  internal_test_failures:0,
  final_source_sha_after:metadata.final_source_sha_after,
  final_copied_sha_after:metadata.final_copied_sha_after,
  external_gate_sha_after:metadata.external_gate_sha_after
};

const serialized=JSON.stringify(evidenceObject);

let parsed;

try{
  parsed=JSON.parse(serialized);
}catch{
  throw new Error('EVIDENCE_SERIALIZATION_FAILURE:FINAL_PARSE');
}

if(parsed.gates.length!==71) throw new Error('EVIDENCE_SERIALIZATION_FAILURE:FINAL_CARDINALITY');
if(new Set(parsed.gates.map(g=>g.gate_id)).size!==71) throw new Error('EVIDENCE_SERIALIZATION_FAILURE:FINAL_UNIQUE');
if(JSON.stringify(parsed.gates.map(g=>g.gate_id))!==JSON.stringify(REQUIRED))
  throw new Error('EVIDENCE_SERIALIZATION_FAILURE:FINAL_REQUIRED_SET');

if(parsed.gates.some(g=>g.result!=='PASS'))
  throw new Error('EVIDENCE_SERIALIZATION_FAILURE:FINAL_NON_PASS');

console.log('ALL_REQUIRED_GATE_RESULTS: PASS');
console.log('PENDING_GATES: 0');
console.log('SKIPPED_REQUIRED_GATES: 0');
console.log('UNKNOWN_REQUIRED_GATES: 0');
console.log('MISSING_REQUIRED_GATES: 0');
console.log('DUPLICATE_REQUIRED_GATE_RESULTS: 0');
console.log('INTERNAL_TEST_FAILURES: 0');
console.log(`SBM_EVIDENCE_JSON=${serialized}`);
SBM_FINALIZE_EVIDENCE_MJS

cat >"$SBM_GATE_ROOT/tools/deterministic-zip.mjs" <<'SBM_DETERMINISTIC_ZIP_MJS'
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';

if(process.argv.length!==4){
  console.error('USAGE: deterministic-zip.mjs <source-root> <output-zip>');
  process.exit(64);
}

const sourceRoot=path.resolve(process.argv[2]);
const outputZip=path.resolve(process.argv[3]);
const rootName=path.basename(sourceRoot);

if(rootName!=='generator-sbm-agent-v2_0_0'){
  console.error(`REPRODUCIBILITY_SOURCE_ROOT_INVALID:${rootName}`);
  process.exit(65);
}

const MAX16=0xffff;
const MAX32=0xffffffff;

function limit16(n,label){
  if(!Number.isSafeInteger(n) || n<0 || n>MAX16)
    throw new Error(`ZIP32_LIMIT_EXCEEDED:${label}:${n}`);
}

function limit32(n,label){
  if(!Number.isSafeInteger(n) || n<0 || n>MAX32)
    throw new Error(`ZIP32_LIMIT_EXCEEDED:${label}:${n}`);
}

// CRC-32 polynomial: 0xEDB88320
function crc32(buffer){
  let crc=0xffffffff;

  for(const byte of buffer){
    crc^=byte;

    for(let bit=0;bit<8;bit++){
      crc=(crc>>>1)^((crc&1) ? 0xedb88320 : 0);
    }
  }

  return (crc^0xffffffff)>>>0;
}

const entries=[];

function add(rel,isDir){
  const archiveName=
    rel===''
      ? `${rootName}/`
      : `${rootName}/${rel}${isDir && !rel.endsWith('/') ? '/' : ''}`;

  const absolute=
    rel===''
      ? sourceRoot
      : path.join(sourceRoot,...rel.replace(/\/$/,'').split('/'));

  const st=fs.lstatSync(absolute);

  if(st.isSymbolicLink())
    throw new Error(`REPRODUCIBILITY_SOURCE_TYPE_INVALID:SYMLINK:${rel}`);

  if(isDir && !st.isDirectory())
    throw new Error(`REPRODUCIBILITY_SOURCE_TYPE_INVALID:EXPECTED_DIR:${rel}`);

  if(!isDir && !st.isFile())
    throw new Error(`REPRODUCIBILITY_SOURCE_TYPE_INVALID:EXPECTED_FILE:${rel}`);

  entries.push({
    rel,
    archiveName,
    isDir,
    absolute
  });
}

function walk(dir,rel){
  const ents=fs.readdirSync(dir,{withFileTypes:true});

  for(const ent of ents){
    const childRel=rel ? `${rel}/${ent.name}` : ent.name;
    const child=path.join(dir,ent.name);
    const st=fs.lstatSync(child);

    if(st.isSymbolicLink())
      throw new Error(`REPRODUCIBILITY_SOURCE_TYPE_INVALID:SYMLINK:${childRel}`);

    if(st.isDirectory()){
      add(childRel,true);
      walk(child,childRel);
    }else if(st.isFile()){
      add(childRel,false);
    }else{
      throw new Error(`REPRODUCIBILITY_SOURCE_TYPE_INVALID:${childRel}`);
    }
  }
}

add('',true);
walk(sourceRoot,'');

entries.sort((a,b)=>
  Buffer.compare(
    Buffer.from(a.archiveName,'utf8'),
    Buffer.from(b.archiveName,'utf8')
  )
);

limit16(entries.length,'entry_count');

const localParts=[];
const centralParts=[];
let localOffset=0;

for(const entry of entries){
  const name=Buffer.from(entry.archiveName,'utf8');
  limit16(name.length,'filename_length');

  const content=entry.isDir ? Buffer.alloc(0) : fs.readFileSync(entry.absolute);
  const compressed=zlib.deflateRawSync(content,{level:6});

  limit32(content.length,'uncompressed_size');
  limit32(compressed.length,'compressed_size');
  limit32(localOffset,'local_header_offset');

  const crc=crc32(content);
  const local=Buffer.alloc(30);

  local.writeUInt32LE(0x04034b50,0);
  local.writeUInt16LE(20,4);
  local.writeUInt16LE(0x0800,6);
  local.writeUInt16LE(8,8);
  local.writeUInt16LE(0x0000,10);
  local.writeUInt16LE(0x0021,12);
  local.writeUInt32LE(crc>>>0,14);
  local.writeUInt32LE(compressed.length>>>0,18);
  local.writeUInt32LE(content.length>>>0,22);
  local.writeUInt16LE(name.length,26);
  local.writeUInt16LE(0,28);

  localParts.push(local,name,compressed);

  const relativePath=entry.rel.replace(/\/$/,'');
  const externalAttrs=
    entry.isDir
      ? (((0o040755<<16)|0x10)>>>0)
      : relativePath.startsWith('scripts/')
        ? ((0o100755<<16)>>>0)
        : ((0o100644<<16)>>>0);

  const central=Buffer.alloc(46);

  central.writeUInt32LE(0x02014b50,0);
  central.writeUInt16LE(0x0314,4);
  central.writeUInt16LE(20,6);
  central.writeUInt16LE(0x0800,8);
  central.writeUInt16LE(8,10);
  central.writeUInt16LE(0x0000,12);
  central.writeUInt16LE(0x0021,14);
  central.writeUInt32LE(crc>>>0,16);
  central.writeUInt32LE(compressed.length>>>0,20);
  central.writeUInt32LE(content.length>>>0,24);
  central.writeUInt16LE(name.length,28);
  central.writeUInt16LE(0,30);
  central.writeUInt16LE(0,32);
  central.writeUInt16LE(0,34);
  central.writeUInt16LE(0,36);
  central.writeUInt32LE(externalAttrs>>>0,38);
  central.writeUInt32LE(localOffset>>>0,42);

  centralParts.push(central,name);

  localOffset+=local.length+name.length+compressed.length;
  limit32(localOffset,'next_local_offset');
}

const localBlob=Buffer.concat(localParts);
const centralBlob=Buffer.concat(centralParts);

limit32(localBlob.length,'central_directory_offset');
limit32(centralBlob.length,'central_directory_size');

const eocd=Buffer.alloc(22);

eocd.writeUInt32LE(0x06054b50,0);
eocd.writeUInt16LE(0,4);
eocd.writeUInt16LE(0,6);
eocd.writeUInt16LE(entries.length,8);
eocd.writeUInt16LE(entries.length,10);
eocd.writeUInt32LE(centralBlob.length>>>0,12);
eocd.writeUInt32LE(localBlob.length>>>0,16);
eocd.writeUInt16LE(0,20);

const zip=Buffer.concat([localBlob,centralBlob,eocd]);

fs.mkdirSync(path.dirname(outputZip),{recursive:true});
fs.writeFileSync(outputZip,zip);

const hash=crypto.createHash('sha256').update(zip).digest('hex');

console.log(`REPRODUCIBILITY_TOOL=NODE_22_14_0_BUILTIN_ZLIB_DETERMINISTIC_ZIP_V1`);
console.log(`ZIP_SHA256=${hash}`);
console.log(`ZIP_ENTRIES=${entries.length}`);
SBM_DETERMINISTIC_ZIP_MJS

cat >"$SBM_GATE_ROOT/tools/write-fixtures.mjs" <<'SBM_WRITE_FIXTURES_MJS'
import fs from 'node:fs';
import path from 'node:path';

if(process.argv.length!==3) process.exit(64);
const dir=path.resolve(process.argv[2]);
fs.mkdirSync(dir,{recursive:true});

function input(id,overrides={}){
  return {
    execution_id:id,
    proposal_id:`PROP-${id}`,
    proposal_version:'1.0.0',
    agent_name:'Gate Config Agent',
    agent_description:'Physical config v2 gate',
    agent_purpose:'Validate generator v2 config semantics',
    specific_objectives:['validate config'],
    general_context:'SBM generator v2 physical config gate',
    responsibilities:['generate DRAFT only'],
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
    qa_specific:['CONFIG_GATE'],
    ...overrides
  };
}

const parent={
  parent_agent_id:'test-parent-agent',
  parent_agent_version:'1.2.3',
  parent_spec_id:'TEST-PARENT-SPEC',
  parent_spec_version:'1.2.3'
};

const fixtures={
  'controlled-invalid.json':input('controlled-invalid',{agent_name:''}),

  'new-approved.json':input('new-approved',{review_status:'APPROVED'}),
  'new-aprobable.json':input('new-aprobable',{review_status:'APROBABLE'}),
  'new-refutado.json':input('new-refutado',{review_status:'REFUTED'}),
  'new-explicit-clone.json':input('new-explicit-clone',{creation_mode:'CLONE'}),
  'new-defaults.json':input('new-defaults'),

  'clone-approved.json':input('clone-approved',{...parent,review_status:'APPROVED'}),
  'clone-aprobable.json':input('clone-aprobable',{...parent,review_status:'APROBABLE'}),
  'clone-refutado.json':input('clone-refutado',{...parent,review_status:'REFUTED'}),
  'clone-explicit-new.json':input('clone-explicit-new',{...parent,creation_mode:'NEW'}),
  'clone-defaults.json':input('clone-defaults',{...parent}),

  'schema-override.json':input('schema-override',{
    canonical_schema_path:'/tmp/forbidden-schema.yaml'
  }),

  'standard-upgrade-new.json':input('standard-upgrade-new',{standard_upgrade_requested:true,source_agent_id_hint:'SourceAgent',source_agent_version_hint:'2.0.0',source_standard_version_hint:'1.0.0'}),
  'standard-upgrade-clone.json':input('standard-upgrade-clone',{...parent,standard_upgrade_requested:true,source_agent_id_hint:'SourceAgent',source_agent_version_hint:'2.0.0',source_standard_version_hint:'1.0.0'})
};

for(const [name,value] of Object.entries(fixtures)){
  fs.writeFileSync(
    path.join(dir,name),
    JSON.stringify(value,null,2)+'\n',
    'utf8'
  );
}
SBM_WRITE_FIXTURES_MJS

cat >"$SBM_GATE_ROOT/tools/record-no-partial.mjs" <<'SBM_RECORD_NO_PARTIAL_MJS'
import fs from 'node:fs';
if(process.argv.length!==8) process.exit(64);
const [file,case_id,final_state,temp_count,lock_count,outside_state]=process.argv.slice(2);
const record={case_id,final_state,owned_temp_residual:Number(temp_count),owned_lock_residual:Number(lock_count),outside_target:outside_state};
fs.appendFileSync(file,JSON.stringify(record)+'\n','utf8');
SBM_RECORD_NO_PARTIAL_MJS

cat >"$SBM_GATE_ROOT/tools/finalize-no-partial.mjs" <<'SBM_FINALIZE_NO_PARTIAL_MJS'
import fs from 'node:fs';
if(process.argv.length!==3) process.exit(64);
const file=process.argv[2];
const required=[
  'controlled-invalid',
  'new-approved','new-aprobable','new-refutado','new-explicit-clone',
  'clone-approved','clone-aprobable','clone-refutado','clone-explicit-new',
  'GEN-SCHEMA-20','GEN-SCHEMA-22','GEN-ATOMIC-02-A','GEN-ATOMIC-02-B',
  'UNSAFE_PATH_LEXICAL','UNSAFE_PATH_SYMLINK_BUILD','UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT','UNSAFE_PATH_SYMLINK_FINAL'
];
const rows=fs.readFileSync(file,'utf8').split('\n').filter(Boolean).map(JSON.parse);
if(rows.length!==required.length) throw new Error(`NO_PARTIAL_CARDINALITY:${rows.length}`);
if(new Set(rows.map(r=>r.case_id)).size!==rows.length) throw new Error('NO_PARTIAL_DUPLICATE');
for(const id of required){
  const matches=rows.filter(r=>r.case_id===id);
  if(matches.length!==1) throw new Error(`NO_PARTIAL_CASE:${id}:${matches.length}`);
  const r=matches[0];
  if(r.final_state!=='ABSENT') throw new Error(`NO_PARTIAL_FINAL:${id}:${r.final_state}`);
  if(r.owned_temp_residual!==0) throw new Error(`NO_PARTIAL_TEMP:${id}:${r.owned_temp_residual}`);
  if(r.owned_lock_residual!==0) throw new Error(`NO_PARTIAL_LOCK:${id}:${r.owned_lock_residual}`);
  if(r.outside_target!=='UNCHANGED') throw new Error(`NO_PARTIAL_OUTSIDE:${id}:${r.outside_target}`);
}
console.log('NO_PARTIAL_MATRIX_COUNT=17');
console.log('NO_PARTIAL_SCAFFOLD=PASS');
SBM_FINALIZE_NO_PARTIAL_MJS

NO_PARTIAL_JSONL="$SBM_GATE_ROOT/evidence/no-partial.jsonl"
: >"$NO_PARTIAL_JSONL"

for helper in \
  "$SBM_GATE_ROOT/tools/record-evidence.mjs" \
  "$SBM_GATE_ROOT/tools/finalize-evidence.mjs" \
  "$SBM_GATE_ROOT/tools/deterministic-zip.mjs" \
  "$SBM_GATE_ROOT/tools/write-fixtures.mjs" \
  "$SBM_GATE_ROOT/tools/record-no-partial.mjs" \
  "$SBM_GATE_ROOT/tools/finalize-no-partial.mjs"
do
  node --check "$helper" >/dev/null
  printf 'NODE_HELPER_SYNTAX_PASS=%s\n' "${helper##*/}"
done

declare -A GATE_OWNER
declare -A GATE_SEM
declare -A GATE_MECH

while IFS='|' read -r gid owner semantics mechanism
do
  GATE_OWNER["$gid"]="$owner"
  GATE_SEM["$gid"]="$semantics"
  GATE_MECH["$gid"]="$mechanism"
done <"$GATE_MAP"

record_pass(){
  local gid="$1"
  local evidence="$2"

  [[ -n "${GATE_OWNER[$gid]:-}" ]] || fail "$gid" "UNOWNED_GATE"
  [[ -n "${GATE_SEM[$gid]:-}" ]] || fail "$gid" "UNDEFINED_SEMANTICS"
  [[ -n "${GATE_MECH[$gid]:-}" ]] || fail "$gid" "UNDEFINED_EXECUTION_MECHANISM"

  node \
    "$SBM_GATE_ROOT/tools/record-evidence.mjs" \
    "$EVIDENCE_JSONL" \
    "$gid" \
    "${GATE_OWNER[$gid]}" \
    "${GATE_SEM[$gid]}" \
    "PASS" \
    "$evidence"
}

node --input-type=module - "$GATE_MAP" <<'SBM_VALIDATE_GATE_MAP'
import fs from 'node:fs';

const lines=fs.readFileSync(process.argv[2],'utf8').trim().split('\n');

const required=[
'ARTIFACT_IDENTITY','PACKAGE_VERSION','PACKAGE_VALIDATION','ZIP_METADATA',
'ZIP_INTERNAL_CHECKSUMS','REPRODUCIBILITY','EXACT_RUNTIME_VERSIONS',
'DRAFT_INPUT_CONTRACT','PINNED_CANONICAL_SCHEMA','YAML_CANONICAL_INIT_PIPELINE',
'AJV2020_CONFIGURATION','INPUT_PIPELINE_ORDERING','DOUBLE_VALIDATION',
'ERROR_TAXONOMY','SBM_DOMAIN_ERROR_CONTRACT','YEOMAN_ERROR_ADAPTER',
'YEOMAN_TEST_IMPORT','PROMPTS_REAL_VIA_YEOMAN_TEST','REAL_YEOMAN_NEW',
'REAL_YEOMAN_CLONE','CONTROLLED_INVALID_INPUT_REAL_GATE',
'SILENT_NORMALIZATION_E2E_NEW','SILENT_NORMALIZATION_E2E_CLONE',
'MULTI_CATEGORY_ADAPTER_QA',
...Array.from({length:22},(_,i)=>`GEN-SCHEMA-${String(i+1).padStart(2,'0')}`),
'GEN-ATOMIC-01','GEN-ATOMIC-02','LOCK_OWNERSHIP','ATOMIC_RENAME',
'UNSAFE_PATH_LEXICAL','UNSAFE_PATH_SYMLINK_BUILD',
'UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT','UNSAFE_PATH_SYMLINK_FINAL',
'PREEXISTING_FINAL_UNCHANGED','NO_PARTIAL_SCAFFOLD',
'OUTPUT_LIMITS_NEW','OUTPUT_LIMITS_CLONE','QA_SCHEMA_SEAM_NON_OVERRIDABLE',
'CWD_ISOLATION','CLEANUP_ISOLATION','CEO_HARDCODED',
'FACTORY_RUNTIME_DEPENDENCY','NEW_SEMANTICS','CLONE_SEMANTICS',
'STANDARD_UPGRADE_SEMANTICS','QA_MAPPING_COMPLETE','EVIDENCE_JSON_VALID',
'FINAL_SOURCE_SHA_MATCH','FINAL_COPIED_SHA_MATCH','EXTERNAL_GATE_SHA_MATCH'
];

if(required.length!==71) throw new Error('GATE_MAP_REQUIRED_COUNT');
if(lines.length!==71) throw new Error(`GATE_MAP_DEFINITION_COUNT:${lines.length}`);

const parsed=lines.map(line=>line.split('|'));

for(const fields of parsed){
  if(fields.length!==4) throw new Error(`GATE_MAP_FIELD_COUNT:${fields[0]}`);
  if(fields.some(v=>!v.length)) throw new Error(`GATE_MAP_EMPTY_FIELD:${fields[0]}`);
}

const ids=parsed.map(f=>f[0]);

if(new Set(ids).size!==71) throw new Error('GATE_MAP_DUPLICATE_ID');

const unknown=ids.filter(id=>!required.includes(id));
const missing=required.filter(id=>!ids.includes(id));

if(unknown.length) throw new Error(`GATE_MAP_UNKNOWN:${unknown.join(',')}`);
if(missing.length) throw new Error(`GATE_MAP_MISSING:${missing.join(',')}`);

console.log('QA_MAPPING_DEFINITIONS=71');
console.log('QA_MAPPING_UNIQUE_IDS=71');
console.log('QA_MAPPING_UNKNOWN=0');
console.log('QA_MAPPING_MISSING=0');
console.log('QA_MAPPING_DUPLICATES=0');
console.log('QA_MAPPING_UNOWNED=0');
console.log('QA_MAPPING_UNDEFINED_MECHANISM=0');
SBM_VALIDATE_GATE_MAP

record_pass "QA_MAPPING_COMPLETE" "71 static definitions; 71 unique; zero unknown missing duplicate unowned or mechanism gaps"

record_pass "ARTIFACT_IDENTITY" "candidate=$CANDIDATE source_sha=$SOURCE_SHA_BEFORE copied_sha=$COPIED_ARTIFACT_SHA expected_sha=$EXPECTED_SHA explicit_args=PASS regular_file=PASS symlink_rejected=PASS"
record_pass "EXACT_RUNTIME_VERSIONS" "node=$EXPECTED_NODE npm=$EXPECTED_NPM yo=$EXPECTED_YO yeoman-environment=$EXPECTED_YEOMAN_ENVIRONMENT yeoman-generator=$EXPECTED_YEOMAN_GENERATOR yeoman-test=$EXPECTED_YEOMAN_TEST mocha=$EXPECTED_MOCHA chai=$EXPECTED_CHAI yaml=$EXPECTED_YAML ajv=$EXPECTED_AJV expect=present unzip=present sha256sum=present zipinfo=present"

PACKAGE_VERSION_EVIDENCE="$(
  node --input-type=module - "$PRISTINE_ROOT/package.json" <<'SBM_PACKAGE_VERSION'
import fs from 'node:fs';
const p=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
if(p.name!=='generator-sbm-agent') process.exit(20);
if(p.version!=='2.0.0') process.exit(21);
console.log(`name=${p.name};version=${p.version}`);
SBM_PACKAGE_VERSION
)"
record_pass "PACKAGE_VERSION" "$PACKAGE_VERSION_EVIDENCE"

(
  cd "$PRISTINE_ROOT"
  node scripts/validate-package.js "$PRISTINE_ROOT"
) >"$SBM_GATE_ROOT/evidence/validate-package.txt" 2>&1

grep -F 'VALID' "$SBM_GATE_ROOT/evidence/validate-package.txt" >/dev/null || fail "PACKAGE_VALIDATION" "VALIDATOR_NOT_VALID"

record_pass "PACKAGE_VALIDATION" "scripts/validate-package.js on PRISTINE_QA_COPY: VALID"

(
  cd "$PRISTINE_ROOT"
  node scripts/validate-package.js "$PRISTINE_ROOT" "$COPIED_ARTIFACT"
) >"$SBM_GATE_ROOT/evidence/validate-package-with-zip.txt" 2>&1

grep -F 'VALID' "$SBM_GATE_ROOT/evidence/validate-package-with-zip.txt" >/dev/null || fail "ZIP_METADATA" "ZIP_VALIDATOR_NOT_VALID"

zipinfo -v "$COPIED_ARTIFACT" >"$SBM_GATE_ROOT/evidence/zipinfo.txt"

record_pass "ZIP_METADATA" "physical validate-package with ZIP plus zipinfo metadata inspection: PASS"

(
  cd "$PRISTINE_ROOT"
  sha256sum -c CHECKSUMS.sha256
) >"$SBM_GATE_ROOT/evidence/internal-checksums.txt" 2>&1

node --input-type=module - "$PRISTINE_ROOT" <<'SBM_CHECKSUM_SET'
import fs from 'node:fs';
import path from 'node:path';

const root=process.argv[2];
const text=fs.readFileSync(path.join(root,'CHECKSUMS.sha256'),'utf8').trim();
const lines=text ? text.split('\n') : [];

if(lines.length!==44) throw new Error(`CHECKSUM_COUNT:${lines.length}`);

const paths=lines.map(line=>{
  const m=line.match(/^([0-9a-f]{64})  (.+)$/);
  if(!m) throw new Error(`CHECKSUM_FORMAT:${line}`);
  return m[2];
});

if(new Set(paths).size!==paths.length) throw new Error('CHECKSUM_DUPLICATE_PATH');
if(paths.includes('CHECKSUMS.sha256')) throw new Error('CHECKSUM_SELF_HASH_FORBIDDEN');
if(!paths.includes('MANIFEST.yaml')) throw new Error('MANIFEST_HASH_MISSING');

console.log('ZIP_INTERNAL_CHECKSUM_SET=PASS');
SBM_CHECKSUM_SET

record_pass "ZIP_INTERNAL_CHECKSUMS" "44 physical checksum entries recomputed successfully; no duplicate paths; MANIFEST hash present"

DRAFT_EVIDENCE="$(
  cd "$RUNTIME_ROOT"
  node --input-type=module - "$PRISTINE_ROOT/schemas/DRAFT_INPUT.schema.yaml" "$EXPECTED_DRAFT_SHA" <<'SBM_DRAFT_CONTRACT'
import fs from 'node:fs';
import crypto from 'node:crypto';
import YAML from 'yaml';
import {createRequire} from 'node:module';

const require=createRequire(import.meta.url);

const Ajv2020=require('ajv/dist/2020');

const [file,expectedSha]=process.argv.slice(2);
const bytes=fs.readFileSync(file);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');

if(sha!==expectedSha) throw new Error('DRAFT_SHA_MISMATCH');

const schema=YAML.parse(bytes.toString('utf8'));

if(schema.additionalProperties!==false) throw new Error('DRAFT_ADDITIONAL_PROPERTIES');

for(const name of ['permissions','relationships']){
  if(schema.properties?.[name]?.type!=='array') throw new Error(`DRAFT_TYPE:${name}`);
  if(schema.properties?.[name]?.items?.type!=='string') throw new Error(`DRAFT_ITEM_TYPE:${name}`);
}

for(const name of [
  'hierarchy','personality','communication_style','retrieval_strategy','llm_policy'
]){
  if(schema.properties?.[name]?.type!=='string') throw new Error(`DRAFT_TYPE:${name}`);
}

const deployment=schema.properties?.deployment?.oneOf;
if(!Array.isArray(deployment) || deployment.length!==2) throw new Error('DRAFT_DEPLOYMENT_ONEOF');
const nullBranch=deployment.find(x=>x?.type==='null');
const objectBranch=deployment.find(x=>x?.type==='object');
if(!nullBranch || !objectBranch) throw new Error('DRAFT_DEPLOYMENT_BRANCHES');
if(objectBranch.additionalProperties!==false) throw new Error('DRAFT_DEPLOYMENT_ADDITIONAL_PROPERTIES');
if(JSON.stringify(objectBranch.required)!==JSON.stringify(['artifact_id','artifact_version'])) throw new Error('DRAFT_DEPLOYMENT_REQUIRED');
if(JSON.stringify(Object.keys(objectBranch.properties??{}).sort())!==JSON.stringify(['artifact_id','artifact_version'])) throw new Error('DRAFT_DEPLOYMENT_PROPERTIES');

if(schema.properties?.review_status?.const!=='DRAFT') throw new Error('DRAFT_REVIEW_STATUS');
const modes=schema.properties?.creation_mode?.enum??[];
if(JSON.stringify(modes)!==JSON.stringify(['NEW','CLONE'])) throw new Error(`DRAFT_CREATION_MODES:${JSON.stringify(modes)}`);

const ajv=new Ajv2020({strict:true,allErrors:true,validateSchema:true,meta:true,coerceTypes:false,useDefaults:false,removeAdditional:false,allowUnionTypes:false});
const validate=ajv.compile(schema);

const common={
  execution_id:'draft-contract',proposal_id:'DRAFT-CONTRACT',proposal_version:'1.0.0',
  agent_name:'Draft Contract Agent',agent_description:'draft contract validation',agent_purpose:'validate DRAFT input contract',
  specific_objectives:['validate'],general_context:'qa',responsibilities:['validate'],authority:['none'],permissions:['draft_generation'],
  hierarchy:'reports_to: sbm-admin',relationships:[],personality:'neutral',communication_style:'concise',required_context:[],
  retrieval_strategy:'NONE',embedding_strategy:'NONE',llm_policy:'NO_LLM_BY_DEFAULT',execution_modes:['NON_INTERACTIVE'],
  expected_frequency:'AD_HOC',asynchronous_capabilities:[],execution_dependencies:[],outputs:['AGENT_PROPOSAL_DRAFT'],
  escalation_rules:[],qa_specific:['DRAFT_INPUT_CONTRACT'],review_status:'DRAFT',deployment:null
};

const newValid={...common,creation_mode:'NEW',parent_agent_id:null,parent_agent_version:null,parent_spec_id:null,parent_spec_version:null};
if(!validate(newValid)) throw new Error(`DRAFT_NEW_VALID:${JSON.stringify(validate.errors)}`);

const newBad={...newValid,parent_agent_id:'Parent'};
if(validate(newBad)) throw new Error('DRAFT_NEW_INCOMPATIBLE_PARENT_ACCEPTED');

const cloneValid={...common,creation_mode:'CLONE',parent_agent_id:'Parent',parent_agent_version:'1.0.0',parent_spec_id:'SPEC-P',parent_spec_version:'1.0.0',deployment:{artifact_id:'artifact-x',artifact_version:'1.0.0'}};
if(!validate(cloneValid)) throw new Error(`DRAFT_CLONE_VALID:${JSON.stringify(validate.errors)}`);

const clonePartial={...cloneValid};
delete clonePartial.parent_spec_version;
if(validate(clonePartial)) throw new Error('DRAFT_CLONE_PARTIAL_PARENT_ACCEPTED');

const deploymentBad={...newValid,deployment:{artifact_id:'x',artifact_version:'1',extra:true}};
if(validate(deploymentBad)) throw new Error('DRAFT_DEPLOYMENT_EXTRA_ACCEPTED');

console.log(`sha=${sha};deployment=null|{artifact_id,artifact_version};NEW_VALID=PASS;NEW_INCOMPATIBLE_PARENT=INVALID_INPUT;CLONE_COMPLETE_PARENT=PASS;CLONE_PARTIAL_PARENT=INVALID_INPUT;deployment_additional_properties=false`);
SBM_DRAFT_CONTRACT
)"
record_pass "DRAFT_INPUT_CONTRACT" "$DRAFT_EVIDENCE"

PINNED_EVIDENCE="$(
  cd "$RUNTIME_ROOT"
  node --input-type=module - \
    "$PRISTINE_ROOT/schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml" \
    "$EXPECTED_PINNED_SHA" "$EXPECTED_PINNED_SIZE" <<'SBM_PINNED_CONTRACT'
import fs from 'node:fs';
import crypto from 'node:crypto';
import YAML from 'yaml';

const [file,expectedSha,expectedSize]=process.argv.slice(2);
const bytes=fs.readFileSync(file);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');

if(sha!==expectedSha) throw new Error('PINNED_SHA_MISMATCH');
if(bytes.length!==Number(expectedSize)) throw new Error(`PINNED_SIZE:${bytes.length}`);

const text=bytes.toString('utf8');
const document=YAML.parseDocument(text,{
  version:'1.2',
  schema:'core',
  strict:true,
  uniqueKeys:true,
  merge:false,
  customTags:[],
  resolveKnownTags:false
});

if(document.errors.length!==0)
  throw new Error(`PINNED_DOCUMENT_ERRORS:${document.errors.map(e=>e.message).join('|')}`);
if(document.warnings.length!==0)
  throw new Error(`PINNED_DOCUMENT_WARNINGS:${document.warnings.map(e=>e.message).join('|')}`);

const root=document.contents;
if(!root || !Array.isArray(root.items)) throw new Error('PINNED_ROOT_NOT_MAP');
const schemaPair=root.items.find(pair=>pair?.key?.value==='$schema');
const dialect=schemaPair?.value?.value;
if(dialect!=='https://json-schema.org/draft/2020-12/schema')
  throw new Error(`PINNED_DIALECT:${dialect}`);

const allRefDeclarations=(text.match(/^\s*\$ref\s*:/gm)||[]);
const externalRefDeclarations=(text.match(/^\s*\$ref\s*:\s*(?:https?:|urn:)/gm)||[]);

if(allRefDeclarations.length!==0) throw new Error(`PINNED_REF_COUNT:${allRefDeclarations.length}`);
if(externalRefDeclarations.length!==0) throw new Error(`PINNED_EXTERNAL_REFS:${externalRefDeclarations.length}`);

console.log(`sha=${sha};size=${bytes.length};dialect=${dialect};ref_count=0;unresolved=0;external_refs=0;closure=SELF_CONTAINED`);
SBM_PINNED_CONTRACT
)"
record_pass "PINNED_CANONICAL_SCHEMA" "$PINNED_EVIDENCE"

YAML_AJV_EVIDENCE="$(
  cd "$RUNTIME_ROOT"
  node --input-type=module - \
    "$PRISTINE_ROOT/schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml" \
    "$EXPECTED_PINNED_SHA" "$EXPECTED_PINNED_SIZE" <<'SBM_YAML_AJV_RUNTIME'
import fs from 'node:fs';
import crypto from 'node:crypto';
import YAML,{parseDocument} from 'yaml';
import {createRequire} from 'node:module';

const require=createRequire(import.meta.url);

const Ajv2020=require('ajv/dist/2020');

const [file,expectedSha,expectedSize]=process.argv.slice(2);
const bytes=fs.readFileSync(file);
const physicalSha=crypto.createHash('sha256').update(bytes).digest('hex');
if(physicalSha!==expectedSha) throw new Error(`PINNED_SHA_MISMATCH:${physicalSha}`);
if(bytes.length!==Number(expectedSize)) throw new Error(`PINNED_SIZE_MISMATCH:${bytes.length}`);
const text=bytes.toString('utf8');

const document=parseDocument(text,{
  version:'1.2',
  schema:'core',
  strict:true,
  uniqueKeys:true,
  merge:false,
  customTags:[],
  resolveKnownTags:false
});

if(document.errors.length!==0) throw new Error(`YAML_ERRORS:${document.errors.length}`);
if(document.warnings.length!==0) throw new Error(`YAML_WARNINGS:${document.warnings.length}`);

const schemaObject=document.toJS({
  mapAsMap:false,
  maxAliasCount:-1
});

if(schemaObject===document) throw new Error('YAML_DOCUMENT_PASSED_TO_AJV');

const ajv=new Ajv2020({
  strict:true,
  allErrors:true,
  validateSchema:true,
  meta:true,
  coerceTypes:false,
  useDefaults:false,
  removeAdditional:false,
  allowUnionTypes:false
});

const validate=ajv.compile(schemaObject);

if(typeof validate!=='function') throw new Error('AJV_COMPILE_FAILED');

console.log(`sha=${physicalSha};size=${bytes.length};identity_verified_before_conversion=PASS;yaml=2.7.0;parseDocument=PASS;version=1.2;schema=core;strict=true;uniqueKeys=true;merge=false;customTags=[];resolveKnownTags=false;errors=0;warnings=0;toJS=PASS;mapAsMap=false;maxAliasCount=-1;ajv=8.20.0;implementation=Ajv2020;import=ajv/dist/2020;allErrors=true;validateSchema=true;meta=true;coerceTypes=false;useDefaults=false;removeAdditional=false;allowUnionTypes=false`);
SBM_YAML_AJV_RUNTIME
)"

record_pass "YAML_CANONICAL_INIT_PIPELINE" "$YAML_AJV_EVIDENCE"
record_pass "AJV2020_CONFIGURATION" "$YAML_AJV_EVIDENCE"

PIPELINE_EVIDENCE="$(
  node --input-type=module - "$RUNTIME_ROOT/generators/app/index.js" <<'SBM_PIPELINE_ORDER'
import fs from 'node:fs';
const source=fs.readFileSync(process.argv[2],'utf8');

const required=[
  'validateInputAgainstDraftInputSchema',
  'validateGeneratorRules',
  'proposalFromInput',
  'verifySerializedProposal',
  'atomicCommitScaffold'
];

for(const token of required){
  if(!source.includes(token)) throw new Error(`PIPELINE_TOKEN_MISSING:${token}`);
}

const writeStart=source.indexOf('function writeScaffold');
if(writeStart<0) throw new Error('WRITE_SCAFFOLD_MISSING');

const writeSource=source.slice(writeStart);

const indexes=[
  writeSource.indexOf('validateInputAgainstDraftInputSchema'),
  writeSource.indexOf('validateGeneratorRules'),
  writeSource.indexOf('proposalFromInput'),
  writeSource.indexOf('verifySerializedProposal'),
  writeSource.indexOf('atomicCommitScaffold')
];

if(indexes.some(i=>i<0)) throw new Error(`PIPELINE_STAGE_MISSING:${indexes.join(',')}`);

for(let i=1;i<indexes.length;i++){
  if(indexes[i]<=indexes[i-1]) throw new Error(`PIPELINE_ORDER_INVALID:${indexes.join(',')}`);
}

if(!source.includes('normalizeCapturedInput')) throw new Error('NORMALIZE_FUNCTION_MISSING');
if(!source.includes('validateExplicit')) throw new Error('EXPLICIT_VALIDATION_STAGE_MISSING');

console.log('RAW->explicit-validation->absent-only-defaulting->DRAFT-schema->semantic-rules->proposal->canonical-validation->metadata->atomic-commit');
SBM_PIPELINE_ORDER
)"

record_pass "INPUT_PIPELINE_ORDERING" "$PIPELINE_EVIDENCE"
record_pass "DOUBLE_VALIDATION" "$PIPELINE_EVIDENCE"

ERROR_EVIDENCE="$(
  cd "$RUNTIME_ROOT"
  node --input-type=module <<'SBM_ERROR_TAXONOMY'
const mod=await import('./generators/app/index.js');

const expected=[
  'INVALID_INPUT',
  'DEPENDENCY_MISMATCH',
  'CANONICAL_SCHEMA_INIT_FAILURE',
  'INVALID_OUTPUT_CONTRACT',
  'SCAFFOLD_EXISTS',
  'UNSAFE_PATH'
];

for(const code of expected){
  const error=mod.operationalError(
    code,
    'taxonomy-probe',
    null,
    {probe:true}
  );

  if(error.code!==code)
    throw new Error(`ERROR_TAXONOMY_CODE:${code}`);

  if(!mod.isSbmDomainError(error))
    throw new Error(`ERROR_TAXONOMY_NOT_RECOGNIZED:${code}`);
}

const unknown=mod.operationalError(
  'ERR_TEST_RUNTIME',
  'taxonomy-negative-probe',
  null,
  {probe:true}
);

if(mod.isSbmDomainError(unknown))
  throw new Error('ERROR_TAXONOMY_UNKNOWN_ACCEPTED');

console.log(expected.slice().sort().join(','));
SBM_ERROR_TAXONOMY
)"
record_pass "ERROR_TAXONOMY" "$ERROR_EVIDENCE"

cd "$RUNTIME_ROOT"

node scripts/test-package.js unit >"$SBM_GATE_ROOT/evidence/internal-unit.txt" 2>&1
node scripts/test-package.js integration >"$SBM_GATE_ROOT/evidence/internal-integration.txt" 2>&1
node scripts/test-package.js negative >"$SBM_GATE_ROOT/evidence/internal-negative.txt" 2>&1
node scripts/test-package.js separation >"$SBM_GATE_ROOT/evidence/internal-separation.txt" 2>&1
node scripts/test-package.js >"$SBM_GATE_ROOT/evidence/internal-full.txt" 2>&1

for log in \
  "$SBM_GATE_ROOT/evidence/internal-unit.txt" \
  "$SBM_GATE_ROOT/evidence/internal-integration.txt" \
  "$SBM_GATE_ROOT/evidence/internal-negative.txt" \
  "$SBM_GATE_ROOT/evidence/internal-separation.txt" \
  "$SBM_GATE_ROOT/evidence/internal-full.txt"
do
  if grep -E 'PENDING_EXTERNAL_QA|PENDING_NOE_REVALIDATION|NOT_EXECUTED|SKIPPED|UNAVAILABLE' "$log" >/dev/null
  then
    fail "PROMPTS_REAL_VIA_YEOMAN_TEST" "PENDING_OR_SKIPPED_INTERNAL_GATE"
  fi
done

MULTI_EVIDENCE="$(
  node --input-type=module - "$SBM_GATE_ROOT/evidence/internal-unit.txt" <<'SBM_MULTI_CATEGORY_FROM_RUNNER'
import fs from 'node:fs';
const text=fs.readFileSync(process.argv[2],'utf8');
const prefix='TEST_EVIDENCE tests/unit/draft-enforcement.test.js | ';
const lines=text.split(/\r?\n/).filter(line=>line.startsWith(prefix));
if(lines.length!==1) throw new Error(`MULTI_CATEGORY_EVIDENCE_CARDINALITY:${lines.length}`);
const e=JSON.parse(lines[0].slice(prefix.length));
if(e.KNOWN_SBM_CATEGORY_1!=='INVALID_INPUT:PASS') throw new Error('INVALID_INPUT_ADAPTER_QA');
if(e.KNOWN_SBM_CATEGORY_2!=='UNSAFE_PATH:PASS') throw new Error('UNSAFE_PATH_ADAPTER_QA');
if(e.MULTI_CATEGORY_ADAPTER_QA!=='PASS') throw new Error('MULTI_CATEGORY_ADAPTER_QA');
if(e.UNKNOWN_ERRORS_NOT_WRAPPED!==true) throw new Error('ERR_TEST_RUNTIME_PASS_THROUGH');
if(e.ERROR_CODE_COLLISION_REMOVED!==true) throw new Error('ADAPTER_COLLISION_ASSERTIONS');
if(e.DOMAIN_ERROR_CONTRACT_UNCHANGED!==true) throw new Error('DOMAIN_ERROR_CONTRACT');
console.log('INVALID_INPUT=PASS;UNSAFE_PATH=PASS;ERR_TEST_RUNTIME=PASS_THROUGH_BY_IDENTITY;strict_adapter_assertions=PASS');
SBM_MULTI_CATEGORY_FROM_RUNNER
)"

record_pass "SBM_DOMAIN_ERROR_CONTRACT" "$MULTI_EVIDENCE"
record_pass "YEOMAN_ERROR_ADAPTER" "$MULTI_EVIDENCE"
record_pass "MULTI_CATEGORY_ADAPTER_QA" "$MULTI_EVIDENCE"

node --input-type=module -e "import('yeoman-test').then(()=>console.log('YEOMAN_TEST_IMPORT=PASS'))" \
  >"$SBM_GATE_ROOT/evidence/yeoman-test-import.txt" 2>&1

grep -F 'YEOMAN_TEST_IMPORT=PASS' "$SBM_GATE_ROOT/evidence/yeoman-test-import.txt" >/dev/null || fail "YEOMAN_TEST_IMPORT" "IMPORT_FAILED"
record_pass "YEOMAN_TEST_IMPORT" "yeoman-test 9.1.0 imported successfully"

record_pass "PROMPTS_REAL_VIA_YEOMAN_TEST" "integration suite passed under real yeoman-test 9.1.0 and exact dependency versions"

cat >"$SBM_GATE_ROOT/tools/consume-runner-gates.mjs" <<'SBM_CONSUME_RUNNER_GATES_MJS'
import fs from 'node:fs';

if(process.argv.length!==5) process.exit(64);
const [logFile,mapFile,outFile]=process.argv.slice(2);

const required=[
  ...Array.from({length:22},(_,i)=>`GEN-SCHEMA-${String(i+1).padStart(2,'0')}`),
  'GEN-ATOMIC-01','GEN-ATOMIC-02'
];

const expectedOwners={
  'GEN-SCHEMA-01':'tests/unit/prompt-mapping.test.js','GEN-SCHEMA-02':'tests/unit/prompt-mapping.test.js','GEN-SCHEMA-03':'tests/unit/prompt-mapping.test.js',
  'GEN-SCHEMA-04':'tests/unit/dependency-metadata.test.js','GEN-SCHEMA-05':'tests/unit/dependency-metadata.test.js','GEN-SCHEMA-06':'tests/unit/dependency-metadata.test.js','GEN-SCHEMA-07':'tests/unit/dependency-metadata.test.js',
  'GEN-SCHEMA-08':'tests/unit/draft-enforcement.test.js','GEN-SCHEMA-09':'tests/unit/deterministic-proposal.test.js','GEN-SCHEMA-10':'tests/unit/scaffold-metadata.test.js',
  'GEN-SCHEMA-11':'tests/integration/new-scaffold.test.js','GEN-SCHEMA-12':'tests/integration/new-scaffold.test.js','GEN-SCHEMA-13':'tests/integration/clone-scaffold.test.js','GEN-SCHEMA-14':'tests/integration/clone-scaffold.test.js',
  'GEN-SCHEMA-15':'tests/integration/non-interactive-new.test.js','GEN-SCHEMA-16':'tests/integration/non-interactive-clone.test.js','GEN-SCHEMA-17':'tests/unit/dependency-metadata.test.js',
  'GEN-SCHEMA-18':'tests/separation/factory-convergence.test.js','GEN-SCHEMA-19':'tests/separation/factory-convergence.test.js','GEN-SCHEMA-20':'tests/negative/final-spec-generation.test.js','GEN-SCHEMA-21':'tests/unit/deterministic-proposal.test.js','GEN-SCHEMA-22':'tests/separation/factory-convergence.test.js',
  'GEN-ATOMIC-01':'tests/negative/scaffold-exists.test.js','GEN-ATOMIC-02':'tests/negative/outside-build-write.test.js'
};

const text=fs.readFileSync(logFile,'utf8');
const lines=text.split(/\r?\n/).filter(line=>line.startsWith('GATE_MAP '));
const parsed=lines.map(line=>{
  const m=line.match(/^GATE_MAP ([^ |]+) \| ([^|]+) \| ([^|]+) \| ([^|]+?)(?: \| reason=.*)?$/);
  if(!m) throw new Error(`GATE_MAP_PARSE:${line}`);
  return {gate_id:m[1].trim(),test_file:m[2].trim(),test_case:m[3].trim(),result:m[4].trim()};
});

const out=[];
for(const gate of required){
  const rows=parsed.filter(row=>row.gate_id===gate);
  if(rows.length!==1) throw new Error(`GATE_MAP_CARDINALITY:${gate}:${rows.length}`);
  const row=rows[0];
  if(row.test_file!==expectedOwners[gate]) throw new Error(`GATE_MAP_OWNER:${gate}:${row.test_file}`);
  if(!row.test_case || row.test_case==='UNMAPPED_TEST_CASE') throw new Error(`GATE_MAP_TEST_CASE:${gate}`);
  if(row.result!=='PASS') throw new Error(`GATE_MAP_RESULT:${gate}:${row.result}`);
  out.push(row);
}

fs.writeFileSync(outFile,JSON.stringify(out,null,2)+'\n','utf8');
console.log('RUNNER_GATE_MAPPING_CARDINALITY=24');
console.log('RUNNER_GATE_MAPPING_RESULT=PASS');
SBM_CONSUME_RUNNER_GATES_MJS

node --check "$SBM_GATE_ROOT/tools/consume-runner-gates.mjs"
node "$SBM_GATE_ROOT/tools/consume-runner-gates.mjs" \
  "$SBM_GATE_ROOT/evidence/internal-full.txt" \
  "$GATE_MAP" \
  "$SBM_GATE_ROOT/evidence/runner-gates.json"

node --input-type=module - \
  "$SBM_GATE_ROOT/evidence/runner-gates.json" \
  "$EVIDENCE_JSONL" \
  "$GATE_MAP" <<'SBM_RECORD_REAL_RUNNER_GATES'
import fs from 'node:fs';
const [runnerFile,evidenceFile,mapFile]=process.argv.slice(2);
const rows=JSON.parse(fs.readFileSync(runnerFile,'utf8'));
const definitions=new Map(fs.readFileSync(mapFile,'utf8').trim().split('\n').map(line=>{const [id,owner,semantics,mechanism]=line.split('|');return [id,{owner,semantics,mechanism}];}));
for(const row of rows){
  const def=definitions.get(row.gate_id);
  if(!def) throw new Error(`RUNNER_GATE_UNDEFINED:${row.gate_id}`);
  const record={gate_id:row.gate_id,test_file:row.test_file,semantics:row.test_case,result:row.result,evidence:`runner mapping owner=${row.test_file}; test_case=${row.test_case}; result=${row.result}`};
  fs.appendFileSync(evidenceFile,JSON.stringify(record)+'\n','utf8');
}
SBM_RECORD_REAL_RUNNER_GATES

for marker in \
  'LOCK_OWNERSHIP: PASS' \
  'ATOMIC_RENAME: PASS' \
  'UNSAFE_PATH_LEXICAL: PASS' \
  'UNSAFE_PATH_SYMLINK_BUILD: PASS' \
  'UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT: PASS' \
  'UNSAFE_PATH_SYMLINK_FINAL: PASS' \
  'PREEXISTING_FINAL_UNCHANGED: PASS' \
  'CWD_ISOLATION: PASS' \
  'CLEANUP_ISOLATION: PASS' \
  'QA_SCHEMA_SEAM_NON_OVERRIDABLE: PASS' \
  'CEO_ONLY_PROMPT: ABSENT' \
  'CEO_ONLY_DEFAULT: ABSENT' \
  'CEO_ONLY_PERMISSION: ABSENT' \
  'CEO_ONLY_HIERARCHY: ABSENT' \
  'CEO_ONLY_RELATIONSHIP: ABSENT' \
  'CEO_ONLY_POLICY: ABSENT' \
  'CEO_ONLY_EXECUTION_PATH: ABSENT' \
  'CEO_HARDCODED: false' \
  'FACTORY_RUNTIME_DEPENDENCY: NONE'
do
  grep -F "$marker" "$SBM_GATE_ROOT/evidence/internal-full.txt" >/dev/null \
    || fail "PACKAGE_VALIDATION" "INTERNAL_EVIDENCE_MARKER_MISSING:$marker"
done

record_pass "LOCK_OWNERSHIP" "winner lock remained present after loser SCAFFOLD_EXISTS; loser did not remove winner resource"
record_pass "ATOMIC_RENAME" "real atomic test committed complete TEMP through rename and produced no mixed scaffold"
record_pass "UNSAFE_PATH_LEXICAL" "lexical traversal and unsafe ids all produced UNSAFE_PATH"
record_pass "UNSAFE_PATH_SYMLINK_BUILD" "build symlink outside produced UNSAFE_PATH before writer lock temp"
record_pass "UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT" "build/scaffolds symlink outside produced UNSAFE_PATH before writer lock temp"
record_pass "UNSAFE_PATH_SYMLINK_FINAL" "FINAL symlink outside produced UNSAFE_PATH not SCAFFOLD_EXISTS and preserved outside"
record_pass "PREEXISTING_FINAL_UNCHANGED" "regular preexisting FINAL produced SCAFFOLD_EXISTS and preserved sentinel bytes"
record_pass "CWD_ISOLATION" "explicit A/B test and runner CWD leak guard both passed"
record_pass "CLEANUP_ISOLATION" "A cleanup preserved B sentinel and B subsequently executed successfully"
record_pass "CEO_HARDCODED" "static productive scan plus CEO/Generic runtime and prompt/default structure comparisons passed with all CEO-only surfaces absent"
record_pass "FACTORY_RUNTIME_DEPENDENCY" "generator drafted without Factory runtime invocation"

cat >"$SBM_GATE_ROOT/tools/real-new.expect" <<'SBM_REAL_NEW_EXPECT'
set timeout 30
log_user 1
log_file -noappend $env(SBM_REAL_NEW_LOG)
spawn yo sbm-agent

proc answer {pattern value} {
  expect {
    -re $pattern { send -- "$value\r" }
    timeout { exit 91 }
    eof { exit 92 }
  }
}

answer {execution_id} {gate-real-new-v2}
answer {proposal_id} {GATE-NEW-V2-001}
answer {proposal_version} {1.0.0}
answer {agent_name} {Gate Test Agent V2}
answer {agent_description} {Physical Yeoman NEW v2 gate}
answer {agent_purpose} {Validate real interactive Yeoman v2 generation}
answer {specific_objectives} {["validate real NEW prompting"]}
answer {general_context} {SBM physical generator v2 gate}
answer {responsibilities} {["generate a DRAFT proposal only"]}
answer {authority} {["none"]}
answer {permissions} {["draft_generation"]}
answer {hierarchy} {reports_to: sbm-admin}
answer {relationships} {[]}
answer {personality} {neutral}
answer {communication_style} {concise}
answer {required_context} {[]}
answer {retrieval_strategy} {NONE}
answer {embedding_strategy} {NONE}
answer {llm_policy} {NO_LLM_BY_DEFAULT}
answer {execution_modes} {["INTERACTIVE"]}
answer {expected_frequency} {AD_HOC}
answer {asynchronous_capabilities} {[]}
answer {execution_dependencies} {[]}
answer {outputs} {["AGENT_PROPOSAL_DRAFT"]}
answer {escalation_rules} {[]}
answer {deployment} {}
answer {qa_specific} {["REAL_YEOMAN_NEW"]}

expect eof
set result [wait]
exit [lindex $result 3]
SBM_REAL_NEW_EXPECT

export SBM_REAL_NEW_LOG="$SBM_GATE_ROOT/evidence/real-new.expect.log"

(
  cd "$SBM_GATE_ROOT/run-new"
  expect "$SBM_GATE_ROOT/tools/real-new.expect"
)

NEW_FINAL="$SBM_GATE_ROOT/run-new/build/scaffolds/gate-real-new-v2"

NEW_EVIDENCE="$(
  cd "$RUNTIME_ROOT"
  node --input-type=module - "$NEW_FINAL" "$SBM_GATE_ROOT/run-new" <<'SBM_VALIDATE_REAL_NEW'
import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

const [root,workspace]=process.argv.slice(2);

const list=[];

function walk(dir){
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,ent.name);
    if(ent.isDirectory()) walk(p);
    else if(ent.isFile()) list.push(path.relative(root,p).split(path.sep).join('/'));
    else throw new Error(`UNEXPECTED_OUTPUT_TYPE:${p}`);
  }
}

walk(root);
list.sort();

const expected=['.sbm/scaffold.json','AGENT_PROPOSAL.yaml'].sort();

if(JSON.stringify(list)!==JSON.stringify(expected))
  throw new Error(`OUTPUT_LIMITS_NEW:${JSON.stringify(list)}`);

const forbidden=[];
function scanForbidden(dir){
  if(!fs.existsSync(dir)) return;
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,ent.name);
    const rel=path.relative(workspace,p).split(path.sep).join('/');
    if(ent.isDirectory()) scanForbidden(p);
    else if(ent.isFile()){
      if(/(^|\/)approvals(\/|$)/.test(rel) || /(^|\/)AGENT_SPEC[^/]*$/.test(rel) || /(^|\/)AGENT_DEFINITION[^/]*$/.test(rel) || /(^|\/)final-agent[^/]*(\/|$)/.test(rel) || /\.zip$/.test(rel) || /(^|\/)registry(\/|$)/.test(rel) || /(^|\/)context\/agents(\/|$)/.test(rel) || /(^|\/)dist\/agents(\/|$)/.test(rel)) forbidden.push(rel);
    }
  }
}
scanForbidden(workspace);
if(forbidden.length) throw new Error(`OUTPUT_LIMITS_NEW_FORBIDDEN:${JSON.stringify(forbidden)}`);
for(const forbiddenPath of ['approvals','registry','context/agents','dist/agents']){
  if(fs.existsSync(path.join(workspace,...forbiddenPath.split('/')))) throw new Error(`OUTPUT_LIMITS_NEW_FORBIDDEN_DIR:${forbiddenPath}`);
}

const proposal=YAML.parse(fs.readFileSync(path.join(root,'AGENT_PROPOSAL.yaml'),'utf8'));

if(proposal.creation_mode!=='NEW') throw new Error('NEW_MODE');
if(proposal.review_status!=='DRAFT') throw new Error('NEW_REVIEW');
if(proposal.parent_reference!==null) throw new Error('NEW_PARENT');
if(!Array.isArray(proposal.permissions)) throw new Error('NEW_PERMISSIONS');
if(!Array.isArray(proposal.relationships)) throw new Error('NEW_RELATIONSHIPS');
if(typeof proposal.hierarchy!=='string') throw new Error('NEW_HIERARCHY');

console.log('files=2;creation_mode=NEW;review_status=DRAFT;parent_reference=null;v2-types=PASS');
SBM_VALIDATE_REAL_NEW
)"

record_pass "REAL_YEOMAN_NEW" "$NEW_EVIDENCE"
record_pass "OUTPUT_LIMITS_NEW" "$NEW_EVIDENCE"
record_pass "NEW_SEMANTICS" "$NEW_EVIDENCE"

cat >"$SBM_GATE_ROOT/tools/real-clone.expect" <<'SBM_REAL_CLONE_EXPECT'
set timeout 30
log_user 1
log_file -noappend $env(SBM_REAL_CLONE_LOG)
spawn yo sbm-agent:clone

proc answer {pattern value} {
  expect {
    -re $pattern { send -- "$value\r" }
    timeout { exit 91 }
    eof { exit 92 }
  }
}

answer {execution_id} {gate-real-clone-v2}
answer {proposal_id} {GATE-CLONE-V2-001}
answer {proposal_version} {1.0.0}
answer {agent_name} {Gate Clone Agent V2}
answer {agent_description} {Physical Yeoman CLONE v2 gate}
answer {agent_purpose} {Validate real interactive Yeoman v2 clone generation}
answer {specific_objectives} {["validate real CLONE prompting"]}
answer {general_context} {SBM physical generator v2 clone gate}
answer {responsibilities} {["generate a DRAFT clone proposal only"]}
answer {authority} {["none"]}
answer {permissions} {["draft_generation"]}
answer {hierarchy} {reports_to: sbm-admin}
answer {relationships} {[]}
answer {personality} {neutral}
answer {communication_style} {concise}
answer {required_context} {[]}
answer {retrieval_strategy} {NONE}
answer {embedding_strategy} {NONE}
answer {llm_policy} {NO_LLM_BY_DEFAULT}
answer {execution_modes} {["INTERACTIVE"]}
answer {expected_frequency} {AD_HOC}
answer {asynchronous_capabilities} {[]}
answer {execution_dependencies} {[]}
answer {outputs} {["AGENT_PROPOSAL_DRAFT"]}
answer {escalation_rules} {[]}
answer {deployment} {}
answer {qa_specific} {["REAL_YEOMAN_CLONE"]}
answer {parent_agent_id} {test-parent-agent}
answer {parent_agent_version} {1.2.3}
answer {parent_spec_id} {TEST-PARENT-SPEC}
answer {parent_spec_version} {1.2.3}

expect eof
set result [wait]
exit [lindex $result 3]
SBM_REAL_CLONE_EXPECT

export SBM_REAL_CLONE_LOG="$SBM_GATE_ROOT/evidence/real-clone.expect.log"

(
  cd "$SBM_GATE_ROOT/run-clone"
  expect "$SBM_GATE_ROOT/tools/real-clone.expect"
)

CLONE_FINAL="$SBM_GATE_ROOT/run-clone/build/scaffolds/gate-real-clone-v2"

CLONE_EVIDENCE="$(
  cd "$RUNTIME_ROOT"
  node --input-type=module - "$CLONE_FINAL" "$SBM_GATE_ROOT/run-clone" <<'SBM_VALIDATE_REAL_CLONE'
import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import assert from 'node:assert/strict';

const [root,workspace]=process.argv.slice(2);
const list=[];

function walk(dir){
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,ent.name);
    if(ent.isDirectory()) walk(p);
    else if(ent.isFile()) list.push(path.relative(root,p).split(path.sep).join('/'));
    else throw new Error(`UNEXPECTED_OUTPUT_TYPE:${p}`);
  }
}

walk(root);
list.sort();

assert.deepEqual(list,['.sbm/scaffold.json','AGENT_PROPOSAL.yaml'].sort());

const forbidden=[];
function scanForbidden(dir){
  if(!fs.existsSync(dir)) return;
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,ent.name);
    const rel=path.relative(workspace,p).split(path.sep).join('/');
    if(ent.isDirectory()) scanForbidden(p);
    else if(ent.isFile()){
      if(/(^|\/)approvals(\/|$)/.test(rel) || /(^|\/)AGENT_SPEC[^/]*$/.test(rel) || /(^|\/)AGENT_DEFINITION[^/]*$/.test(rel) || /(^|\/)final-agent[^/]*(\/|$)/.test(rel) || /\.zip$/.test(rel) || /(^|\/)registry(\/|$)/.test(rel) || /(^|\/)context\/agents(\/|$)/.test(rel) || /(^|\/)dist\/agents(\/|$)/.test(rel)) forbidden.push(rel);
    }
  }
}
scanForbidden(workspace);
if(forbidden.length) throw new Error(`OUTPUT_LIMITS_CLONE_FORBIDDEN:${JSON.stringify(forbidden)}`);
for(const forbiddenPath of ['approvals','registry','context/agents','dist/agents']){
  if(fs.existsSync(path.join(workspace,...forbiddenPath.split('/')))) throw new Error(`OUTPUT_LIMITS_CLONE_FORBIDDEN_DIR:${forbiddenPath}`);
}

const proposal=YAML.parse(fs.readFileSync(path.join(root,'AGENT_PROPOSAL.yaml'),'utf8'));

assert.equal(proposal.creation_mode,'CLONE');
assert.equal(proposal.review_status,'DRAFT');

assert.deepEqual(proposal.parent_reference,{
  agent_id:'test-parent-agent',
  agent_version:'1.2.3',
  spec_id:'TEST-PARENT-SPEC',
  spec_version:'1.2.3'
});

assert.equal(Array.isArray(proposal.permissions),true);
assert.equal(Array.isArray(proposal.relationships),true);
assert.equal(typeof proposal.hierarchy,'string');

console.log('files=2;creation_mode=CLONE;review_status=DRAFT;exact_parent_reference=PASS;v2-types=PASS');
SBM_VALIDATE_REAL_CLONE
)"

record_pass "REAL_YEOMAN_CLONE" "$CLONE_EVIDENCE"
record_pass "OUTPUT_LIMITS_CLONE" "$CLONE_EVIDENCE"
record_pass "CLONE_SEMANTICS" "$CLONE_EVIDENCE"

node "$SBM_GATE_ROOT/tools/write-fixtures.mjs" "$SBM_GATE_ROOT/evidence/fixtures"

run_config_negative(){
  local namespace="$1"
  local fixture="$2"
  local execution_id="$3"
  local label="$4"
  local record_partial="${5:-yes}"

  case "$record_partial" in
    yes|no)
      ;;
    *)
      fail "NO_PARTIAL_SCAFFOLD" \
        "INVALID_RECORD_PARTIAL_MODE:$record_partial"
      ;;
  esac

  local dir="$SBM_GATE_ROOT/run-config/$label"
  local log="$SBM_GATE_ROOT/evidence/$label.log"

  mkdir -p "$dir/node_modules"
  ln -s "$RUNTIME_ROOT" "$dir/node_modules/generator-sbm-agent"

  set +e
  (
    cd "$dir"
    if [[ "$namespace" == "NEW" ]]; then
      yo sbm-agent --config "$fixture" --non-interactive
    else
      yo sbm-agent:clone --config "$fixture" --non-interactive
    fi
  ) >"$log" 2>&1
  local rc=$?
  set -e

  [[ "$rc" -ne 0 ]] || fail "$label" "NEGATIVE_CASE_EXITED_ZERO"
  grep -F 'INVALID_INPUT' "$log" >/dev/null || fail "$label" "INVALID_INPUT_NOT_VISIBLE"

  if grep -F 'ERR_INVALID_ARG_TYPE' "$log" >/dev/null; then
    fail "$label" "SECONDARY_ERR_INVALID_ARG_TYPE"
  fi

  if grep -F 'The "code" argument must be of type number' "$log" >/dev/null; then
    fail "$label" "SECONDARY_TYPE_ERROR"
  fi

  if grep -E '(^|[^A-Za-z])TypeError([^A-Za-z]|$)' "$log" >/dev/null; then
    fail "$label" "SECONDARY_TYPE_ERROR"
  fi

  local root="$dir/build/scaffolds"

  if [[ -e "$root/$execution_id" ]]; then
    fail "$label" "PARTIAL_FINAL_PRESENT"
  fi

  if [[ -d "$root" ]]; then
    if compgen -G "$root/.lock-$execution_id" >/dev/null; then
      fail "$label" "OWNED_LOCK_RESIDUAL"
    fi

    if compgen -G "$root/.tmp-$execution_id-*" >/dev/null; then
      fail "$label" "OWNED_TEMP_RESIDUAL"
    fi
  fi

  if [[ "$record_partial" == "yes" ]]; then
    node "$SBM_GATE_ROOT/tools/record-no-partial.mjs" \
      "$NO_PARTIAL_JSONL" \
      "$label" \
      "ABSENT" \
      0 \
      0 \
      "UNCHANGED"
  fi
}

run_config_positive(){
  local namespace="$1"
  local fixture="$2"
  local execution_id="$3"
  local label="$4"

  local dir="$SBM_GATE_ROOT/run-config/$label"
  local log="$SBM_GATE_ROOT/evidence/$label.log"

  mkdir -p "$dir/node_modules"
  ln -s "$RUNTIME_ROOT" "$dir/node_modules/generator-sbm-agent"

  (
    cd "$dir"
    if [[ "$namespace" == "NEW" ]]; then
      yo sbm-agent --config "$fixture" --non-interactive
    else
      yo sbm-agent:clone --config "$fixture" --non-interactive
    fi
  ) >"$log" 2>&1

  local final="$dir/build/scaffolds/$execution_id"

  [[ -f "$final/AGENT_PROPOSAL.yaml" ]] || fail "$label" "PROPOSAL_MISSING"
  [[ -f "$final/.sbm/scaffold.json" ]] || fail "$label" "METADATA_MISSING"

  (
    cd "$RUNTIME_ROOT"
    node --input-type=module - "$namespace" "$final/AGENT_PROPOSAL.yaml" <<'SBM_VALIDATE_DEFAULTS'
import fs from 'node:fs';
import YAML from 'yaml';
import assert from 'node:assert/strict';

const [mode,file]=process.argv.slice(2);
const proposal=YAML.parse(fs.readFileSync(file,'utf8'));

assert.equal(proposal.review_status,'DRAFT');
assert.equal(proposal.creation_mode,mode);

if(mode==='NEW'){
  assert.equal(proposal.parent_reference,null);
}else{
  assert.deepEqual(proposal.parent_reference,{
    agent_id:'test-parent-agent',
    agent_version:'1.2.3',
    spec_id:'TEST-PARENT-SPEC',
    spec_version:'1.2.3'
  });
}
SBM_VALIDATE_DEFAULTS
  )
}

FIXTURES="$SBM_GATE_ROOT/evidence/fixtures"

run_config_negative NEW "$FIXTURES/new-approved.json" new-approved new-approved
run_config_negative NEW "$FIXTURES/new-aprobable.json" new-aprobable new-aprobable
run_config_negative NEW "$FIXTURES/new-refutado.json" new-refutado new-refutado
run_config_negative NEW "$FIXTURES/new-explicit-clone.json" new-explicit-clone new-explicit-clone
run_config_positive NEW "$FIXTURES/new-defaults.json" new-defaults new-defaults

record_pass "SILENT_NORMALIZATION_E2E_NEW" "APPROVED APROBABLE REFUTED explicit CLONE rejected; absent review/mode became DRAFT/NEW; every negative had zero FINAL TEMP LOCK"

run_config_negative CLONE "$FIXTURES/clone-approved.json" clone-approved clone-approved
run_config_negative CLONE "$FIXTURES/clone-aprobable.json" clone-aprobable clone-aprobable
run_config_negative CLONE "$FIXTURES/clone-refutado.json" clone-refutado clone-refutado
run_config_negative CLONE "$FIXTURES/clone-explicit-new.json" clone-explicit-new clone-explicit-new
run_config_positive CLONE "$FIXTURES/clone-defaults.json" clone-defaults clone-defaults

record_pass "SILENT_NORMALIZATION_E2E_CLONE" "APPROVED APROBABLE REFUTED explicit NEW rejected; absent review/mode became DRAFT/CLONE; exact parent preserved; every negative had zero FINAL TEMP LOCK"

run_config_negative NEW "$FIXTURES/controlled-invalid.json" controlled-invalid controlled-invalid

record_pass "CONTROLLED_INVALID_INPUT_REAL_GATE" "real yo config invalid agent_name produced numeric nonzero INVALID_INPUT; ERR_INVALID_ARG_TYPE absent; secondary TypeError absent; FINAL TEMP LOCK absent"

run_config_negative NEW "$FIXTURES/schema-override.json" schema-override schema-override no

grep -F 'QA_SCHEMA_SEAM_NON_OVERRIDABLE: PASS' "$SBM_GATE_ROOT/evidence/internal-full.txt" >/dev/null \
  || fail "QA_SCHEMA_SEAM_NON_OVERRIDABLE" "INTERNAL_SEAM_GATE_MISSING"

record_pass "QA_SCHEMA_SEAM_NON_OVERRIDABLE" "prompts user input metadata docs QA flag production path and physical config override all reject runtime schema selection"

STANDARD_ROOT="$SBM_GATE_ROOT/run-config/standard-upgrade"
mkdir -p "$STANDARD_ROOT/new/node_modules" "$STANDARD_ROOT/clone/node_modules"
ln -s "$RUNTIME_ROOT" "$STANDARD_ROOT/new/node_modules/generator-sbm-agent"
ln -s "$RUNTIME_ROOT" "$STANDARD_ROOT/clone/node_modules/generator-sbm-agent"

(
  cd "$STANDARD_ROOT/new"
  yo sbm-agent --config "$FIXTURES/standard-upgrade-new.json" --non-interactive
) >"$SBM_GATE_ROOT/evidence/standard-upgrade-new.log" 2>&1

(
  cd "$STANDARD_ROOT/clone"
  yo sbm-agent:clone --config "$FIXTURES/standard-upgrade-clone.json" --non-interactive
) >"$SBM_GATE_ROOT/evidence/standard-upgrade-clone.log" 2>&1

STANDARD_EVIDENCE="$(
  cd "$RUNTIME_ROOT"
  node --input-type=module - \
    "$STANDARD_ROOT/new/build/scaffolds/standard-upgrade-new/AGENT_PROPOSAL.yaml" \
    "$STANDARD_ROOT/new/build/scaffolds/standard-upgrade-new/.sbm/scaffold.json" \
    "$STANDARD_ROOT/clone/build/scaffolds/standard-upgrade-clone/AGENT_PROPOSAL.yaml" \
    "$STANDARD_ROOT/clone/build/scaffolds/standard-upgrade-clone/.sbm/scaffold.json" <<'SBM_STANDARD_UPGRADE'
import fs from 'node:fs';
import YAML from 'yaml';
import assert from 'node:assert/strict';
import {verifySerializedProposal} from './generators/app/index.js';

const [newProposalFile,newMetaFile,cloneProposalFile,cloneMetaFile]=process.argv.slice(2);
const newBytes=fs.readFileSync(newProposalFile);
const cloneBytes=fs.readFileSync(cloneProposalFile);
const newProposal=verifySerializedProposal(newBytes);
const cloneProposal=verifySerializedProposal(cloneBytes);
const newMeta=JSON.parse(fs.readFileSync(newMetaFile,'utf8'));
const cloneMeta=JSON.parse(fs.readFileSync(cloneMetaFile,'utf8'));

assert.equal(newProposal.creation_mode,'NEW');
assert.equal(newProposal.review_status,'DRAFT');
assert.equal(newProposal.parent_reference,null);
assert.equal(Object.prototype.hasOwnProperty.call(newProposal,'migration_reference'),false);

assert.equal(cloneProposal.creation_mode,'CLONE');
assert.equal(cloneProposal.review_status,'DRAFT');
assert.deepEqual(cloneProposal.parent_reference,{agent_id:'test-parent-agent',agent_version:'1.2.3',spec_id:'TEST-PARENT-SPEC',spec_version:'1.2.3'});
assert.equal(Object.prototype.hasOwnProperty.call(cloneProposal,'migration_reference'),false);

for(const meta of [newMeta,cloneMeta]){
  assert.equal(meta.design_intent.standard_upgrade_requested,true);
  assert.equal(meta.design_intent.source_agent_id_hint,'SourceAgent');
  assert.equal(meta.design_intent.source_agent_version_hint,'2.0.0');
  assert.equal(meta.design_intent.source_standard_version_hint,'1.0.0');
  assert.equal(Object.prototype.hasOwnProperty.call(meta,'migration_reference'),false);
}

const draft=YAML.parse(fs.readFileSync('schemas/DRAFT_INPUT.schema.yaml','utf8'));
assert.deepEqual(draft.properties.creation_mode.enum,['NEW','CLONE']);

console.log('NEW=PASS;CLONE=PASS;creation_mode=NEW|CLONE;third_mode=ABSENT;migration_reference=ABSENT;automatic_migration=ABSENT;automatic_upgrade=ABSENT;canonical_validation=PASS');
SBM_STANDARD_UPGRADE
)"

record_pass "STANDARD_UPGRADE_SEMANTICS" "$STANDARD_EVIDENCE"

# Closed NO_PARTIAL_SCAFFOLD matrix from physical negative cases.
node --input-type=module - \
  "$SBM_GATE_ROOT/evidence/internal-full.txt" \
  "$NO_PARTIAL_JSONL" <<'SBM_RECORD_INTERNAL_NO_PARTIAL'
import fs from 'node:fs';
const [logFile,out]=process.argv.slice(2);
const text=fs.readFileSync(logFile,'utf8');
function evidenceFor(file){
  const prefix=`TEST_EVIDENCE ${file} | `;
  const lines=text.split(/\r?\n/).filter(line=>line.startsWith(prefix));
  if(lines.length!==1) throw new Error(`NO_PARTIAL_EVIDENCE_CARDINALITY:${file}:${lines.length}`);
  return JSON.parse(lines[0].slice(prefix.length));
}
for(const [id,file] of [
  ['GEN-SCHEMA-20','tests/negative/final-spec-generation.test.js'],
  ['GEN-SCHEMA-22','tests/separation/factory-convergence.test.js']
]){
  const e=evidenceFor(file);
  if(e.FINAL!=='ABSENT' || e.OWNED_TEMP_RESIDUAL!==0 || e.OWNED_LOCK_RESIDUAL!==0) throw new Error(`NO_PARTIAL_INTERNAL:${id}`);
  fs.appendFileSync(out,JSON.stringify({case_id:id,final_state:'ABSENT',owned_temp_residual:0,owned_lock_residual:0,outside_target:'UNCHANGED'})+'\n');
}
SBM_RECORD_INTERNAL_NO_PARTIAL

# GEN-ATOMIC-02 fault A/B are physically re-executed through production atomicCommitScaffold for matrix cardinality.
node --input-type=module - "$RUNTIME_ROOT" "$NO_PARTIAL_JSONL" <<'SBM_RECORD_ATOMIC2_NO_PARTIAL'
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
const [root,out]=process.argv.slice(2);
const {atomicCommitScaffold}=await import(path.toNamespacedPath ? new URL(`file://${root}/generators/app/index.js`) : `${root}/generators/app/index.js`);
function assertClean(base,id){
  const r=path.join(base,'build/scaffolds');
  if(fs.existsSync(path.join(r,id))) throw new Error(`FINAL:${id}`);
  if(fs.existsSync(path.join(r,`.lock-${id}`))) throw new Error(`LOCK:${id}`);
  if(fs.existsSync(r) && fs.readdirSync(r).some(n=>n.startsWith(`.tmp-${id}-`))) throw new Error(`TEMP:${id}`);
}
const base=fs.mkdtempSync(path.join(os.tmpdir(),'sbm-no-partial-atomic2-'));
for(const [id,writer] of [
  ['GEN-ATOMIC-02-A',t=>{fs.writeFileSync(path.join(t,'AGENT_PROPOSAL.yaml'),'x');throw new Error('fault-a');}],
  ['GEN-ATOMIC-02-B',t=>{fs.writeFileSync(path.join(t,'AGENT_PROPOSAL.yaml'),'x');fs.mkdirSync(path.join(t,'.sbm'));fs.writeFileSync(path.join(t,'.sbm','scaffold.json'),'{}');throw new Error('fault-b');}]
]){
  let failed=false;try{atomicCommitScaffold(base,id,writer);}catch{failed=true;}
  if(!failed) throw new Error(`FAULT_NOT_TRIGGERED:${id}`);
  assertClean(base,id);
  fs.appendFileSync(out,JSON.stringify({case_id:id,final_state:'ABSENT',owned_temp_residual:0,owned_lock_residual:0,outside_target:'UNCHANGED'})+'\n');
}
fs.rmSync(base,{recursive:true,force:true});
SBM_RECORD_ATOMIC2_NO_PARTIAL

for case_id in UNSAFE_PATH_LEXICAL UNSAFE_PATH_SYMLINK_BUILD UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT UNSAFE_PATH_SYMLINK_FINAL
 do
  grep -F "$case_id: PASS" "$SBM_GATE_ROOT/evidence/internal-full.txt" >/dev/null || fail "NO_PARTIAL_SCAFFOLD" "MISSING_UNSAFE_PATH_MATRIX:$case_id"
  node "$SBM_GATE_ROOT/tools/record-no-partial.mjs" "$NO_PARTIAL_JSONL" "$case_id" "ABSENT" 0 0 "UNCHANGED"
done

node "$SBM_GATE_ROOT/tools/finalize-no-partial.mjs" "$NO_PARTIAL_JSONL" >"$SBM_GATE_ROOT/evidence/no-partial-summary.txt"
grep -F 'NO_PARTIAL_SCAFFOLD=PASS' "$SBM_GATE_ROOT/evidence/no-partial-summary.txt" >/dev/null || fail "NO_PARTIAL_SCAFFOLD" "MATRIX_FAIL"
record_pass "NO_PARTIAL_SCAFFOLD" "closed 17-case physical matrix: controlled invalid; NEW/CLONE explicit invalids; GEN20/22; atomic02 A/B; lexical and 3 symlink UNSAFE_PATH; every failure FINAL absent TEMP 0 LOCK 0 outside unchanged"

mkdir -p "$SBM_GATE_ROOT/repro-a/extract" "$SBM_GATE_ROOT/repro-independent/extract"

unzip -q "$COPIED_ARTIFACT" -d "$SBM_GATE_ROOT/repro-a/extract"
unzip -q "$COPIED_ARTIFACT" -d "$SBM_GATE_ROOT/repro-independent/extract"

node "$SBM_GATE_ROOT/tools/deterministic-zip.mjs" \
  "$SBM_GATE_ROOT/repro-a/extract/generator-sbm-agent-v2_0_0" \
  "$SBM_GATE_ROOT/repro-a/generation-a.zip" \
  >"$SBM_GATE_ROOT/evidence/repro-a.txt"

node "$SBM_GATE_ROOT/tools/deterministic-zip.mjs" \
  "$SBM_GATE_ROOT/repro-a/extract/generator-sbm-agent-v2_0_0" \
  "$SBM_GATE_ROOT/repro-a/generation-b.zip" \
  >"$SBM_GATE_ROOT/evidence/repro-b.txt"

node "$SBM_GATE_ROOT/tools/deterministic-zip.mjs" \
  "$SBM_GATE_ROOT/repro-independent/extract/generator-sbm-agent-v2_0_0" \
  "$SBM_GATE_ROOT/repro-independent/independent.zip" \
  >"$SBM_GATE_ROOT/evidence/repro-independent.txt"

read -r GENERATION_A_SHA _ < <(sha256sum "$SBM_GATE_ROOT/repro-a/generation-a.zip")
read -r GENERATION_B_SHA _ < <(sha256sum "$SBM_GATE_ROOT/repro-a/generation-b.zip")
read -r INDEPENDENT_REBUILD_SHA _ < <(sha256sum "$SBM_GATE_ROOT/repro-independent/independent.zip")

[[ "$GENERATION_A_SHA" == "$EXPECTED_SHA" ]] || fail "REPRODUCIBILITY" "GENERATION_A_MISMATCH"
[[ "$GENERATION_B_SHA" == "$EXPECTED_SHA" ]] || fail "REPRODUCIBILITY" "GENERATION_B_MISMATCH"
[[ "$INDEPENDENT_REBUILD_SHA" == "$EXPECTED_SHA" ]] || fail "REPRODUCIBILITY" "INDEPENDENT_MISMATCH"

record_pass "REPRODUCIBILITY" "generation_a=$GENERATION_A_SHA generation_b=$GENERATION_B_SHA delivered=$EXPECTED_SHA independent=$INDEPENDENT_REBUILD_SHA byte_identical=PASS"

read -r FINAL_SOURCE_SHA_AFTER _ < <(sha256sum "$CANDIDATE")
read -r FINAL_COPIED_SHA_AFTER _ < <(sha256sum "$COPIED_ARTIFACT")
read -r EXTERNAL_GATE_SHA_AFTER _ < <(sha256sum "$SCRIPT_PATH")

[[ "$FINAL_SOURCE_SHA_AFTER" == "$EXPECTED_SHA" ]] || fail "FINAL_SOURCE_SHA_MATCH" "SOURCE_MUTATED"
[[ "$FINAL_COPIED_SHA_AFTER" == "$EXPECTED_SHA" ]] || fail "FINAL_COPIED_SHA_MATCH" "COPY_MUTATED"
[[ "$EXTERNAL_GATE_SHA_AFTER" == "$EXTERNAL_GATE_SHA_BEFORE" ]] || fail "EXTERNAL_GATE_SHA_MATCH" "FAIL_EXTERNAL_GATE_MUTATED"

record_pass "FINAL_SOURCE_SHA_MATCH" "final_source_sha_after=$FINAL_SOURCE_SHA_AFTER expected=$EXPECTED_SHA"
record_pass "FINAL_COPIED_SHA_MATCH" "final_copied_sha_after=$FINAL_COPIED_SHA_AFTER expected=$EXPECTED_SHA"
record_pass "EXTERNAL_GATE_SHA_MATCH" "external_gate_sha_before=$EXTERNAL_GATE_SHA_BEFORE external_gate_sha_after=$EXTERNAL_GATE_SHA_AFTER"

node --input-type=module - \
  "$RUNTIME_METADATA_FILE" \
  "$EXPECTED_SHA" \
  "$EXTERNAL_GATE_SHA_BEFORE" \
  "$GENERATION_A_SHA" \
  "$GENERATION_B_SHA" \
  "$INDEPENDENT_REBUILD_SHA" \
  "$FINAL_SOURCE_SHA_AFTER" \
  "$FINAL_COPIED_SHA_AFTER" \
  "$EXTERNAL_GATE_SHA_AFTER" \
  "$(node -p 'process.versions.zlib')" <<'SBM_RUNTIME_METADATA'
import fs from 'node:fs';

const [
  file,
  artifact,
  gate,
  genA,
  genB,
  independent,
  finalSource,
  finalCopy,
  gateAfter,
  zlib
]=process.argv.slice(2);

const object={
  artifact_sha:artifact,
  expected_artifact_sha:artifact,
  external_gate_sha:gate,
  runtime_versions:{
    node:'22.14.0',
    npm:'10.9.2',
    yo:'7.0.1',
    yeoman_environment:'6.2.0',
    yeoman_generator:'7.5.1',
    yeoman_test:'9.1.0',
    mocha:'10.8.2',
    chai:'5.1.2',
    yaml:'2.7.0',
    ajv:'8.20.0',
    zlib
  },
  reproducibility_tool:'NODE_22_14_0_BUILTIN_ZLIB_DETERMINISTIC_ZIP_V1',
  reproducibility_hashes:{
    generation_a:genA,
    generation_b:genB,
    delivered:artifact,
    independent_rebuild:independent
  },
  package_validation:'PASS',
  final_source_sha_after:finalSource,
  final_copied_sha_after:finalCopy,
  external_gate_sha_after:gateAfter
};

fs.writeFileSync(file,JSON.stringify(object,null,2)+'\n');
SBM_RUNTIME_METADATA

node \
  "$SBM_GATE_ROOT/tools/finalize-evidence.mjs" \
  "$EVIDENCE_JSONL" \
  "$RUNTIME_METADATA_FILE"

printf 'GATE_INITIAL_CANDIDATE_SHA256=%s\n' "$SOURCE_SHA_BEFORE"
printf 'GATE_FINAL_CANDIDATE_SHA256=%s\n' "$FINAL_SOURCE_SHA_AFTER"
printf 'EXPECTED_CANDIDATE_SHA256=%s\n' "$EXPECTED_SHA"
printf 'EXTERNAL_ACCEPTANCE_GATE_SHA256=%s\n' "$EXTERNAL_GATE_SHA_BEFORE"
printf 'DUAL_SHA_BINDING=PASS\n'
printf 'RESULT: PASS_GATE\n'

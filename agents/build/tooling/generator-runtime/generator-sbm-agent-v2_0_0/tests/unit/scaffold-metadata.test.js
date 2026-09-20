import assert from 'node:assert/strict';
import {metadataFromInput,proposalCandidateFromInput} from '../../generators/app/index.js';
import {validInput,exactRuntimeDependenciesAvailable} from './prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-10'];
export const gateCases={'GEN-SCHEMA-10':'operational design-intent metadata stays in scaffold metadata and never leaks into canonical proposal output'};
export async function run(){
  if(!exactRuntimeDependenciesAvailable())return {pending:gates,reason:'ajv@8.20.0/yaml@2.7.0 unavailable'};
  const i={...validInput(),standard_upgrade_requested:true,source_agent_id_hint:'Alpha',source_agent_version_hint:'0.9.0',source_standard_version_hint:'1.0.0'};
  const m=metadataFromInput(i),p=proposalCandidateFromInput(i);
  assert.equal(m.design_intent.standard_upgrade_requested,true);
  for(const k of ['execution_id','origin','design_intent','standard_upgrade_requested','source_agent_id_hint'])assert.equal(k in p,false);
  assert.equal('migration_reference' in p,false);
}

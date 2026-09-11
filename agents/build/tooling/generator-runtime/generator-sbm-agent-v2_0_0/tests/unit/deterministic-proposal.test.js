import assert from 'node:assert/strict';
import {proposalFromInput,deterministicDigest,validateProposal} from '../../generators/app/index.js';
import {validInput,exactRuntimeDependenciesAvailable} from './prompt-mapping.test.js';
export const gates=['GEN-SCHEMA-09','GEN-SCHEMA-21'];
export const gateCases={
  'GEN-SCHEMA-09':'same valid DRAFT_INPUT yields the same canonical proposal digest',
  'GEN-SCHEMA-21':'canonical validator executes real valid/invalid cases covering type, required, additionalProperties, minLength, items, oneOf, enum, allOf, if, const and then'
};
function invalid(base,mutate){const x=structuredClone(base);mutate(x);return x;}
export async function run(){
  if(!exactRuntimeDependenciesAvailable())return {pending:gates,reason:'ajv@8.20.0/yaml@2.7.0 unavailable'};
  const a=proposalFromInput(validInput()),b=proposalFromInput(validInput());
  assert.equal(deterministicDigest(a),deterministicDigest(b));
  const cases=[
    ['type',p=>p.agent_name=7],
    ['required',p=>delete p.agent_name],
    ['additionalProperties',p=>p.extra='x'],
    ['minLength',p=>p.agent_name=''],
    ['items',p=>p.specific_objectives=[7]],
    ['oneOf',p=>p.deployment='bad'],
    ['enum',p=>p.creation_mode='OTHER'],
    ['allOf-if-const-then NEW',p=>{p.creation_mode='NEW';p.parent_reference={agent_id:'P',agent_version:'1',spec_id:'S',spec_version:'1'};}],
    ['allOf-if-const-then CLONE',p=>{p.creation_mode='CLONE';p.parent_reference=null;}]
  ];
  for(const [name,mutate] of cases){
    assert.throws(()=>validateProposal(invalid(a,mutate)),e=>e.code==='INVALID_OUTPUT_CONTRACT',name);
  }
  validateProposal(a);
}

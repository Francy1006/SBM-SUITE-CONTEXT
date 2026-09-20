import assert from 'node:assert/strict';import {validateGeneratorRules} from '../../generators/app/index.js';import {validInput} from '../unit/prompt-mapping.test.js';
export const gates=[];export async function run(){assert.throws(()=>validateGeneratorRules({...validInput(),approval_record:{approval_id:'x'}}),e=>e.code==='INVALID_INPUT'&&e.details?.reason==='unknown_input');}

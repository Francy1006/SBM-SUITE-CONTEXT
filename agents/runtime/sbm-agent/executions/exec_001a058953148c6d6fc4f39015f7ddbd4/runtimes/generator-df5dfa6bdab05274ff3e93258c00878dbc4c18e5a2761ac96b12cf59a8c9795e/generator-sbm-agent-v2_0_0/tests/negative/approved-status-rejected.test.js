import assert from 'node:assert/strict';
import {normalizeCapturedInput} from '../../generators/app/index.js';
import {validInput} from '../unit/prompt-mapping.test.js';
export const gates=[];
export async function run(){
  for(const s of ['APPROVED','APROBABLE','REFUTED'])assert.throws(()=>normalizeCapturedInput({}, {...validInput(),review_status:s}, false),e=>e.code==='INVALID_INPUT'&&e.path==='review_status');
}

import assert from 'node:assert/strict';import {safeScaffoldPath} from '../../generators/app/index.js';
export const gates=[];export async function run(){assert.throws(()=>safeScaffoldPath('/tmp','context/x'),e=>e.code==='UNSAFE_PATH');}

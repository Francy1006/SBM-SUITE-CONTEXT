import assert from 'node:assert/strict';import {safeScaffoldPath} from '../../generators/app/index.js';
export const gates=[];
export async function run(){for(const value of ['../x','/tmp/x','context/x','dist/x','build/agents/x'])assert.throws(()=>safeScaffoldPath('/tmp',value),e=>e.code==='UNSAFE_PATH');}

import assert from 'node:assert/strict';import fs from 'node:fs';
export const gates=[];export async function run(){for(const f of ['generators/app/index.js','generators/clone/index.js']){const s=fs.readFileSync(new URL('../../'+f,import.meta.url),'utf8');assert.equal(s.includes('AGENT_DEFINITION.yaml'),false);assert.equal(s.includes('AGENT_SPEC.yaml'),false);}}

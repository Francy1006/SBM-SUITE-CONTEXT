import assert from 'node:assert/strict';
import fs from 'node:fs';
export const gates=[];
export async function run(){
  for(const f of ['generators/app/index.js','generators/clone/index.js']){
    const s=fs.readFileSync(new URL('../../'+f,import.meta.url),'utf8');
    for(const token of ['createWriteStream(','archiver','new JSZip','new AdmZip','package-agent','dist/agents'])assert.equal(s.includes(token),false,`${f} must not implement final ZIP generation: ${token}`);
  }
}

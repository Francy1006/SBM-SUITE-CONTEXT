import assert from 'node:assert/strict';import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {atomicCommitScaffold} from '../../generators/app/index.js';
export const gates=['GEN-ATOMIC-02'];
export const gateCases={'GEN-ATOMIC-02':'fault injection after first TEMP write and after second TEMP write before rename leaves no FINAL, owned TEMP or owned LOCK'};
function assertClean(base,id){const root=path.join(base,'build/scaffolds');assert.equal(fs.existsSync(path.join(root,id)),false);assert.equal(fs.existsSync(path.join(root,`.lock-${id}`)),false);assert.equal(fs.readdirSync(root).some(x=>x.startsWith(`.tmp-${id}-`)),false);}
export async function run(){
  const base=fs.mkdtempSync(path.join(os.tmpdir(),'gen-v2-fault-'));const root=path.join(base,'build/scaffolds');fs.mkdirSync(root,{recursive:true});fs.writeFileSync(path.join(root,'.lock-unowned'),'sentinel');fs.mkdirSync(path.join(root,'.tmp-unowned'));
  assert.throws(()=>atomicCommitScaffold(base,'fault-a',t=>{fs.writeFileSync(path.join(t,'AGENT_PROPOSAL.yaml'),'x');throw new Error('fault-after-first-write');}),/fault-after-first-write/);assertClean(base,'fault-a');
  assert.throws(()=>atomicCommitScaffold(base,'fault-b',t=>{fs.writeFileSync(path.join(t,'AGENT_PROPOSAL.yaml'),'x');fs.mkdirSync(path.join(t,'.sbm'));fs.writeFileSync(path.join(t,'.sbm/scaffold.json'),'{}');throw new Error('fault-after-second-write-before-rename');}),/fault-after-second-write-before-rename/);assertClean(base,'fault-b');
  assert.equal(fs.existsSync(path.join(root,'.lock-unowned')),true);assert.equal(fs.existsSync(path.join(root,'.tmp-unowned')),true);
}

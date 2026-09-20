import assert from 'node:assert/strict';import {safeScaffoldPath} from '../../generators/app/index.js';
export const gates=[];
export async function run(){for(const v of ['../x','/tmp/x','context/x','dist/x','build/agents/x'])assert.throws(()=>safeScaffoldPath('/tmp',v),e=>e.code==='UNSAFE_PATH');}

/* SBM_CHECKLIST_269_SYMLINK_ESCAPE_PHYSICAL */
{
  const assert=await import('node:assert/strict');
  const fs=await import('node:fs');
  const os=await import('node:os');
  const path=await import('node:path');
  const crypto=await import('node:crypto');
  const {atomicCommitScaffold,safeScaffoldPath}=await import('../../generators/app/index.js');

  function sha(file){
    return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  }

  for(const raw of ['../x','/tmp/x','a/b','a\\b','context/x','dist/x','build/agents/x','..']){
    const base=fs.mkdtempSync(path.join(os.tmpdir(),'sbm-unsafe-lexical-'));
    let caught;

    try{
      safeScaffoldPath(base,raw);
    }catch(error){
      caught=error;
    }

    assert.equal(caught?.code,'UNSAFE_PATH');
    assert.equal(fs.existsSync(path.join(base,'build','scaffolds')),false);

    fs.rmSync(base,{recursive:true,force:true});
  }

  console.log('UNSAFE_PATH_LEXICAL: PASS');

  async function symlinkCase(kind){
    const root=fs.mkdtempSync(path.join(os.tmpdir(),`sbm-unsafe-${kind}-`));
    const base=path.join(root,'base');
    const outside=path.join(root,'outside');

    fs.mkdirSync(base,{recursive:true});
    fs.mkdirSync(outside,{recursive:true});

    const sentinel=path.join(outside,'sentinel.txt');
    fs.writeFileSync(sentinel,'OUTSIDE-PROTECTED\n');
    const before=sha(sentinel);

    const id='symlink-escape';
    let writerCalled=false;

    if(kind==='build'){
      fs.symlinkSync(outside,path.join(base,'build'),'dir');
    }else if(kind==='scaffold-root'){
      fs.mkdirSync(path.join(base,'build'),{recursive:true});
      fs.symlinkSync(outside,path.join(base,'build','scaffolds'),'dir');
    }else if(kind==='final'){
      fs.mkdirSync(path.join(base,'build','scaffolds'),{recursive:true});
      fs.symlinkSync(outside,path.join(base,'build','scaffolds',id),'dir');
    }else{
      throw new Error(`UNKNOWN_TEST_KIND:${kind}`);
    }

    let caught;

    try{
      atomicCommitScaffold(base,id,()=>{
        writerCalled=true;
      });
    }catch(error){
      caught=error;
    }

    assert.equal(caught?.code,'UNSAFE_PATH');
    assert.equal(writerCalled,false);
    assert.equal(sha(sentinel),before);

    const scaffoldRoot=path.join(base,'build','scaffolds');

    if(fs.existsSync(scaffoldRoot) && !fs.lstatSync(scaffoldRoot).isSymbolicLink()){
      const names=fs.readdirSync(scaffoldRoot);
      assert.equal(names.some(n=>n===`.lock-${id}`),false);
      assert.equal(names.some(n=>n.startsWith(`.tmp-${id}-`)),false);

      if(kind!=='final'){
        assert.equal(fs.existsSync(path.join(scaffoldRoot,id)),false);
      }
    }

    fs.rmSync(root,{recursive:true,force:true});
  }

  await symlinkCase('build');
  console.log('UNSAFE_PATH_SYMLINK_BUILD: PASS');

  await symlinkCase('scaffold-root');
  console.log('UNSAFE_PATH_SYMLINK_SCAFFOLD_ROOT: PASS');

  await symlinkCase('final');
  console.log('UNSAFE_PATH_SYMLINK_FINAL: PASS');
}

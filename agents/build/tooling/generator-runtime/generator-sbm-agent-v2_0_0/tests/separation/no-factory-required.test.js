import assert from 'node:assert/strict';import fs from 'node:fs';
export const gates=[];export async function run(){const p=JSON.parse(fs.readFileSync(new URL('../../package.json',import.meta.url),'utf8'));assert.equal('sbm-agent-factory' in (p.dependencies||{}),false);for(const f of ['generators/app/index.js','generators/clone/index.js']){const s=fs.readFileSync(new URL('../../'+f,import.meta.url),'utf8');assert.equal(s.includes('sbm-agent create'),false);assert.equal(s.includes('SBM-Agent-Factory-v1_0_0.zip'),false);}}

/* SBM_CHECKLIST_269_CEO_GENERICITY */
{
  const assert=await import('node:assert/strict');
  const fs=await import('node:fs');
  const path=await import('node:path');
  const {
    proposalFromInput,
    promptQuestions,
    normalizeCapturedInput
  }=await import('../../generators/app/index.js');
  const {exactRuntimeDependenciesAvailable}=await import('../unit/prompt-mapping.test.js');

  const projectRoot=path.resolve(
    new URL('../../',import.meta.url).pathname
  );

  const productiveRoots=[
    path.join(projectRoot,'generators'),
    path.join(projectRoot,'config'),
    path.join(projectRoot,'schemas'),
    path.join(projectRoot,'templates')
  ];

  const productiveFiles=[];

  function walk(dir){
    if(!fs.existsSync(dir)) return;

    for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
      const p=path.join(dir,ent.name);

      if(ent.isDirectory()){
        walk(p);
      }else if(ent.isFile()){
        productiveFiles.push(p);
      }
    }
  }

  for(const root of productiveRoots) walk(root);

  for(const file of productiveFiles){
    const source=fs.readFileSync(file,'utf8');

    if(
      /\\bCEO\\b/.test(source) ||
      /CEO Agent/.test(source) ||
      /CEO_HARDCODED/.test(source) ||
      /case\\s+['\"]CEO['\"]/.test(source) ||
      /===\\s*['\"]CEO['\"]/.test(source) ||
      /!==\\s*['\"]CEO['\"]/.test(source)
    ){
      throw new Error(`CEO_PRODUCTIVE_SPECIALIZATION:${file}`);
    }
  }

  function input(agent_name,proposal_id){
    return {
      execution_id:'genericity-run',
      proposal_id,
      proposal_version:'1.0.0',
      agent_name,
      agent_description:'Generic semantic comparison',
      agent_purpose:'Validate generic generator behavior',
      specific_objectives:['genericity'],
      general_context:'Generic QA',
      responsibilities:['generic responsibility'],
      authority:['none'],
      permissions:['draft_generation'],
      hierarchy:'reports_to: sbm-admin',
      relationships:[],
      personality:'neutral',
      communication_style:'concise',
      required_context:[],
      retrieval_strategy:'NONE',
      embedding_strategy:'NONE',
      llm_policy:'NO_LLM_BY_DEFAULT',
      execution_modes:['NON_INTERACTIVE'],
      expected_frequency:'AD_HOC',
      asynchronous_capabilities:[],
      execution_dependencies:[],
      outputs:['AGENT_PROPOSAL_DRAFT'],
      escalation_rules:[],
      deployment:null,
      qa_specific:['CEO_GENERICITY'],
      creation_mode:'NEW',
      review_status:'DRAFT',
      origin:'config',
      non_interactive:true,
      standard_upgrade_requested:false,
      source_agent_id_hint:null,
      source_agent_version_hint:null,
      source_standard_version_hint:null
    };
  }

  const ceoInput=input('CEO','CEO-GENERICITY');
  const genericInput=input('GenericAgent','GENERIC-GENERICITY');

  function normalizeProposal(proposal){
    return {
      ...proposal,
      agent_name:'<IDENTITY>',
      proposal_id:'<PROPOSAL_ID>'
    };
  }

  if(exactRuntimeDependenciesAvailable()){
    const ceoProposal=proposalFromInput(ceoInput,{clone:false});
    const genericProposal=proposalFromInput(genericInput,{clone:false});
    assert.deepEqual(
      normalizeProposal(ceoProposal),
      normalizeProposal(genericProposal)
    );
  }

  const ceoProcessed=normalizeCapturedInput({},ceoInput,false);
  const genericProcessed=normalizeCapturedInput({},genericInput,false);
  assert.deepEqual(
    normalizeProposal(ceoProcessed),
    normalizeProposal(genericProcessed)
  );

  const ceoDefaults={agent_name:'CEO',proposal_id:'CEO-GENERICITY'};
  const genericDefaults={agent_name:'GenericAgent',proposal_id:'GENERIC-GENERICITY'};

  const ceoPrompts=promptQuestions(ceoDefaults,false);
  const genericPrompts=promptQuestions(genericDefaults,false);

  function normalizePrompt(q){
    const out={name:q.name,type:q.type,message:q.message};
    if(q.name==='agent_name') out.default='<IDENTITY>';
    else if(q.name==='proposal_id') out.default='<PROPOSAL_ID>';
    else out.default=q.default;
    return out;
  }

  assert.deepEqual(
    ceoPrompts.map(normalizePrompt),
    genericPrompts.map(normalizePrompt)
  );

  const ceoOnlyFields=['permission','hierarchy','relationship','policy','execution'];
  for(const token of ceoOnlyFields){
    assert.equal(
      ceoPrompts.some(q=>String(q.name).toLowerCase().includes(`ceo_${token}`)),
      false
    );
  }

  const appSource=fs.readFileSync(
    new URL('../../generators/app/index.js',import.meta.url),
    'utf8'
  );

  assert.equal(
    /(?:import|require|spawn|exec)[^\\n]*SBM-Agent-Factory/i.test(appSource),
    false
  );

  console.log('CEO_ONLY_PROMPT: ABSENT');
  console.log('CEO_ONLY_DEFAULT: ABSENT');
  console.log('CEO_ONLY_PERMISSION: ABSENT');
  console.log('CEO_ONLY_HIERARCHY: ABSENT');
  console.log('CEO_ONLY_RELATIONSHIP: ABSENT');
  console.log('CEO_ONLY_POLICY: ABSENT');
  console.log('CEO_ONLY_EXECUTION_PATH: ABSENT');
  console.log('CEO_HARDCODED: false');
  console.log('FACTORY_RUNTIME_DEPENDENCY: NONE');
}

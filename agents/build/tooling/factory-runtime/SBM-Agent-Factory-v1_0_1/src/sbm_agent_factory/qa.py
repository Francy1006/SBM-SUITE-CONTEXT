from pathlib import Path
import subprocess,sys,os,yaml,copy,tempfile
from concurrent.futures import ThreadPoolExecutor

def run_tests(root):
    from types import SimpleNamespace
    root=Path(root)
    env=dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    targets=[root/'tests'/'unit',root/'tests'/'integration',root/'tests'/'negative',root/'tests'/'e2e']
    with tempfile.TemporaryDirectory(prefix='sbm-factory-qa-') as td:
        procs=[]
        for i,target in enumerate(targets):
            outp=Path(td)/f'{i}.out'; errp=Path(td)/f'{i}.err'
            of=outp.open('w'); ef=errp.open('w')
            proc=subprocess.Popen([sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(target)],cwd=root,text=True,stdout=of,stderr=ef,env=env)
            procs.append((target,proc,of,ef,outp,errp))
        results=[]
        for target,proc,of,ef,outp,errp in procs:
            rc=proc.wait(); of.close(); ef.close()
            results.append((target.name,rc,outp.read_text(),errp.read_text()))
    failures=[label for label,rc,_,_ in results if rc!=0]
    stdout=''.join(f'[{label}]\n{out}' for label,_,out,_ in results)
    stderr=''.join(err for _,_,_,err in results)
    if failures: stderr += 'FAILED_TARGETS: '+', '.join(failures)+'\n'
    return SimpleNamespace(returncode=1 if failures else 0,stdout=stdout,stderr=stderr,failed_targets=failures)

def canonical_template_path():
    p=os.environ.get('SBM_CANONICAL_TEMPLATE')
    if p and Path(p).is_file(): return Path(p)
    for c in [Path('/mnt/data/SBM-Agent-Template-v2_0_1.zip'),Path.cwd().parent/'SBM-Agent-Template-v2_0_1.zip']:
        if c.is_file(): return c
    raise FileNotFoundError('SBM_CANONICAL_TEMPLATE is required for canonical Factory E2E QA')

def _approval(aid,typ,artifact_id,version):
    return {'approval_id':aid,'approval_type':typ,'approved_by':'sbm-admin','approved_at':'1980-01-01T00:00:00Z','artifact_id':artifact_id,'artifact_version':str(version),'approval_status':'APPROVED'}

def write_fixture_bundle(base,template_zip=None,mode='NEW',agent_id='FixtureAgent',agent_version='1.0.0',parent_spec=None,migration=None,mutator=None):
    from .template_engine import TemplateEngine
    from .checksum import sha256_file
    template_zip=Path(template_zip or canonical_template_path()); base=Path(base); base.mkdir(parents=True,exist_ok=True)
    contract=TemplateEngine().resolve('SBM-Agent-Template','2.0.1',template_zip,sha256_file(template_zip))
    try: fx=yaml.safe_load((contract.root/'fixtures/new/fixture.yaml').read_text(encoding='utf-8'))
    finally: contract.close()
    p=copy.deepcopy(fx['proposal']); s=copy.deepcopy(fx['spec']); comps={k:copy.deepcopy(fx[k]) for k in ['definition','agent_context','context_contract','runtime_profile','permissions','hierarchy','relationships','lineage']}
    old='FixtureAgent'; p.update({'proposal_id':f'PROP-{agent_id}','agent_name':agent_id,'creation_mode':mode,'parent_reference':None,'review_status':'APPROVED'})
    s.update({'spec_id':f'SPEC-{agent_id}','agent_id':agent_id,'agent_version':str(agent_version),'proposal_reference':{'proposal_id':p['proposal_id'],'proposal_version':p['proposal_version']},'creation_mode':mode,'migration_reference':migration,'parent_reference':None})
    d=comps['definition']; d.update({'agent_definition_id':f'DEF-{agent_id}','agent_id':agent_id,'agent_version':str(agent_version),'agent_definition_version':str(agent_version)})
    ac=comps['agent_context']; ac.update({'agent_id':agent_id,'agent_version':str(agent_version),'context_version':str(agent_version)})
    cc=comps['context_contract']; cc.update({'context_contract_id':f'CTX-{agent_id}','context_contract_version':str(agent_version),'agent_id':agent_id})
    rp=comps['runtime_profile']; rp.update({'runtime_profile_id':f'RUN-{agent_id}','runtime_profile_version':str(agent_version),'agent_id':agent_id})
    pe=comps['permissions']; pe.update({'permissions_id':f'PERM-{agent_id}','permissions_version':str(agent_version),'agent_id':agent_id})
    hi=comps['hierarchy']; hi.update({'agent_id':agent_id,'hierarchy_version':str(agent_version)})
    re=comps['relationships']; re.update({'relationships_id':f'REL-{agent_id}','relationships_version':str(agent_version),'agent_id':agent_id})
    li=comps['lineage']; li.update({'clone_lineage_id':f'LINEAGE-{agent_id}','agent_id':agent_id,'agent_version':str(agent_version),'clone_id':None,'parent_agent_id':None,'parent_agent_version':None,'parent_spec_id':None,'parent_spec_version':None})
    if mode=='CLONE':
        if not parent_spec: raise ValueError('CLONE requires parent_spec')
        pref={'agent_id':parent_spec['agent_id'],'agent_version':parent_spec['agent_version'],'spec_id':parent_spec['spec_id'],'spec_version':parent_spec['spec_version']}; p['parent_reference']=pref; s['parent_reference']=pref; s['migration_reference']=None
        li.update({'is_clone':True,'clone_id':agent_id,'parent_agent_id':pref['agent_id'],'parent_agent_version':pref['agent_version'],'parent_spec_id':pref['spec_id'],'parent_spec_version':pref['spec_version']})
    else:
        li['is_clone']=False
    s['component_references']={
        'AGENT_DEFINITION':{'artifact_id':d['agent_definition_id'],'artifact_version':d['agent_definition_version']},
        'AGENT_CONTEXT':{'artifact_id':ac['agent_id'],'artifact_version':ac['context_version']},
        'CONTEXT_CONTRACT':{'artifact_id':cc['context_contract_id'],'artifact_version':cc['context_contract_version']},
        'RUNTIME_PROFILE':{'artifact_id':rp['runtime_profile_id'],'artifact_version':rp['runtime_profile_version']},
        'CLONE_LINEAGE':{'artifact_id':li['clone_lineage_id'],'artifact_version':li['agent_version']},
        'PERMISSIONS':{'artifact_id':pe['permissions_id'],'artifact_version':pe['permissions_version']},
        'HIERARCHY':{'artifact_id':hi['agent_id'],'artifact_version':hi['hierarchy_version']},
        'RELATIONSHIPS':{'artifact_id':re['relationships_id'],'artifact_version':re['relationships_version']},
    }
    spec_approval=_approval(f'SPEC-APP-{agent_id}','AGENT_SPEC',s['spec_id'],s['spec_version']); s['approval_reference']={'approval_id':spec_approval['approval_id'],'artifact_version':spec_approval['artifact_version']}
    proposal_approval=_approval(f'PROP-APP-{agent_id}','AGENT_PROPOSAL',p['proposal_id'],p['proposal_version'])
    materialization=_approval(f'MAT-APP-{agent_id}','MATERIALIZATION',s['spec_id'],s['spec_version'])
    payload={'proposal':p,'spec':s,'AGENT_DEFINITION':d,'AGENT_CONTEXT':ac,'CONTEXT_CONTRACT':cc,'RUNTIME_PROFILE':rp,'CLONE_LINEAGE':li,'PERMISSIONS':pe,'HIERARCHY':hi,'RELATIONSHIPS':re,'proposal_approval':proposal_approval,'spec_approval':spec_approval,'materialization_approval':materialization}
    if mutator: mutator(payload)
    pathmap={'proposal':'AGENT_PROPOSAL.yaml','spec':'AGENT_SPEC.yaml','AGENT_DEFINITION':'AGENT_DEFINITION.yaml','AGENT_CONTEXT':'AGENT_CONTEXT.yaml','CONTEXT_CONTRACT':'config/CONTEXT_CONTRACT.yaml','RUNTIME_PROFILE':'config/RUNTIME_PROFILE.yaml','CLONE_LINEAGE':'config/CLONE_LINEAGE.yaml','PERMISSIONS':'config/PERMISSIONS.yaml','HIERARCHY':'config/HIERARCHY.yaml','RELATIONSHIPS':'config/RELATIONSHIPS.yaml','proposal_approval':'PROPOSAL_APPROVAL.yaml','spec_approval':'SPEC_APPROVAL.yaml','materialization_approval':'MATERIALIZATION_APPROVAL.yaml'}
    out={}
    for k,rel in pathmap.items():
        q=base/rel; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(yaml.safe_dump(payload[k],sort_keys=False),encoding='utf-8',newline='\n'); out[k]=q
    out['payload']=payload; return out


def render_fixture_agent(bundle, template_zip, destination, config):
    """QA-only helper: materialize a valid unpacked agent without producing a prior ZIP."""
    from .approvals import validate_gate
    from .template_engine import TemplateEngine
    from .create import load_target_components, _write_integrity
    proposal,spec,approvals=validate_gate(bundle['proposal'],bundle['proposal_approval'],bundle['spec'],bundle['spec_approval'],bundle['materialization_approval'])
    engine=TemplateEngine(); contract=engine.resolve(config['template_id'],config['template_version'],template_zip,config['canonical_template_sha256'])
    try:
        comps=load_target_components(bundle['spec'],spec)
        engine.validate_inputs(contract,proposal,spec,approvals,comps)
        destination=Path(destination); destination.mkdir(parents=True,exist_ok=True)
        engine.render(contract,{'proposal':proposal,'spec':spec,'components':comps,'approvals':approvals},destination)
        engine.verify_output(destination,contract)
        _write_integrity(destination)
        return destination
    finally:
        contract.close()

def run_agent_qa(agent_root):
    root=Path(agent_root)
    env=dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    validate_script=root/'scripts/validate'
    test_script=root/'scripts/test'
    if not validate_script.is_file() or not test_script.is_file():
        return {'validation_result':'INVALID','qa_result':'NOT_RUN','agent_validate_exit_code':127,'agent_test_exit_code':127,'validate_stdout':'','validate_stderr':'missing scripts/validate or scripts/test','test_stdout':'','test_stderr':''}
    vr=subprocess.run([sys.executable,str(validate_script)],cwd=root,text=True,capture_output=True,env=env)
    if vr.returncode!=0:
        return {'validation_result':'INVALID','qa_result':'FAIL','agent_validate_exit_code':vr.returncode,'agent_test_exit_code':-1,'validate_stdout':vr.stdout,'validate_stderr':vr.stderr,'test_stdout':'','test_stderr':'NOT_RUN'}
    tr=subprocess.run([sys.executable,str(test_script)],cwd=root,text=True,capture_output=True,env=env)
    return {'validation_result':'VALID','qa_result':'PASS' if tr.returncode==0 else 'FAIL','agent_validate_exit_code':vr.returncode,'agent_test_exit_code':tr.returncode,'validate_stdout':vr.stdout,'validate_stderr':vr.stderr,'test_stdout':tr.stdout,'test_stderr':tr.stderr}

from pathlib import Path
import copy, hashlib, io, json, tempfile, zipfile
import yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
FIXED_DT=(2020,1,1,0,0,0)

def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding='utf-8'))

def _approval_schema(): return y('schemas/APPROVAL_RECORD.schema.yaml')

def _proposal_schema(): return y('schemas/AGENT_PROPOSAL.schema.yaml')

def _canonical_yaml(obj): return yaml.safe_dump(obj,sort_keys=True,allow_unicode=True).encode('utf-8')

def _zip_bytes(files):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel,data in sorted(files.items()):
            zi=zipfile.ZipInfo(rel,FIXED_DT); zi.create_system=3; zi.external_attr=(0o100644 << 16); zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,data)
    return out.getvalue()

def _materialize_for_test(proposal, approval, scaffold_dir=None, origin='DIRECT'):
    """Deterministic QA-only materialization harness; not a product Factory/Generator."""
    if proposal.get('review_status')!='APPROVED':
        return {'status':'BLOCKED','error':'PROPOSAL_NOT_APPROVED','package':None,'operation_attempted':True}
    p_errors=list(Draft202012Validator(_proposal_schema()).iter_errors(proposal))
    a_errors=list(Draft202012Validator(_approval_schema()).iter_errors(approval))
    if p_errors or a_errors or approval.get('approved_by')!='sbm-admin' or approval.get('approval_status')!='APPROVED':
        return {'status':'BLOCKED','error':'APPROVAL_PATH_INVALID','package':None,'operation_attempted':True}
    if scaffold_dir is not None and 'build/scaffolds/' in scaffold_dir.as_posix().replace('\\','/'):
        return {'status':'BLOCKED','error':'PROVISIONAL_SCAFFOLD_NOT_REGISTRABLE','package':None,'operation_attempted':True}
    files={
        'Agent/AGENT_PROPOSAL.yaml':_canonical_yaml(proposal),
        'Agent/APPROVAL.yaml':_canonical_yaml(approval),
    }
    if scaffold_dir is not None:
        for p in sorted(scaffold_dir.rglob('*')):
            if not p.is_file(): continue
            rel=p.relative_to(scaffold_dir).as_posix()
            if rel=='.sbm/scaffold.json' or rel.startswith('.sbm/') or rel.startswith('build/') or rel.startswith('context/'):
                continue
            files['Agent/scaffold/'+rel]=p.read_bytes()
    # origin deliberately has no normative effect and is not packaged.
    return {'status':'SUCCEEDED','error':None,'package':_zip_bytes(files),'operation_attempted':True,'origin_seen':origin}

def _candidate_registry_incorporate(result, registry_root):
    registry_root.mkdir(parents=True,exist_ok=True)
    if result['status']!='SUCCEEDED':
        return {'status':'BLOCKED','written':False}
    (registry_root/'candidate.zip').write_bytes(result['package'])
    return {'status':'SUCCEEDED','written':True}

def test_qa_template_22_separation_01_to_05():
    fixture=y('fixtures/new/fixture.yaml')
    approved=copy.deepcopy(fixture['proposal'])
    approval=copy.deepcopy(fixture['approval'])

    # QA-SEPARATION-01: a real materialization attempt is blocked before a package exists.
    draft=copy.deepcopy(approved); draft['review_status']='DRAFT'
    r=_materialize_for_test(draft,approval)
    assert r['operation_attempted'] is True
    assert r['status']=='BLOCKED' and r['error']=='PROPOSAL_NOT_APPROVED' and r['package'] is None

    # QA-SEPARATION-02: Yeoman cannot traverse the effective approval path.
    yeoman_approval=copy.deepcopy(approval); yeoman_approval['approved_by']='Yeoman'
    r=_materialize_for_test(approved,yeoman_approval,origin='YEOMAN')
    assert r['status']=='BLOCKED' and r['error']=='APPROVAL_PATH_INVALID' and r['package'] is None

    with tempfile.TemporaryDirectory(prefix='sbm-separation-') as td:
        td=Path(td)
        # QA-SEPARATION-03: package an actual scaffold; .sbm metadata is physically excluded.
        scaffold=td/'scaffold'; (scaffold/'.sbm').mkdir(parents=True); (scaffold/'input').mkdir()
        (scaffold/'.sbm/scaffold.json').write_text(json.dumps({'origin':'Yeoman'}),encoding='utf-8')
        (scaffold/'input/payload.txt').write_text('canonical payload\n',encoding='utf-8')
        r=_materialize_for_test(approved,approval,scaffold,origin='YEOMAN')
        assert r['status']=='SUCCEEDED' and r['package']
        with zipfile.ZipFile(io.BytesIO(r['package'])) as z:
            names=z.namelist()
            assert not any('.sbm/' in n or n.endswith('scaffold.json') for n in names)
            assert 'Agent/scaffold/input/payload.txt' in names

        # QA-SEPARATION-04: a provisional build/scaffolds candidate is rejected; registry remains empty.
        provisional=td/'build/scaffolds/exec-001'; provisional.mkdir(parents=True)
        (provisional/'candidate.txt').write_text('provisional\n',encoding='utf-8')
        r=_materialize_for_test(approved,approval,provisional,origin='YEOMAN')
        registry=td/'registry-candidate/context/agents'
        inc=_candidate_registry_incorporate(r,registry)
        assert r['status']=='BLOCKED' and r['error']=='PROVISIONAL_SCAFFOLD_NOT_REGISTRABLE'
        assert inc=={'status':'BLOCKED','written':False}
        assert not registry.exists() or not any(registry.rglob('*'))

        # QA-SEPARATION-05: same approved normative inputs, different origins, same pipeline => byte-identical artifact.
        canonical=td/'canonical'; canonical.mkdir(); (canonical/'payload.txt').write_text('same\n',encoding='utf-8')
        a=_materialize_for_test(copy.deepcopy(approved),copy.deepcopy(approval),canonical,origin='YEOMAN')
        b=_materialize_for_test(copy.deepcopy(approved),copy.deepcopy(approval),canonical,origin='DIRECT')
        assert a['status']==b['status']=='SUCCEEDED'
        assert a['package']==b['package']
        assert hashlib.sha256(a['package']).hexdigest()==hashlib.sha256(b['package']).hexdigest()

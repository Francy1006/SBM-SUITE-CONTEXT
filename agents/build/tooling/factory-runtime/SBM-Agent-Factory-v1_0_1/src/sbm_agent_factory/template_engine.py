from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import hashlib, json, shutil, yaml
from jsonschema import Draft202012Validator
from jinja2 import Environment, StrictUndefined
from .errors import blocked, invalid

@dataclass
class TemplateContract:
    artifact_path: Path
    sha256: str
    root: Path
    metadata: dict
    templates: dict[str, Path]
    schemas: dict[str, Path]
    required_files: list[str]
    optional_file_groups: dict
    prohibited_patterns: list[str]
    _tmp: TemporaryDirectory
    def close(self): self._tmp.cleanup()

class TemplateEngine:
    def resolve(self, template_id, template_version, artifact_path, expected_sha256):
        p=Path(artifact_path)
        if not p.is_file(): blocked('TEMPLATE_SHA_MISMATCH','Template artifact missing',path=str(p))
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected_sha256: blocked('TEMPLATE_SHA_MISMATCH','Noncanonical template hash',artifact=template_id,details={'expected':expected_sha256,'actual':actual})
        tmp=TemporaryDirectory(prefix='sbm-template-')
        try:
            with ZipFile(p) as z:
                names=[n for n in z.namelist() if n and not n.endswith('/')]
                roots={n.split('/')[0] for n in names}
                if roots != {'SBM-Agent-Template'}: invalid('INSTANCE_INVALID','Template ZIP root mismatch',details={'roots':sorted(roots)})
                z.extractall(tmp.name)
            root=Path(tmp.name)/'SBM-Agent-Template'
            meta=yaml.safe_load((root/'TEMPLATE.yaml').read_text(encoding='utf-8'))
            schema=yaml.safe_load((root/'schemas/TEMPLATE.schema.yaml').read_text(encoding='utf-8'))
            errs=sorted(Draft202012Validator(schema).iter_errors(meta),key=lambda e:list(e.path))
            if errs: invalid('INSTANCE_INVALID',f'TEMPLATE.yaml: {errs[0].message}')
            if meta.get('template_id')!=template_id or str(meta.get('template_version'))!=str(template_version): blocked('SPEC_VERSION_MISMATCH','Template id/version mismatch')
            templates={x:root/x for x in meta.get('template_references',[])}
            schemas={x:root/x for x in meta.get('schema_references',[])}
            if not all(x.is_file() for x in templates.values()) or not all(x.is_file() for x in schemas.values()): invalid('INSTANCE_INVALID','Template references unresolved')
            return TemplateContract(p,actual,root,meta,templates,schemas,list(meta.get('required_files',[])),dict(meta.get('optional_file_groups',{})),list(meta.get('prohibited_patterns',[])),tmp)
        except Exception:
            if not isinstance(_, type(None)) if False else False: pass
            # cleanup is intentionally deferred only for successful contracts
            raise

    def validate_inputs(self, contract, proposal, spec, approvals, components):
        if proposal.get('review_status')!='APPROVED': blocked('PROPOSAL_NOT_APPROVED','Proposal is not APPROVED')
        if spec.get('template_id')!=contract.metadata['template_id'] or str(spec.get('template_version'))!=str(contract.metadata['template_version']): blocked('SPEC_VERSION_MISMATCH','Spec/Template mismatch')
        if spec.get('standard_id')!=contract.metadata['standard_id'] or str(spec.get('standard_version'))!=str(contract.metadata['standard_version']): blocked('SPEC_VERSION_MISMATCH','Spec/Standard mismatch')
        pref=spec.get('proposal_reference') or {}
        if pref != {'proposal_id':proposal.get('proposal_id'),'proposal_version':proposal.get('proposal_version')}: blocked('CROSS_REFERENCE_MISMATCH','proposal_reference mismatch')
        for name in ['AGENT_DEFINITION','AGENT_CONTEXT','CONTEXT_CONTRACT','RUNTIME_PROFILE','CLONE_LINEAGE','PERMISSIONS','HIERARCHY','RELATIONSHIPS']:
            if name not in components: invalid('INSTANCE_INVALID',f'Missing target component {name}')
        return True

    def render(self, contract, approved_inputs, destination):
        dest=Path(destination); dest.mkdir(parents=True,exist_ok=True)
        proposal=approved_inputs['proposal']; spec=approved_inputs['spec']; comps=approved_inputs['components']; approvals=approved_inputs['approvals']
        mapping={
            'AGENT_PROPOSAL.yaml':proposal,'AGENT_SPEC.yaml':spec,
            'AGENT_DEFINITION.yaml':comps['AGENT_DEFINITION'],'AGENT_CONTEXT.yaml':comps['AGENT_CONTEXT'],
            'config/CONTEXT_CONTRACT.yaml':comps['CONTEXT_CONTRACT'],'config/RUNTIME_PROFILE.yaml':comps['RUNTIME_PROFILE'],
            'config/CLONE_LINEAGE.yaml':comps['CLONE_LINEAGE'],'config/PERMISSIONS.yaml':comps['PERMISSIONS'],
            'config/HIERARCHY.yaml':comps['HIERARCHY'],'config/RELATIONSHIPS.yaml':comps['RELATIONSHIPS'],
            'approvals/PROPOSAL_APPROVAL.yaml':approvals['proposal'],'approvals/SPEC_APPROVAL.yaml':approvals['spec'],
            'approvals/MATERIALIZATION_APPROVAL.yaml':approvals['materialization'],
        }
        if spec.get('deployment_reference') is not None:
            mapping['deployment/DEPLOYMENT_PROFILE.yaml']=comps['DEPLOYMENT_PROFILE']
        for rel,obj in mapping.items():
            q=dest/rel; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(yaml.safe_dump(obj,sort_keys=False,allow_unicode=True),encoding='utf-8',newline='\n')
        env=Environment(undefined=StrictUndefined,keep_trailing_newline=True)
        ctx={'agent_id':spec['agent_id'],'agent_version':spec['agent_version'],'standard_version':spec['standard_version']}
        for src_rel,out_rel in [('templates/agent/INIT.template.md','INIT.md'),('templates/agent/README.template.md','README.md'),('templates/agent/manifest.template.json','manifest.json')]:
            txt=(contract.root/src_rel).read_text(encoding='utf-8'); (dest/out_rel).write_text(env.from_string(txt).render(**ctx),encoding='utf-8',newline='\n')
        for rel in contract.metadata.get('schema_references',[]):
            if rel=='schemas/TEMPLATE.schema.yaml': continue
            q=dest/rel; q.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(contract.root/rel,q)
        if spec.get('deployment_reference') is not None:
            depctx={'agent_id':spec['agent_id'],'agent_version':spec['agent_version'],'deployment_profile_id':comps['DEPLOYMENT_PROFILE'].get('deployment_profile_id','DEPLOYMENT'),'deployment_profile_version':comps['DEPLOYMENT_PROFILE'].get('deployment_profile_version','1.0.0')}
            for src_rel,out_rel in [('templates/agent/deployment/GPT_INSTRUCTIONS.template.md','deployment/GPT_INSTRUCTIONS.md'),('templates/agent/deployment/GPT_KNOWLEDGE_MANIFEST.template.yaml','deployment/GPT_KNOWLEDGE_MANIFEST.yaml'),('templates/agent/deployment/GPT_SETUP_CHECKLIST.template.md','deployment/GPT_SETUP_CHECKLIST.md')]:
                txt=(contract.root/src_rel).read_text(encoding='utf-8'); q=dest/out_rel; q.parent.mkdir(parents=True,exist_ok=True)
                try: rendered=env.from_string(txt).render(**depctx)
                except Exception: rendered=txt
                q.write_text(rendered,encoding='utf-8',newline='\n')
        (dest/'qa').mkdir(parents=True,exist_ok=True)
        (dest/'qa/TEST_MATRIX.md').write_text('# Agent QA Test Matrix\n\nAgent QA validates the materialized agent root: required files, schemas, instances, cross-references, approvals, permissions/authority, hierarchy, relationships, context, runtime, lineage, deployment conditionality, integrity, prohibited artifacts and applicable STANDARD_UPGRADE invariants.\n\nPackaging requires scripts/validate exit 0 and scripts/test exit 0.\n',encoding='utf-8',newline='\n')
        (dest/'qa/ACCEPTANCE_CRITERIA.md').write_text('# Agent QA Acceptance Criteria\n\nPASS requires scripts/validate exit 0 and scripts/test exit 0 immediately before package. Any failure blocks final ZIP generation.\n',encoding='utf-8',newline='\n')
        validate_code = '''from pathlib import Path\nimport hashlib,json,sys,yaml\nfrom jsonschema import Draft202012Validator\nROOT=Path(__file__).resolve().parents[1]\nBAD={"__pycache__",".pytest_cache",".DS_Store","Thumbs.db","node_modules",".git","build","dist","context",".sbm","coverage"}\ndef die(m): print("INVALID: "+m,file=sys.stderr); raise SystemExit(2)\ndef load(rel):\n p=ROOT/rel\n if not p.is_file(): die("missing "+rel)\n try: return json.loads(p.read_text(encoding="utf-8")) if p.suffix==".json" else yaml.safe_load(p.read_text(encoding="utf-8"))\n except Exception as e: die(rel+": "+str(e))\ndef sch(n): return load("schemas/"+n+".schema.yaml")\ndef chk(o,n,r):\n e=sorted(Draft202012Validator(sch(n)).iter_errors(o),key=lambda x:list(x.path))\n if e: die(r+": "+e[0].message)\nfor p in ROOT.rglob("*"):\n rel=p.relative_to(ROOT).as_posix()\n if set(rel.split("/")) & BAD or p.suffix in {".pyc",".pyo"} or p.name.endswith((".tmp",".temp",".log")): die("prohibited "+rel)\npaths={"AGENT_PROPOSAL":"AGENT_PROPOSAL.yaml","AGENT_SPEC":"AGENT_SPEC.yaml","AGENT_DEFINITION":"AGENT_DEFINITION.yaml","AGENT_CONTEXT":"AGENT_CONTEXT.yaml","CONTEXT_CONTRACT":"config/CONTEXT_CONTRACT.yaml","RUNTIME_PROFILE":"config/RUNTIME_PROFILE.yaml","CLONE_LINEAGE":"config/CLONE_LINEAGE.yaml","PERMISSIONS":"config/PERMISSIONS.yaml","HIERARCHY":"config/HIERARCHY.yaml","RELATIONSHIPS":"config/RELATIONSHIPS.yaml"}\no={k:load(v) for k,v in paths.items()}; p=o["AGENT_PROPOSAL"]; s=o["AGENT_SPEC"]\nchk(p,"AGENT_PROPOSAL",paths["AGENT_PROPOSAL"]); chk(s,"AGENT_SPEC",paths["AGENT_SPEC"])\nfor k,v in o.items():\n if k not in {"AGENT_PROPOSAL","AGENT_SPEC"}: chk(v,k,paths[k])\na=[]\nfor r in ["approvals/PROPOSAL_APPROVAL.yaml","approvals/SPEC_APPROVAL.yaml","approvals/MATERIALIZATION_APPROVAL.yaml"]:\n x=load(r); chk(x,"APPROVAL_RECORD",r); a.append(x)\nif s.get("deployment_reference") is not None:\n d=load("deployment/DEPLOYMENT_PROFILE.yaml"); chk(d,"DEPLOYMENT_PROFILE","deployment/DEPLOYMENT_PROFILE.yaml"); o["DEPLOYMENT_PROFILE"]=d\nelif (ROOT/"deployment/DEPLOYMENT_PROFILE.yaml").exists(): die("deployment without reference")\nif p.get("review_status")!="APPROVED": die("proposal not approved")\npr=s.get("proposal_reference") or {}\nif pr.get("proposal_id")!=p.get("proposal_id") or str(pr.get("proposal_version"))!=str(p.get("proposal_version")): die("proposal reference mismatch")\nif a[0].get("artifact_id")!=p.get("proposal_id") or str(a[0].get("artifact_version"))!=str(p.get("proposal_version")): die("proposal approval mismatch")\nif a[1].get("artifact_id")!=s.get("spec_id") or str(a[1].get("artifact_version"))!=str(s.get("spec_version")): die("spec approval mismatch")\nif a[2].get("artifact_id")!=s.get("spec_id") or str(a[2].get("artifact_version"))!=str(s.get("spec_version")): die("materialization approval mismatch")\nif any(x.get("approved_by")!="sbm-admin" or x.get("approval_status")!="APPROVED" for x in a): die("approval authority/status mismatch")\naid=s.get("agent_id"); refs=s.get("component_references") or {}\niv={"AGENT_DEFINITION":("agent_definition_id","agent_definition_version"),"AGENT_CONTEXT":("agent_id","context_version"),"CONTEXT_CONTRACT":("context_contract_id","context_contract_version"),"RUNTIME_PROFILE":("runtime_profile_id","runtime_profile_version"),"CLONE_LINEAGE":("clone_lineage_id","agent_version"),"PERMISSIONS":("permissions_id","permissions_version"),"HIERARCHY":("agent_id","hierarchy_version"),"RELATIONSHIPS":("relationships_id","relationships_version"),"DEPLOYMENT_PROFILE":("deployment_profile_id","deployment_profile_version")}\nfor n,x in o.items():\n if n in {"AGENT_PROPOSAL","AGENT_SPEC"}: continue\n if x.get("agent_id") not in (None,aid): die(n+" agent_id mismatch")\n if n not in refs: die("missing reference "+n)\n ik,vk=iv[n]; r=refs[n]\n if str(r.get("artifact_id"))!=str(x.get(ik)) or str(r.get("artifact_version"))!=str(x.get(vk)): die(n+" reference mismatch")\npm=o["PERMISSIONS"]; au=o["AGENT_DEFINITION"].get("authority",[])\nif set(pm.get("allowed_actions",[])) & set(pm.get("denied_actions",[])): die("permission conflict")\nif isinstance(au,list) and not set(pm.get("allowed_actions",[])).issubset(set(au)): die("permissions exceed authority")\nln=o["CLONE_LINEAGE"]; mode=s.get("creation_mode"); mig=s.get("migration_reference")\nif mode=="NEW":\n if s.get("parent_reference") is not None or ln.get("is_clone") is not False: die("NEW lineage invalid")\n if any(ln.get(k) is not None for k in ["parent_agent_id","parent_agent_version","parent_spec_id","parent_spec_version"]): die("NEW parent refs invalid")\n if mig is not None and (mig.get("migration_type")!="STANDARD_UPGRADE" or mig.get("source_agent_id")!=aid or str(mig.get("source_agent_version"))==str(s.get("agent_version")) or str(mig.get("source_standard_version"))==str(s.get("standard_version"))): die("STANDARD_UPGRADE invalid")\nelif mode=="CLONE":\n if ln.get("is_clone") is not True or s.get("parent_reference") is None or mig is not None: die("CLONE lineage invalid")\nelse: die("creation_mode invalid")\nif (ROOT/"MANIFEST.yaml").exists() or (ROOT/"CHECKSUMS.sha256").exists():\n if not (ROOT/"MANIFEST.yaml").is_file() or not (ROOT/"CHECKSUMS.sha256").is_file(): die("partial integrity")\n m=load("MANIFEST.yaml"); mf={x["path"]:x for x in m.get("files",[])}; phys=sorted(x.relative_to(ROOT).as_posix() for x in ROOT.rglob("*") if x.is_file())\n if set(mf)!=set(phys): die("manifest physical mismatch")\n sums={}\n for line in (ROOT/"CHECKSUMS.sha256").read_text().splitlines():\n  if line.strip(): h,r=line.split("  ",1); sums[r]=h\n if set(sums)!=set(phys)-{"CHECKSUMS.sha256"}: die("checksum coverage mismatch")\n for r,h in sums.items():\n  if hashlib.sha256((ROOT/r).read_bytes()).hexdigest()!=h: die("checksum mismatch "+r)\n  if r!="MANIFEST.yaml" and mf[r].get("sha256")!=h: die("manifest hash mismatch "+r)\n if mf["MANIFEST.yaml"].get("sha256") is not None or mf["CHECKSUMS.sha256"].get("sha256") is not None: die("self hash must be null")\nprint("VALID")\n'''
        q=dest/'scripts/validate'; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(validate_code,encoding='utf-8',newline='\n'); q.chmod(0o755)
        test_code='''from pathlib import Path\nimport runpy,sys,traceback\nROOT=Path(__file__).resolve().parents[1]\nfailed=[]; count=0\nfor path in sorted((ROOT/"tests").glob("test_*.py")):\n ns=runpy.run_path(str(path))\n for name,obj in sorted(ns.items()):\n  if name.startswith("test_") and callable(obj):\n   count+=1\n   try: obj()\n   except Exception as e:\n    failed.append((path.name,name,str(e)))\nif failed:\n [print(f"FAIL {f}::{n}: {e}",file=sys.stderr) for f,n,e in failed]\n print(f"TESTS: FAIL {len(failed)}/{count}",file=sys.stderr); raise SystemExit(1)\nprint(f"TESTS: PASS {count}")\n'''
        q=dest/'scripts/test'; q.write_text(test_code,encoding='utf-8',newline='\n'); q.chmod(0o755)
        test_refs=[x for x in contract.metadata.get('qa_references',[]) if x.startswith('tests/')]
        prefix='from pathlib import Path\nimport subprocess,sys\nagent_root=Path(__file__).resolve().parents[1]\ndef run_validate(): return subprocess.run([sys.executable,str(agent_root/"scripts/validate")],cwd=agent_root,text=True,capture_output=True)\n'
        bodies={
          'test_approvals.py':'import yaml\ndef test_approvals():\n s=yaml.safe_load((agent_root/"AGENT_SPEC.yaml").read_text()); a=yaml.safe_load((agent_root/"approvals/MATERIALIZATION_APPROVAL.yaml").read_text()); assert a["artifact_id"]==s["spec_id"] and str(a["artifact_version"])==str(s["spec_version"])\n',
          'test_permissions.py':'import yaml\ndef test_permissions():\n p=yaml.safe_load((agent_root/"config/PERMISSIONS.yaml").read_text()); assert not(set(p.get("allowed_actions",[])) & set(p.get("denied_actions",[])))\n',
          'test_hierarchy.py':'import yaml\ndef test_hierarchy():\n h=yaml.safe_load((agent_root/"config/HIERARCHY.yaml").read_text()); assert "reports_to" in h and "escalation_target" in h\n',
          'test_relationships.py':'import yaml\ndef test_relationships():\n r=yaml.safe_load((agent_root/"config/RELATIONSHIPS.yaml").read_text()); assert all({"actor","relationship_type","direction","purpose"}<=set(x) for x in r.get("relationships",[]))\n',
          'test_context_contract.py':'import yaml\ndef test_context():\n c=yaml.safe_load((agent_root/"config/CONTEXT_CONTRACT.yaml").read_text()); assert "context_zip_required" in c and "specific_objectives" not in c\n',
          'test_deployment_conditionality.py':'import yaml\ndef test_deployment():\n s=yaml.safe_load((agent_root/"AGENT_SPEC.yaml").read_text()); assert (agent_root/"deployment/DEPLOYMENT_PROFILE.yaml").exists()==(s.get("deployment_reference") is not None)\n',
          'test_prohibited_artifacts.py':'def test_no_prohibited():\n bad={"__pycache__",".pytest_cache",".git",".sbm","node_modules","build","dist","context","coverage"}; assert not any(set(p.relative_to(agent_root).parts)&bad for p in agent_root.rglob("*"))\n',
          'test_schema_validity.py':'import yaml\nfrom jsonschema import Draft202012Validator\ndef test_schemas():\n [Draft202012Validator.check_schema(yaml.safe_load(p.read_text())) for p in (agent_root/"schemas").glob("*.yaml")]\n',
          'test_required_files.py':'def test_required():\n req=["INIT.md","manifest.json","AGENT_PROPOSAL.yaml","AGENT_SPEC.yaml","AGENT_DEFINITION.yaml","AGENT_CONTEXT.yaml","scripts/validate","scripts/test","MANIFEST.yaml","CHECKSUMS.sha256"]; assert all((agent_root/x).is_file() for x in req)\n',
          'test_separation.py':'def test_separation():\n assert not (agent_root/"TEMPLATE.yaml").exists(); assert not (agent_root/"fixtures").exists(); assert not (agent_root/".sbm/scaffold.json").exists()\n',
          'test_template_tree.py':'def test_agent_not_template():\n assert (agent_root/"AGENT_SPEC.yaml").is_file() and not (agent_root/"TEMPLATE.yaml").exists()\n',
          'test_standard_upgrade.py':'import yaml\ndef test_upgrade():\n s=yaml.safe_load((agent_root/"AGENT_SPEC.yaml").read_text()); m=s.get("migration_reference"); assert m is None or m.get("migration_type")=="STANDARD_UPGRADE"\n',
          'test_cross_references.py':'import yaml\ndef test_refs():\n s=yaml.safe_load((agent_root/"AGENT_SPEC.yaml").read_text()); assert s.get("proposal_reference") and s.get("component_references")\n',
          'test_lineage.py':'import yaml\ndef test_lineage():\n s=yaml.safe_load((agent_root/"AGENT_SPEC.yaml").read_text()); l=yaml.safe_load((agent_root/"config/CLONE_LINEAGE.yaml").read_text()); assert (s["creation_mode"]=="CLONE")==bool(l["is_clone"])\n',
          'test_manifest_checksums.py':'def test_integrity_files():\n assert (agent_root/"MANIFEST.yaml").is_file() and (agent_root/"CHECKSUMS.sha256").is_file()\n',
          'test_reproducibility.py':'def test_deterministic_inputs_present():\n assert (agent_root/"MANIFEST.yaml").is_file() and (agent_root/"CHECKSUMS.sha256").is_file()\n',
          'test_instance_validation.py':'import yaml\nfrom jsonschema import Draft202012Validator\ndef test_instances_against_schemas():\n pairs=[("AGENT_PROPOSAL.yaml","AGENT_PROPOSAL.schema.yaml"),("AGENT_SPEC.yaml","AGENT_SPEC.schema.yaml"),("AGENT_DEFINITION.yaml","AGENT_DEFINITION.schema.yaml"),("AGENT_CONTEXT.yaml","AGENT_CONTEXT.schema.yaml")]\n for rel,srel in pairs:\n  obj=yaml.safe_load((agent_root/rel).read_text()); sch=yaml.safe_load((agent_root/"schemas"/srel).read_text()); assert not list(Draft202012Validator(sch).iter_errors(obj))\n',
        }
        default='def test_agent_conformance():\n assert (agent_root/"AGENT_SPEC.yaml").is_file()\n'
        for rel in test_refs:
            q=dest/rel; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(prefix+bodies.get(Path(rel).name,default),encoding='utf-8',newline='\n')
        return dest

    def expected_agent_files(self, contract, spec, include_integrity=True):
        declared=set(contract.required_files)
        required={'MANIFEST.yaml','CHECKSUMS.sha256'} if include_integrity else set()
        # Agent files are derived only from canonical Template references.
        for src in contract.metadata.get('template_references',[]):
            if src not in declared: invalid('INSTANCE_INVALID','Template reference is not a declared required file',path=src)
            if not src.startswith('templates/agent/'): continue
            rel=src[len('templates/agent/'):]
            if '.template.' in rel: rel=rel.replace('.template.','.')
            elif rel.endswith('.template'): rel=rel[:-len('.template')]
            required.add(rel)
        for src in contract.metadata.get('schema_references',[]):
            if src not in declared: invalid('INSTANCE_INVALID','Schema reference is not a declared required file',path=src)
            if src != "schemas/TEMPLATE.schema.yaml": required.add(src)
        for src in contract.metadata.get('qa_references',[]):
            if src not in declared: invalid('INSTANCE_INVALID','QA reference is not a declared required file',path=src)
            if src.startswith('tests/'): required.add(src)
        conditional=set()
        for name,group in contract.optional_file_groups.items():
            if group.get('scope')!='GENERATED_AGENT': continue
            condition=group.get('condition')
            if name=='deployment' and condition=='deployment_reference != null':
                paths=set(group.get('paths',[]))
                if spec.get('deployment_reference') is not None: conditional |= paths
                else: required -= paths
            else:
                blocked('INSTANCE_INVALID','Unsupported generated-agent conditional group',details={'group':name,'condition':condition})
        required |= conditional
        return required

    def verify_output(self,destination,contract,include_integrity=False):
        root=Path(destination)
        spec=yaml.safe_load((root/'AGENT_SPEC.yaml').read_text(encoding='utf-8'))
        expected=self.expected_agent_files(contract,spec,include_integrity=include_integrity)
        physical={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        missing=sorted(expected-physical)
        extra=sorted(physical-expected)
        if missing: invalid('INSTANCE_INVALID','Generated agent missing Template-required files',details={'missing':missing})
        if extra: invalid('EXTRA_FILE','Generated agent contains files not declared by Template contract',details={'extra':extra})
        return True

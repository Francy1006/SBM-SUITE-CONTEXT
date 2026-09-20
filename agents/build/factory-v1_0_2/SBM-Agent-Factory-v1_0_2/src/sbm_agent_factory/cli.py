import argparse,sys,yaml
from pathlib import Path
from .errors import FactoryError,EXIT_CODES
from .create import create_agent
from .clone import clone_agent
from .validate import validate_factory_config,validate_workspace,validate_agent_workspace
from .qa import run_tests
from .documentation import generate_docs
from .authorization import verify_authorization

def config_from_here():
    root=Path(__file__).resolve().parents[2]; return yaml.safe_load((root/'config/FACTORY_CONFIG.yaml').read_text())
def main(argv=None):
    p=argparse.ArgumentParser(prog='sbm-agent'); sp=p.add_subparsers(dest='cmd',required=True)
    for name in ['create','clone']:
        q=sp.add_parser(name)
        for a in ['proposal','proposal-approval','spec','spec-approval','materialization-approval','template','output-dir','orchestrator-authorization','build-approval-event','approved-proposal-projection','execution-id','reservation-id']: q.add_argument('--'+a,required=True)
        if name=='clone': q.add_argument('--parent',required=True)
    q=sp.add_parser('validate'); q.add_argument('--root',default='.')
    q=sp.add_parser('test'); q.add_argument('--root',default='.')
    q=sp.add_parser('package'); q.add_argument('--root',required=True); q.add_argument('--template',required=True); q.add_argument('--output',required=True)
    q=sp.add_parser('docs'); q.add_argument('--root',required=True); q.add_argument('--spec',required=True)
    a=p.parse_args(argv); cfg=config_from_here()
    try:
        if a.cmd in {'create','clone'}:
            verify_authorization(a.orchestrator_authorization,a.build_approval_event,a.approved_proposal_projection,a.spec,a.template,a.execution_id,a.reservation_id)
        if a.cmd=='create': create_agent(a.proposal,a.proposal_approval,a.spec,a.spec_approval,a.materialization_approval,a.template,a.output_dir,cfg)
        elif a.cmd=='clone': clone_agent(a.proposal,a.proposal_approval,a.spec,a.spec_approval,a.materialization_approval,a.parent,a.template,a.output_dir,cfg)
        elif a.cmd=='validate': validate_workspace(a.root); print('VALID')
        elif a.cmd=='test':
            r=run_tests(a.root); print(r.stdout,end=''); print(r.stderr,end='',file=sys.stderr); return r.returncode
        elif a.cmd=='package':
            from .package import package_workspace
            from .template_engine import TemplateEngine
            engine=TemplateEngine(); contract=engine.resolve(cfg['template_id'],cfg['template_version'],a.template,cfg['canonical_template_sha256'])
            try:
                if str(contract.metadata.get('standard_version'))!=str(cfg['standard_version']):
                    from .errors import blocked
                    blocked('SPEC_VERSION_MISMATCH','Template Standard version mismatch')
                package_workspace(a.root,a.output,arc_root=Path(a.root).name,compresslevel=cfg['zip_compresslevel'],template_contract=contract)
            finally:
                contract.close()
        elif a.cmd=='docs':
            s=yaml.safe_load(Path(a.spec).read_text()); generate_docs(a.root,s)
        return 0
    except FactoryError as e:
        print(str(e),file=sys.stderr); return EXIT_CODES.get(e.status,4)
if __name__=='__main__': raise SystemExit(main())

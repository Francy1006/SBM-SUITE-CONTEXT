from pathlib import Path

def generate_docs(root,spec):
    root=Path(root)
    docs={'README.md':f"# {spec['agent_id']}\n\nVersion {spec['agent_version']}\n",'REGISTRY.md':f"# Registry\n\n{spec['agent_id']} {spec['agent_version']}\n",'VERSION_MATRIX.md':f"# Version Matrix\n\nStandard {spec['standard_version']} / Template {spec['template_version']}\n"}
    for n,c in docs.items(): (root/n).write_text(c,encoding='utf-8',newline='\n')
    return sorted(docs)

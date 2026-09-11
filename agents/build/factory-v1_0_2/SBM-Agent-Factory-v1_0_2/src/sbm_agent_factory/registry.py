from pathlib import Path
import yaml

def make_candidate(agent, package_path, package_sha256, factory_config, context_path='context/agents'):
    return {
        'agent_id':agent['agent_id'],
        'agent_name':agent.get('agent_name',agent['agent_id']),
        'description':agent.get('description',''),
        'agent_version':agent['agent_version'],
        'spec_version':agent.get('spec_version','1.0.0'),
        'standard_version':agent['standard_version'],
        'factory_id':factory_config['factory_id'],
        'factory_version':factory_config['factory_version'],
        'template_id':factory_config['template_id'],
        'template_version':agent['template_version'],
        'template_sha256':factory_config['canonical_template_sha256'],
        'status':'CANDIDATE',
        'deployment_targets':agent.get('deployment_targets',[]),
        'package_path':str(package_path),
        'package_sha256':package_sha256,
        'context_path':context_path,
        'updated_at':'1980-01-01T00:00:00Z',
    }
def write_candidate(path,data): Path(path).write_text(yaml.safe_dump(data,sort_keys=False),encoding='utf-8',newline='\n')

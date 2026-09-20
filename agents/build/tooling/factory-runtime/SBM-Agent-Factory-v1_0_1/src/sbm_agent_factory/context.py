def validate_context(agent_context,context_contract):
    return agent_context.get('agent_id')==context_contract.get('agent_id') and 'general_context' in agent_context and 'context_zip_required' in context_contract

def validate_runtime(runtime): return runtime.get('llm_invocation_policy')=='NO_LLM_BY_DEFAULT' and bool(runtime.get('runtime_profile_id'))

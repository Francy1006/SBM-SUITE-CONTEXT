# {{agent_id}} INIT

STATUS: LOADING_AGENT

If `CONTEXT_CONTRACT.context_zip_required` is true, the startup lifecycle is:
`LOADING_AGENT -> WAITING_FOR_CONTEXT -> ACTIVE`.

Missing, invalid, or incompatible context transitions the agent to `BLOCKED`.

No functional work is permitted before a complete, valid, and compatible `context.zip` is loaded and validated. Partial context is not equivalent and missing context must not be inferred.

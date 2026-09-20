import json


class OrchestratorError(RuntimeError):
    def __init__(self, code, message, *, status="BLOCKED", details=None):
        self.code = code
        self.status = status
        self.details = details or {}
        super().__init__(message)

    def __str__(self):
        return json.dumps(
            {"code": self.code, "status": self.status, "message": super().__str__(), "details": self.details},
            sort_keys=True,
        )

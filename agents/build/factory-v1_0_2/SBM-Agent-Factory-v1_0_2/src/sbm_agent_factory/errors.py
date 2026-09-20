from dataclasses import dataclass, asdict
import json

EXIT_CODES={"SUCCEEDED":0,"INVALID":2,"BLOCKED":3,"FAILED":4}

@dataclass
class FactoryError(Exception):
    code:str
    status:str
    message:str
    artifact:str|None=None
    path:str|None=None
    details:dict|None=None
    remediation:str|None=None
    def to_dict(self): return asdict(self)
    def __str__(self): return json.dumps(self.to_dict(), sort_keys=True)

def invalid(code,message,**kw): raise FactoryError(code,"INVALID",message,**kw)
def blocked(code,message,**kw): raise FactoryError(code,"BLOCKED",message,**kw)

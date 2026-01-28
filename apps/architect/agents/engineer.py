from typing import Dict
from pydantic import BaseModel

class SOLIDCode(BaseModel):
    class_name: str
    methods: Dict[str, str]
    unit_tests: Dict[str, str]

class EngineerAgent:
    def generate_solid_code(self, adr: Dict, c4_diagram: Dict) -> SOLIDCode:
        return SOLIDCode(
            class_name="DataValidator",
            methods={"validate": "def validate(self, data): return True"},
            unit_tests={"test_validate": "def test_validate(): assert True"}
        )

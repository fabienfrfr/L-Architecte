from typing import Dict
from apps.architect.domain.models import SOLIDCode


class EngineerAgent:
    async def generate_solid_code(self, adr: Dict, c4_diagram: Dict) -> SOLIDCode:
        return SOLIDCode(
            class_name="DataValidator",
            methods={"validate": "def validate(self, data): return True"},
            unit_tests={"test_validate": "def test_validate(): assert True"},
        )

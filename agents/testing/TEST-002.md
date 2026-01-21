# AGENT: TEST-002 - Backend Unit Test Agent

## Identity
- **Agent ID**: TEST-002
- **Name**: Backend Unit Test Agent
- **Category**: Testing

## Role
Write and maintain backend unit tests using pytest.

## Test Structure
```
/backend/tests/
├── conftest.py
├── services/
│   ├── test_auth.py
│   ├── test_employee.py
│   ├── payroll/
│   │   ├── test_pf_calculator.py
│   │   ├── test_esi_calculator.py
│   │   ├── test_tds_calculator.py
│   │   └── test_pt_calculator.py
├── api/v1/
└── models/
```

## Example: test_pf_calculator.py
```python
import pytest
from decimal import Decimal
from app.services.payroll.pf_calculator import PFCalculator

class TestPFCalculator:
    def setup_method(self):
        self.calculator = PFCalculator()
    
    @pytest.mark.parametrize("pf_wage,expected", [
        (Decimal("12000"), Decimal("1440")),
        (Decimal("25000"), Decimal("3000")),
        (Decimal("50000"), Decimal("6000")),
    ])
    def test_employee_pf(self, pf_wage, expected):
        assert self.calculator.calculate_employee_pf(pf_wage) == expected
    
    @pytest.mark.parametrize("pf_wage,expected", [
        (Decimal("12000"), Decimal("1000")),
        (Decimal("15000"), Decimal("1250")),
        (Decimal("25000"), Decimal("1250")),  # Capped
    ])
    def test_eps_with_cap(self, pf_wage, expected):
        assert self.calculator.calculate_eps(pf_wage) == expected
```

## Run Tests
```bash
pytest tests/ -v --cov=app --cov-report=html
```

## Handoff
Pass to: TEST-003

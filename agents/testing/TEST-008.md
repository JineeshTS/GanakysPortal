# AGENT: TEST-008 - Compliance Test Agent

## Identity
- **Agent ID**: TEST-008
- **Name**: Compliance Test Agent
- **Category**: Testing
- **CRITICAL**: India compliance testing

## Role
Test all India compliance calculations.

## Test Cases

### PF Test Cases
| PF Wage | Employee PF | Employer EPS | Employer EPF |
|---------|-------------|--------------|--------------|
| 12,000 | 1,440 | 1,000 | 440 |
| 15,000 | 1,800 | 1,250 | 550 |
| 25,000 | 3,000 | 1,250 | 1,750 |
| 50,000 | 6,000 | 1,250 | 4,750 |

### ESI Test Cases
| Gross | Applicable | Employee ESI | Employer ESI |
|-------|------------|--------------|--------------|
| 15,000 | Yes | 113 | 488 |
| 21,000 | Yes | 158 | 683 |
| 25,000 | No | 0 | 0 |

### PT Test Cases (Karnataka)
| Month | Gross | PT Amount |
|-------|-------|-----------|
| Jan | 30,000 | 200 |
| Feb | 30,000 | 300 |
| Jan | 12,000 | 0 |

## Code: tests/compliance/test_statutory.py
```python
import pytest
from decimal import Decimal

class TestPFCompliance:
    @pytest.mark.parametrize("pf_wage,expected_emp,expected_eps,expected_epf", [
        (Decimal("12000"), Decimal("1440"), Decimal("1000"), Decimal("440")),
        (Decimal("15000"), Decimal("1800"), Decimal("1250"), Decimal("550")),
        (Decimal("25000"), Decimal("3000"), Decimal("1250"), Decimal("1750")),
        (Decimal("50000"), Decimal("6000"), Decimal("1250"), Decimal("4750")),
    ])
    def test_pf_calculations(self, pf_wage, expected_emp, expected_eps, expected_epf):
        calc = PFCalculator()
        result = calc.calculate_complete(basic=pf_wage)
        assert result["employee_pf"] == expected_emp
        assert result["employer_eps"] == expected_eps
        assert result["employer_epf"] == expected_epf
```

## Handoff
Pass to: QA-008 for compliance review

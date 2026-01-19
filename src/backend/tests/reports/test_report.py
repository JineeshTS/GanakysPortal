"""
TEST-012: Test Coverage Reporter
Generate comprehensive test reports
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import json


class TestStatus(str, Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    module: str
    status: TestStatus
    duration_ms: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Test suite result."""
    name: str
    tests: List[TestResult] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: float = 0


@dataclass
class CoverageReport:
    """Code coverage report."""
    lines_total: int
    lines_covered: int
    lines_percentage: float
    branches_total: int
    branches_covered: int
    branches_percentage: float
    functions_total: int
    functions_covered: int
    functions_percentage: float
    files: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class TestReport:
    """Complete test report."""
    project: str
    timestamp: datetime
    duration_ms: float
    suites: List[TestSuiteResult]
    coverage: CoverageReport
    summary: Dict[str, Any]


class TestReportGenerator:
    """Generate test reports in various formats."""

    def __init__(self):
        self.suites: List[TestSuiteResult] = []
        self.coverage: Optional[CoverageReport] = None

    def add_suite(self, suite: TestSuiteResult) -> None:
        """Add test suite result."""
        self.suites.append(suite)

    def set_coverage(self, coverage: CoverageReport) -> None:
        """Set coverage report."""
        self.coverage = coverage

    def generate_report(self) -> TestReport:
        """Generate complete test report."""
        total_tests = sum(s.total for s in self.suites)
        total_passed = sum(s.passed for s in self.suites)
        total_failed = sum(s.failed for s in self.suites)
        total_skipped = sum(s.skipped for s in self.suites)
        total_duration = sum(s.duration_ms for s in self.suites)

        return TestReport(
            project="GanaPortal",
            timestamp=datetime.utcnow(),
            duration_ms=total_duration,
            suites=self.suites,
            coverage=self.coverage,
            summary={
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "coverage_line": self.coverage.lines_percentage if self.coverage else 0,
                "coverage_branch": self.coverage.branches_percentage if self.coverage else 0,
            }
        )

    def to_json(self) -> str:
        """Export report as JSON."""
        report = self.generate_report()
        return json.dumps({
            "project": report.project,
            "timestamp": report.timestamp.isoformat(),
            "duration_ms": report.duration_ms,
            "summary": report.summary,
            "suites": [
                {
                    "name": s.name,
                    "total": s.total,
                    "passed": s.passed,
                    "failed": s.failed,
                    "skipped": s.skipped,
                    "duration_ms": s.duration_ms,
                }
                for s in report.suites
            ],
            "coverage": {
                "lines": report.coverage.lines_percentage,
                "branches": report.coverage.branches_percentage,
                "functions": report.coverage.functions_percentage,
            } if report.coverage else None,
        }, indent=2)

    def to_markdown(self) -> str:
        """Export report as Markdown."""
        report = self.generate_report()
        lines = [
            f"# Test Report - {report.project}",
            f"",
            f"**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Duration:** {report.duration_ms:.2f}ms",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Tests | {report.summary['total_tests']} |",
            f"| Passed | {report.summary['passed']} ✅ |",
            f"| Failed | {report.summary['failed']} ❌ |",
            f"| Skipped | {report.summary['skipped']} ⏭️ |",
            f"| Pass Rate | {report.summary['pass_rate']:.1f}% |",
            f"",
        ]

        if report.coverage:
            lines.extend([
                f"## Coverage",
                f"",
                f"| Metric | Coverage |",
                f"|--------|----------|",
                f"| Lines | {report.coverage.lines_percentage:.1f}% |",
                f"| Branches | {report.coverage.branches_percentage:.1f}% |",
                f"| Functions | {report.coverage.functions_percentage:.1f}% |",
                f"",
            ])

        lines.extend([
            f"## Test Suites",
            f"",
        ])

        for suite in report.suites:
            status_icon = "✅" if suite.failed == 0 else "❌"
            lines.append(f"### {status_icon} {suite.name}")
            lines.append(f"")
            lines.append(f"- Total: {suite.total}")
            lines.append(f"- Passed: {suite.passed}")
            lines.append(f"- Failed: {suite.failed}")
            lines.append(f"- Duration: {suite.duration_ms:.2f}ms")
            lines.append(f"")

        return "\n".join(lines)


# Sample test execution results for GanaPortal
def generate_sample_report() -> TestReport:
    """Generate sample test report for GanaPortal."""
    generator = TestReportGenerator()

    # Backend Unit Tests
    generator.add_suite(TestSuiteResult(
        name="Backend Unit Tests",
        total=145,
        passed=142,
        failed=2,
        skipped=1,
        duration_ms=8500
    ))

    # Backend Integration Tests
    generator.add_suite(TestSuiteResult(
        name="Backend Integration Tests",
        total=68,
        passed=65,
        failed=2,
        skipped=1,
        duration_ms=15000
    ))

    # Compliance Tests
    generator.add_suite(TestSuiteResult(
        name="Statutory Compliance Tests",
        total=42,
        passed=42,
        failed=0,
        skipped=0,
        duration_ms=3200
    ))

    # Security Tests
    generator.add_suite(TestSuiteResult(
        name="Security Tests",
        total=35,
        passed=34,
        failed=1,
        skipped=0,
        duration_ms=5600
    ))

    # Performance Tests
    generator.add_suite(TestSuiteResult(
        name="Performance Tests",
        total=18,
        passed=17,
        failed=1,
        skipped=0,
        duration_ms=25000
    ))

    # Frontend Unit Tests
    generator.add_suite(TestSuiteResult(
        name="Frontend Unit Tests",
        total=92,
        passed=89,
        failed=2,
        skipped=1,
        duration_ms=12000
    ))

    # E2E Tests
    generator.add_suite(TestSuiteResult(
        name="E2E Tests",
        total=28,
        passed=26,
        failed=1,
        skipped=1,
        duration_ms=45000
    ))

    # Coverage
    generator.set_coverage(CoverageReport(
        lines_total=15000,
        lines_covered=12450,
        lines_percentage=83.0,
        branches_total=3200,
        branches_covered=2368,
        branches_percentage=74.0,
        functions_total=850,
        functions_covered=714,
        functions_percentage=84.0
    ))

    return generator.generate_report()


if __name__ == "__main__":
    generator = TestReportGenerator()
    # Add sample data
    generator.add_suite(TestSuiteResult(
        name="Unit Tests",
        total=100,
        passed=95,
        failed=3,
        skipped=2,
        duration_ms=5000
    ))
    generator.set_coverage(CoverageReport(
        lines_total=10000,
        lines_covered=8000,
        lines_percentage=80.0,
        branches_total=2000,
        branches_covered=1400,
        branches_percentage=70.0,
        functions_total=500,
        functions_covered=400,
        functions_percentage=80.0
    ))

    print(generator.to_markdown())

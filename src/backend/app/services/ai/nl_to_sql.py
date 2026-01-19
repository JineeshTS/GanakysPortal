"""
AI-005: Natural Language to SQL Service
Convert natural language queries to SQL
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class QueryIntent(str, Enum):
    """Query intent types."""
    SELECT = "select"
    AGGREGATE = "aggregate"
    COMPARE = "compare"
    TREND = "trend"
    FILTER = "filter"


@dataclass
class SQLGenerationResult:
    """SQL generation result."""
    sql: str
    intent: QueryIntent
    tables_used: List[str]
    columns_used: List[str]
    filters: Dict[str, Any]
    confidence: float
    explanation: str
    is_safe: bool
    warnings: List[str]


class NLToSQLService:
    """
    Convert natural language questions to SQL queries.

    Features:
    - Natural language understanding
    - Schema-aware query generation
    - SQL injection prevention
    - Query explanation
    - Indian business context (INR, fiscal year, etc.)
    """

    # Database schema for context
    SCHEMA = {
        "employees": {
            "columns": ["id", "employee_id", "first_name", "last_name", "email",
                       "department_id", "designation", "salary", "date_of_joining",
                       "status", "created_at"],
            "description": "Employee master data"
        },
        "departments": {
            "columns": ["id", "name", "code", "head_id", "budget"],
            "description": "Company departments"
        },
        "payroll_runs": {
            "columns": ["id", "month", "year", "status", "total_gross", "total_net",
                       "total_pf", "total_esi", "total_tds", "processed_at"],
            "description": "Monthly payroll processing"
        },
        "payroll_items": {
            "columns": ["id", "payroll_run_id", "employee_id", "basic", "hra",
                       "allowances", "gross", "pf", "esi", "tds", "deductions", "net"],
            "description": "Individual payroll records"
        },
        "leave_requests": {
            "columns": ["id", "employee_id", "leave_type", "start_date", "end_date",
                       "days", "status", "approved_by"],
            "description": "Employee leave requests"
        },
        "invoices": {
            "columns": ["id", "invoice_number", "customer_id", "invoice_date",
                       "due_date", "subtotal", "tax_amount", "total", "status"],
            "description": "Sales invoices"
        },
        "customers": {
            "columns": ["id", "name", "gstin", "email", "phone", "city", "state"],
            "description": "Customer master"
        },
        "expenses": {
            "columns": ["id", "date", "category", "description", "amount",
                       "vendor", "status", "approved_by"],
            "description": "Company expenses"
        },
    }

    # Common business query patterns
    QUERY_PATTERNS = {
        "total employees": "SELECT COUNT(*) as total_employees FROM employees WHERE status = 'active'",
        "department wise count": "SELECT d.name, COUNT(e.id) as count FROM employees e JOIN departments d ON e.department_id = d.id GROUP BY d.name",
        "salary expense": "SELECT SUM(salary) as total_salary FROM employees WHERE status = 'active'",
        "top earners": "SELECT first_name, last_name, salary FROM employees ORDER BY salary DESC LIMIT 10",
        "pending leaves": "SELECT * FROM leave_requests WHERE status = 'pending'",
        "outstanding invoices": "SELECT * FROM invoices WHERE status = 'pending' AND due_date < CURRENT_DATE",
    }

    # Dangerous SQL patterns to block
    DANGEROUS_PATTERNS = [
        "drop", "delete", "truncate", "update", "insert", "alter", "create",
        "grant", "revoke", "exec", "execute", "--", "/*", "*/"
    ]

    def __init__(self, ai_service=None):
        """Initialize with optional AI service."""
        self.ai_service = ai_service

    async def generate_sql(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SQLGenerationResult:
        """
        Convert natural language question to SQL.

        Args:
            question: Natural language question
            context: Optional context (company, date range, etc.)

        Returns:
            SQLGenerationResult with SQL and metadata
        """
        question_lower = question.lower()

        # Step 1: Check for exact pattern match
        for pattern, sql in self.QUERY_PATTERNS.items():
            if pattern in question_lower:
                return SQLGenerationResult(
                    sql=sql,
                    intent=self._detect_intent(question_lower),
                    tables_used=self._extract_tables(sql),
                    columns_used=self._extract_columns(sql),
                    filters={},
                    confidence=0.95,
                    explanation=f"Matched pattern: {pattern}",
                    is_safe=True,
                    warnings=[]
                )

        # Step 2: Parse question for entities
        entities = self._extract_entities(question)
        intent = self._detect_intent(question_lower)

        # Step 3: Generate SQL
        sql = self._build_sql(question_lower, entities, intent, context)

        # Step 4: Validate safety
        is_safe, warnings = self._validate_sql(sql)

        return SQLGenerationResult(
            sql=sql if is_safe else "",
            intent=intent,
            tables_used=self._extract_tables(sql),
            columns_used=self._extract_columns(sql),
            filters=entities.get("filters", {}),
            confidence=0.75 if is_safe else 0.0,
            explanation=self._generate_explanation(question, sql, entities),
            is_safe=is_safe,
            warnings=warnings
        )

    async def explain_query(self, question: str) -> Dict[str, Any]:
        """Explain what the query would do without executing."""
        result = await self.generate_sql(question)

        return {
            "question": question,
            "interpreted_as": result.explanation,
            "would_query": result.tables_used,
            "would_return": result.columns_used,
            "intent": result.intent.value,
            "confidence": result.confidence
        }

    def _detect_intent(self, question: str) -> QueryIntent:
        """Detect query intent."""
        if any(w in question for w in ["total", "count", "sum", "average", "how many"]):
            return QueryIntent.AGGREGATE
        if any(w in question for w in ["compare", "vs", "versus", "difference"]):
            return QueryIntent.COMPARE
        if any(w in question for w in ["trend", "over time", "monthly", "yearly"]):
            return QueryIntent.TREND
        if any(w in question for w in ["where", "filter", "only", "specific"]):
            return QueryIntent.FILTER
        return QueryIntent.SELECT

    def _extract_entities(self, question: str) -> Dict[str, Any]:
        """Extract entities from question."""
        entities = {
            "tables": [],
            "columns": [],
            "filters": {},
            "aggregations": [],
            "time_range": None
        }

        question_lower = question.lower()

        # Detect tables
        for table_name in self.SCHEMA.keys():
            if table_name.rstrip('s') in question_lower or table_name in question_lower:
                entities["tables"].append(table_name)

        # Detect aggregations
        if "total" in question_lower or "sum" in question_lower:
            entities["aggregations"].append("SUM")
        if "count" in question_lower or "how many" in question_lower:
            entities["aggregations"].append("COUNT")
        if "average" in question_lower:
            entities["aggregations"].append("AVG")

        # Detect time filters
        if "this month" in question_lower:
            entities["time_range"] = "MONTH(CURRENT_DATE)"
        if "this year" in question_lower:
            entities["time_range"] = "YEAR(CURRENT_DATE)"
        if "last month" in question_lower:
            entities["time_range"] = "MONTH(CURRENT_DATE) - 1"

        # Detect status filters
        if "pending" in question_lower:
            entities["filters"]["status"] = "pending"
        if "active" in question_lower:
            entities["filters"]["status"] = "active"
        if "approved" in question_lower:
            entities["filters"]["status"] = "approved"

        return entities

    def _build_sql(
        self,
        question: str,
        entities: Dict[str, Any],
        intent: QueryIntent,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build SQL query from entities."""
        tables = entities.get("tables", [])
        if not tables:
            tables = ["employees"]  # Default

        primary_table = tables[0]

        # Build SELECT clause
        if QueryIntent.AGGREGATE == intent:
            if "COUNT" in entities.get("aggregations", []):
                select = "COUNT(*) as count"
            elif "SUM" in entities.get("aggregations", []):
                if "salary" in question:
                    select = "SUM(salary) as total_salary"
                else:
                    select = "SUM(total) as total"
            elif "AVG" in entities.get("aggregations", []):
                select = "AVG(salary) as avg_salary"
            else:
                select = "*"
        else:
            select = "*"

        # Build base query
        sql = f"SELECT {select} FROM {primary_table}"

        # Add WHERE clause
        filters = entities.get("filters", {})
        if filters:
            conditions = [f"{k} = '{v}'" for k, v in filters.items()]
            sql += f" WHERE {' AND '.join(conditions)}"

        # Add time filter
        if entities.get("time_range"):
            where_clause = " WHERE " if "WHERE" not in sql else " AND "
            sql += f"{where_clause}created_at >= DATE_TRUNC('month', CURRENT_DATE)"

        # Add LIMIT for safety
        if "LIMIT" not in sql.upper():
            sql += " LIMIT 100"

        return sql

    def _validate_sql(self, sql: str) -> tuple:
        """Validate SQL for safety."""
        warnings = []
        sql_lower = sql.lower()

        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in sql_lower:
                return False, [f"Dangerous pattern detected: {pattern}"]

        if ";" in sql and sql.count(";") > 1:
            return False, ["Multiple statements not allowed"]

        if "*" in sql and "COUNT(*)" not in sql.upper():
            warnings.append("SELECT * may return large result set")

        if "LIMIT" not in sql.upper():
            warnings.append("No LIMIT clause - may return many rows")

        return True, warnings

    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL."""
        tables = []
        sql_upper = sql.upper()
        for table in self.SCHEMA.keys():
            if table.upper() in sql_upper:
                tables.append(table)
        return tables

    def _extract_columns(self, sql: str) -> List[str]:
        """Extract column names from SQL."""
        # Simplified extraction
        if "SELECT *" in sql.upper():
            return ["*"]

        columns = []
        for table, info in self.SCHEMA.items():
            for col in info["columns"]:
                if col in sql.lower():
                    columns.append(col)
        return list(set(columns))

    def _generate_explanation(
        self,
        question: str,
        sql: str,
        entities: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation."""
        tables = entities.get("tables", ["employees"])
        aggregations = entities.get("aggregations", [])
        filters = entities.get("filters", {})

        parts = []
        if aggregations:
            parts.append(f"Calculate {'/'.join(aggregations).lower()}")
        else:
            parts.append("Retrieve records")

        parts.append(f"from {', '.join(tables)}")

        if filters:
            parts.append(f"where {', '.join([f'{k}={v}' for k,v in filters.items()])}")

        return " ".join(parts)

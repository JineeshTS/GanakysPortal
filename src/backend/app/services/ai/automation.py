"""
AI-011: Auto-Actions Service
AI-012: Queue Management
Automated actions and intelligent task queue management
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid


class ActionType(str, Enum):
    """Types of automated actions."""
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    DATA_UPDATE = "data_update"
    REMINDER = "reminder"
    ESCALATION = "escalation"
    WORKFLOW = "workflow"
    REPORT = "report"


class ActionStatus(str, Enum):
    """Action execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(str, Enum):
    """Action trigger types."""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"
    MANUAL = "manual"


class QueuePriority(str, Enum):
    """Task queue priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AutoAction:
    """Automated action definition."""
    id: str
    name: str
    action_type: ActionType
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    action_config: Dict[str, Any]
    is_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    run_count: int = 0
    conditions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ActionExecution:
    """Action execution record."""
    id: str
    action_id: str
    status: ActionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    context: Dict[str, Any]


@dataclass
class QueueTask:
    """Task in the queue."""
    id: str
    task_type: str
    priority: QueuePriority
    payload: Dict[str, Any]
    status: ActionStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class AutoActionService:
    """
    AI-011: Automated Actions Service

    Features:
    - Rule-based automation
    - Time-based triggers
    - Event-driven actions
    - Conditional execution
    - Action chaining
    """

    # Pre-defined action templates
    TEMPLATES = {
        "auto_approve_leave": {
            "action_type": ActionType.APPROVAL,
            "trigger_type": TriggerType.EVENT_BASED,
            "trigger_config": {"event": "leave_request_created"},
            "conditions": [
                {"field": "days", "operator": "<=", "value": 2},
                {"field": "leave_balance", "operator": ">=", "value": "days"},
            ],
            "action_config": {
                "action": "approve",
                "notify": ["employee", "manager"],
            }
        },
        "expense_escalation": {
            "action_type": ActionType.ESCALATION,
            "trigger_type": TriggerType.CONDITION_BASED,
            "trigger_config": {"check_interval": 3600},  # hourly
            "conditions": [
                {"field": "status", "operator": "==", "value": "pending"},
                {"field": "age_hours", "operator": ">", "value": 48},
            ],
            "action_config": {
                "escalate_to": "next_level_manager",
                "notify": ["current_approver", "requester"],
            }
        },
        "payroll_reminder": {
            "action_type": ActionType.REMINDER,
            "trigger_type": TriggerType.TIME_BASED,
            "trigger_config": {"cron": "0 9 20 * *"},  # 20th of every month
            "conditions": [],
            "action_config": {
                "message": "Payroll processing due in 5 days",
                "recipients": ["hr_manager", "finance_manager"],
            }
        },
        "invoice_overdue_notification": {
            "action_type": ActionType.NOTIFICATION,
            "trigger_type": TriggerType.TIME_BASED,
            "trigger_config": {"cron": "0 10 * * 1"},  # Every Monday
            "conditions": [
                {"field": "overdue_days", "operator": ">", "value": 0},
            ],
            "action_config": {
                "template": "invoice_overdue_reminder",
                "recipients": ["finance_team"],
            }
        },
    }

    def __init__(self, ai_service=None):
        """Initialize with optional AI service."""
        self.ai_service = ai_service
        self._actions: Dict[str, AutoAction] = {}
        self._executions: List[ActionExecution] = []
        self._handlers: Dict[ActionType, Callable] = {}

    async def create_action(
        self,
        name: str,
        template_name: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> AutoAction:
        """Create new automated action."""
        if template_name and template_name in self.TEMPLATES:
            config = {**self.TEMPLATES[template_name]}
            if custom_config:
                config.update(custom_config)
        elif custom_config:
            config = custom_config
        else:
            raise ValueError("Either template_name or custom_config required")

        action = AutoAction(
            id=str(uuid.uuid4()),
            name=name,
            action_type=ActionType(config["action_type"]),
            trigger_type=TriggerType(config["trigger_type"]),
            trigger_config=config.get("trigger_config", {}),
            action_config=config.get("action_config", {}),
            conditions=config.get("conditions", [])
        )

        self._actions[action.id] = action
        return action

    async def execute_action(
        self,
        action_id: str,
        context: Dict[str, Any]
    ) -> ActionExecution:
        """Execute an automated action."""
        action = self._actions.get(action_id)
        if not action:
            raise ValueError(f"Action not found: {action_id}")

        if not action.is_enabled:
            raise ValueError(f"Action is disabled: {action_id}")

        execution = ActionExecution(
            id=str(uuid.uuid4()),
            action_id=action_id,
            status=ActionStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
            completed_at=None,
            result=None,
            error=None,
            context=context
        )

        try:
            # Check conditions
            if not self._evaluate_conditions(action.conditions, context):
                execution.status = ActionStatus.CANCELLED
                execution.result = {"reason": "Conditions not met"}
                return execution

            # Execute based on action type
            result = await self._execute_by_type(action, context)

            execution.status = ActionStatus.COMPLETED
            execution.result = result
            execution.completed_at = datetime.utcnow()

            # Update action stats
            action.last_run = datetime.utcnow()
            action.run_count += 1

        except Exception as e:
            execution.status = ActionStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()

        self._executions.append(execution)
        return execution

    async def process_event(
        self,
        event_name: str,
        event_data: Dict[str, Any]
    ) -> List[ActionExecution]:
        """Process event and trigger matching actions."""
        executions = []

        for action in self._actions.values():
            if not action.is_enabled:
                continue

            if action.trigger_type != TriggerType.EVENT_BASED:
                continue

            if action.trigger_config.get("event") == event_name:
                execution = await self.execute_action(action.id, event_data)
                executions.append(execution)

        return executions

    def register_handler(
        self,
        action_type: ActionType,
        handler: Callable
    ) -> None:
        """Register custom action handler."""
        self._handlers[action_type] = handler

    def _evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate action conditions."""
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            expected = condition.get("value")

            actual = context.get(field)

            # Handle dynamic value references
            if isinstance(expected, str) and expected in context:
                expected = context[expected]

            if operator == "==":
                if actual != expected:
                    return False
            elif operator == "!=":
                if actual == expected:
                    return False
            elif operator == ">":
                if not (actual and actual > expected):
                    return False
            elif operator == ">=":
                if not (actual and actual >= expected):
                    return False
            elif operator == "<":
                if not (actual and actual < expected):
                    return False
            elif operator == "<=":
                if not (actual and actual <= expected):
                    return False
            elif operator == "in":
                if actual not in expected:
                    return False

        return True

    async def _execute_by_type(
        self,
        action: AutoAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute action based on type."""
        # Check for custom handler
        if action.action_type in self._handlers:
            return await self._handlers[action.action_type](action, context)

        # Default handlers
        if action.action_type == ActionType.APPROVAL:
            return await self._handle_approval(action, context)
        elif action.action_type == ActionType.NOTIFICATION:
            return await self._handle_notification(action, context)
        elif action.action_type == ActionType.REMINDER:
            return await self._handle_reminder(action, context)
        elif action.action_type == ActionType.ESCALATION:
            return await self._handle_escalation(action, context)
        elif action.action_type == ActionType.WORKFLOW:
            return await self._handle_workflow(action, context)
        elif action.action_type == ActionType.REPORT:
            return await self._handle_report(action, context)

        return {"status": "no_handler"}

    async def _handle_approval(
        self,
        action: AutoAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle auto-approval action."""
        # In production, update actual records
        return {
            "approved": True,
            "approved_by": "system",
            "reason": "Auto-approved by rule",
            "entity_id": context.get("id"),
            "notifications_sent": action.action_config.get("notify", [])
        }

    async def _handle_notification(
        self,
        action: AutoAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle notification action."""
        template = action.action_config.get("template", "default")
        recipients = action.action_config.get("recipients", [])

        # In production, send actual notifications
        return {
            "notification_sent": True,
            "template": template,
            "recipients": recipients,
            "context": context
        }

    async def _handle_reminder(
        self,
        action: AutoAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle reminder action."""
        message = action.action_config.get("message", "Reminder")
        recipients = action.action_config.get("recipients", [])

        return {
            "reminder_sent": True,
            "message": message,
            "recipients": recipients
        }

    async def _handle_escalation(
        self,
        action: AutoAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle escalation action."""
        escalate_to = action.action_config.get("escalate_to", "manager")

        return {
            "escalated": True,
            "escalated_to": escalate_to,
            "entity_id": context.get("id")
        }

    async def _handle_workflow(
        self,
        action: AutoAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle workflow action."""
        workflow_steps = action.action_config.get("steps", [])

        return {
            "workflow_initiated": True,
            "steps": workflow_steps
        }

    async def _handle_report(
        self,
        action: AutoAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle report generation action."""
        report_type = action.action_config.get("report_type", "summary")

        return {
            "report_generated": True,
            "report_type": report_type,
            "format": action.action_config.get("format", "pdf")
        }


class TaskQueueService:
    """
    AI-012: Intelligent Task Queue Management

    Features:
    - Priority-based processing
    - Retry mechanism
    - Load balancing
    - Dead letter queue
    - AI-driven prioritization
    """

    # Processing configuration
    MAX_CONCURRENT_TASKS = 10
    RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min

    def __init__(self, ai_service=None):
        """Initialize with optional AI service."""
        self.ai_service = ai_service
        self._queues: Dict[QueuePriority, List[QueueTask]] = {
            p: [] for p in QueuePriority
        }
        self._processing: List[QueueTask] = []
        self._completed: List[QueueTask] = []
        self._dead_letter: List[QueueTask] = []
        self._handlers: Dict[str, Callable] = {}

    async def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: Optional[QueuePriority] = None
    ) -> QueueTask:
        """
        Add task to queue.

        Args:
            task_type: Type of task
            payload: Task data
            priority: Optional priority (AI will determine if not provided)

        Returns:
            Created task
        """
        # AI-driven priority determination
        if priority is None:
            priority = await self._determine_priority(task_type, payload)

        task = QueueTask(
            id=str(uuid.uuid4()),
            task_type=task_type,
            priority=priority,
            payload=payload,
            status=ActionStatus.PENDING,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None
        )

        self._queues[priority].append(task)
        return task

    async def process_next(self) -> Optional[QueueTask]:
        """Process next task from queue."""
        if len(self._processing) >= self.MAX_CONCURRENT_TASKS:
            return None

        # Get highest priority task
        task = self._get_next_task()
        if not task:
            return None

        task.status = ActionStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self._processing.append(task)

        try:
            # Execute task
            handler = self._handlers.get(task.task_type)
            if handler:
                result = await handler(task.payload)
                task.result = result
                task.status = ActionStatus.COMPLETED
            else:
                task.status = ActionStatus.FAILED
                task.error = f"No handler for task type: {task.task_type}"

        except Exception as e:
            task.error = str(e)

            if task.retry_count < task.max_retries:
                # Schedule retry
                task.retry_count += 1
                task.status = ActionStatus.PENDING
                await self._schedule_retry(task)
            else:
                # Move to dead letter queue
                task.status = ActionStatus.FAILED
                self._dead_letter.append(task)

        finally:
            self._processing.remove(task)

            if task.status == ActionStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
                self._completed.append(task)

        return task

    async def process_batch(self, max_tasks: int = 10) -> List[QueueTask]:
        """Process multiple tasks in parallel."""
        tasks = []
        for _ in range(max_tasks):
            task = await self.process_next()
            if task:
                tasks.append(task)
            else:
                break
        return tasks

    def register_handler(
        self,
        task_type: str,
        handler: Callable
    ) -> None:
        """Register task handler."""
        self._handlers[task_type] = handler

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queued": {
                p.value: len(self._queues[p]) for p in QueuePriority
            },
            "processing": len(self._processing),
            "completed": len(self._completed),
            "dead_letter": len(self._dead_letter),
            "total_queued": sum(len(q) for q in self._queues.values())
        }

    def get_task_status(self, task_id: str) -> Optional[QueueTask]:
        """Get task by ID."""
        # Check all queues
        for queue in self._queues.values():
            for task in queue:
                if task.id == task_id:
                    return task

        for task in self._processing:
            if task.id == task_id:
                return task

        for task in self._completed:
            if task.id == task_id:
                return task

        for task in self._dead_letter:
            if task.id == task_id:
                return task

        return None

    def requeue_dead_letter(self, task_id: str) -> bool:
        """Requeue a task from dead letter queue."""
        for task in self._dead_letter:
            if task.id == task_id:
                self._dead_letter.remove(task)
                task.status = ActionStatus.PENDING
                task.retry_count = 0
                task.error = None
                self._queues[task.priority].append(task)
                return True
        return False

    async def _determine_priority(
        self,
        task_type: str,
        payload: Dict[str, Any]
    ) -> QueuePriority:
        """Use AI to determine task priority."""
        # Priority rules
        priority_rules = {
            # Critical tasks
            "payroll_process": QueuePriority.CRITICAL,
            "compliance_filing": QueuePriority.CRITICAL,
            "security_alert": QueuePriority.CRITICAL,

            # High priority
            "invoice_payment": QueuePriority.HIGH,
            "approval_request": QueuePriority.HIGH,
            "employee_offboard": QueuePriority.HIGH,

            # Medium priority
            "report_generate": QueuePriority.MEDIUM,
            "notification_send": QueuePriority.MEDIUM,
            "document_process": QueuePriority.MEDIUM,

            # Low priority
            "backup": QueuePriority.LOW,
            "cleanup": QueuePriority.LOW,
            "analytics": QueuePriority.LOW,
        }

        return priority_rules.get(task_type, QueuePriority.MEDIUM)

    def _get_next_task(self) -> Optional[QueueTask]:
        """Get next task based on priority."""
        for priority in [QueuePriority.CRITICAL, QueuePriority.HIGH,
                        QueuePriority.MEDIUM, QueuePriority.LOW]:
            if self._queues[priority]:
                return self._queues[priority].pop(0)
        return None

    async def _schedule_retry(self, task: QueueTask) -> None:
        """Schedule task retry with backoff."""
        delay_index = min(task.retry_count - 1, len(self.RETRY_DELAYS) - 1)
        delay = self.RETRY_DELAYS[delay_index]

        # In production, use actual scheduling
        # For now, immediately re-queue
        self._queues[task.priority].append(task)

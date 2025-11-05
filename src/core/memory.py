"""Memory manager for execution history and meta-learning."""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.core.schemas import ExecutionRecord
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class MemoryManager:
    """Manage execution history and meta-learning."""

    def __init__(self, db_path: str = "execution_history.db"):
        """
        Initialize memory manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id TEXT PRIMARY KEY,
                workflow_name TEXT,
                blueprint TEXT,
                success BOOLEAN,
                error_type TEXT,
                error_message TEXT,
                retry_count INTEGER,
                duration_seconds REAL,
                timestamp DATETIME,
                learned_adjustments TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT,
                failure_reason TEXT,
                frequency INTEGER DEFAULT 1,
                last_seen DATETIME,
                recommended_fix TEXT
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Memory database initialized at {self.db_path}")

    def record_execution(self, record: ExecutionRecord):
        """
        Record an execution.

        Args:
            record: ExecutionRecord to save
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO execution_history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.id,
            record.workflow_name,
            record.blueprint,
            record.success,
            record.error_type,
            record.error_message,
            record.retry_count,
            record.duration_seconds,
            record.timestamp.isoformat(),
            record.learned_adjustments
        ))

        conn.commit()
        conn.close()

        if not record.success:
            self._update_failure_patterns(record)
            logger.warning(f"Execution failed: {record.workflow_name} - {record.error_message}")
        else:
            logger.info(f"Execution recorded: {record.workflow_name} (success)")

    def get_learning_context(self, workflow_name: str) -> str:
        """
        Get meta-learning context from past failures.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Learning context string
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query recent failures
        cursor.execute("""
            SELECT failure_reason, frequency, recommended_fix
            FROM failure_patterns
            WHERE workflow_name = ?
            ORDER BY frequency DESC
            LIMIT 5
        """, (workflow_name,))

        patterns = cursor.fetchall()
        conn.close()

        if not patterns:
            return "No historical failures for this workflow type."

        context = "Historical learning from past failures:\n"
        for reason, freq, fix in patterns:
            context += f"- Issue: {reason} (occurred {freq} times)\n"
            context += f"  Fix: {fix}\n"

        return context

    def get_execution_stats(self, workflow_name: str) -> Dict[str, Any]:
        """
        Get execution statistics for a workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_executions,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                AVG(duration_seconds) as avg_duration,
                AVG(retry_count) as avg_retries
            FROM execution_history
            WHERE workflow_name = ?
        """, (workflow_name,))

        result = cursor.fetchone()
        conn.close()

        if not result or result[0] == 0:
            return {
                "total_executions": 0,
                "successful": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "avg_retries": 0.0
            }

        total, successful, avg_duration, avg_retries = result
        return {
            "total_executions": total,
            "successful": successful,
            "success_rate": (successful / total) * 100 if total > 0 else 0.0,
            "avg_duration": avg_duration or 0.0,
            "avg_retries": avg_retries or 0.0
        }

    def _update_failure_patterns(self, record: ExecutionRecord):
        """
        Update failure patterns for meta-learning.

        Args:
            record: Failed execution record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if pattern exists
        cursor.execute("""
            SELECT id, frequency FROM failure_patterns
            WHERE workflow_name = ? AND failure_reason = ?
        """, (record.workflow_name, record.error_message))

        existing = cursor.fetchone()

        if existing:
            # Update frequency
            cursor.execute("""
                UPDATE failure_patterns
                SET frequency = ?, last_seen = ?
                WHERE id = ?
            """, (existing[1] + 1, datetime.now().isoformat(), existing[0]))
        else:
            # Insert new pattern
            cursor.execute("""
                INSERT INTO failure_patterns (workflow_name, failure_reason, last_seen, recommended_fix)
                VALUES (?, ?, ?, ?)
            """, (
                record.workflow_name,
                record.error_message,
                datetime.now().isoformat(),
                "Increase prompt strictness and add explicit validation"
            ))

        conn.commit()
        conn.close()

    def clear_history(self, workflow_name: Optional[str] = None):
        """
        Clear execution history.

        Args:
            workflow_name: If provided, clear only this workflow's history
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if workflow_name:
            cursor.execute("DELETE FROM execution_history WHERE workflow_name = ?", (workflow_name,))
            cursor.execute("DELETE FROM failure_patterns WHERE workflow_name = ?", (workflow_name,))
            logger.info(f"Cleared history for workflow: {workflow_name}")
        else:
            cursor.execute("DELETE FROM execution_history")
            cursor.execute("DELETE FROM failure_patterns")
            logger.info("Cleared all execution history")

        conn.commit()
        conn.close()

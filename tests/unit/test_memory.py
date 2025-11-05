"""Unit tests for memory manager."""
import pytest
from datetime import datetime
from src.core.memory import MemoryManager
from src.core.schemas import ExecutionRecord


def test_memory_initialization(temp_db):
    """Test memory manager initialization."""
    memory = MemoryManager(temp_db)

    # Check that tables were created
    import sqlite3
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    conn.close()

    assert "execution_history" in tables
    assert "failure_patterns" in tables


def test_record_successful_execution(temp_db):
    """Test recording successful execution."""
    memory = MemoryManager(temp_db)

    record = ExecutionRecord(
        id="test-123",
        workflow_name="test_workflow",
        blueprint="test blueprint",
        success=True,
        retry_count=0,
        duration_seconds=10.5,
        timestamp=datetime.now()
    )

    memory.record_execution(record)

    # Verify recorded
    stats = memory.get_execution_stats("test_workflow")
    assert stats["total_executions"] == 1
    assert stats["successful"] == 1


def test_record_failed_execution(temp_db):
    """Test recording failed execution."""
    memory = MemoryManager(temp_db)

    record = ExecutionRecord(
        id="test-456",
        workflow_name="test_workflow",
        blueprint="test blueprint",
        success=False,
        error_type="ValidationError",
        error_message="Output too short",
        retry_count=2,
        duration_seconds=8.3,
        timestamp=datetime.now()
    )

    memory.record_execution(record)

    # Verify recorded
    stats = memory.get_execution_stats("test_workflow")
    assert stats["total_executions"] == 1
    assert stats["successful"] == 0
    assert stats["success_rate"] == 0.0


def test_get_learning_context_no_history(temp_db):
    """Test getting learning context with no history."""
    memory = MemoryManager(temp_db)

    context = memory.get_learning_context("new_workflow")

    assert "No historical failures" in context


def test_get_learning_context_with_failures(temp_db):
    """Test getting learning context with failure history."""
    memory = MemoryManager(temp_db)

    # Record a failure
    record = ExecutionRecord(
        id="test-789",
        workflow_name="test_workflow",
        blueprint="test",
        success=False,
        error_type="ValidationError",
        error_message="Missing required sections",
        retry_count=1,
        duration_seconds=5.0,
        timestamp=datetime.now()
    )

    memory.record_execution(record)

    # Get learning context
    context = memory.get_learning_context("test_workflow")

    assert "Historical learning" in context
    assert "Missing required sections" in context


def test_get_execution_stats_multiple_executions(temp_db):
    """Test execution statistics with multiple runs."""
    memory = MemoryManager(temp_db)

    # Record multiple executions
    for i in range(5):
        record = ExecutionRecord(
            id=f"test-{i}",
            workflow_name="test_workflow",
            blueprint="test",
            success=i < 3,  # First 3 succeed
            retry_count=i % 2,
            duration_seconds=10.0 + i,
            timestamp=datetime.now()
        )
        memory.record_execution(record)

    # Check stats
    stats = memory.get_execution_stats("test_workflow")

    assert stats["total_executions"] == 5
    assert stats["successful"] == 3
    assert stats["success_rate"] == 60.0
    assert stats["avg_duration"] > 10.0


def test_clear_history_specific_workflow(temp_db):
    """Test clearing history for specific workflow."""
    memory = MemoryManager(temp_db)

    # Record for two workflows
    for workflow in ["workflow_a", "workflow_b"]:
        record = ExecutionRecord(
            id=f"test-{workflow}",
            workflow_name=workflow,
            blueprint="test",
            success=True,
            retry_count=0,
            duration_seconds=10.0,
            timestamp=datetime.now()
        )
        memory.record_execution(record)

    # Clear only workflow_a
    memory.clear_history("workflow_a")

    # Check that workflow_a is cleared but workflow_b remains
    stats_a = memory.get_execution_stats("workflow_a")
    stats_b = memory.get_execution_stats("workflow_b")

    assert stats_a["total_executions"] == 0
    assert stats_b["total_executions"] == 1


def test_clear_all_history(temp_db):
    """Test clearing all history."""
    memory = MemoryManager(temp_db)

    # Record some executions
    for i in range(3):
        record = ExecutionRecord(
            id=f"test-{i}",
            workflow_name="test_workflow",
            blueprint="test",
            success=True,
            retry_count=0,
            duration_seconds=10.0,
            timestamp=datetime.now()
        )
        memory.record_execution(record)

    # Clear all
    memory.clear_history()

    # Check that all cleared
    stats = memory.get_execution_stats("test_workflow")
    assert stats["total_executions"] == 0

"""API dependencies and utilities."""
from src.core.blueprint_parser import BlueprintParser
from src.core.memory import MemoryManager


def get_blueprint_parser() -> BlueprintParser:
    """
    Get blueprint parser instance.

    Returns:
        BlueprintParser instance
    """
    return BlueprintParser()


def get_memory_manager() -> MemoryManager:
    """
    Get memory manager instance.

    Returns:
        MemoryManager instance
    """
    return MemoryManager()

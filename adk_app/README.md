# Google ADK Integration

## Current Status

**Default Mode**: Mock mode (ADK not required for demo)

This demo showcases how the same workflow can be implemented using Google ADK as an alternative to LangGraph. The system automatically detects ADK availability and gracefully falls back to mock mode.

## Architecture Mapping

| LangGraph Component | ADK Equivalent | Notes |
|---------------------|----------------|-------|
| StateGraph | ADK Workflow | Orchestration pattern |
| Agent Nodes | ADK Agents | Specialized AI agents |
| Tools | Python Functions | Functions agents can call |
| State | Context Dict | Shared state between agents |
| Checkpointer | ADK Memory | Execution persistence |

## Enabling Real ADK

### 1. Install Google ADK

```bash
pip install google-adk
```

### 2. Configure API Key (if needed)

```bash
export GOOGLE_API_KEY=your-api-key-here
```

Or add to `.env`:
```
GOOGLE_API_KEY=your-api-key-here
```

### 3. Restart Application

The system will automatically detect ADK and use it instead of mock mode:

```bash
# Streamlit will show: ✅ Google ADK Enabled
make dev
```

## How It Works

### Mock Mode (Default)

When `google-adk` is not installed:

```python
from adk_app.manager_tool import ADK_AVAILABLE, ADKManagerTool

if not ADK_AVAILABLE:
    # Automatically uses mock implementation
    # All functionality works, but without real ADK
    pass
```

### Real ADK Mode

When `google-adk` is installed:

```python
from google.adk.agents.llm_agent import Agent

# Create ADK agent with tools
manager = Agent(
    model="gemini-2.0-flash-exp",
    name="manager",
    description="Coordinates research and writing agents",
    instruction="Coordinate agents; call research tool when needed.",
    tools=[research_function, write_function],
)

# Execute
result = manager.invoke({"task": "research company X"})
```

## ADK Implementation Example

See [`manager_tool.py`](manager_tool.py) for the complete implementation:

```python
# Tool definition (Python function)
def _mock_research(company: str = "ACME") -> dict:
    """Research tool callable by ADK agents."""
    return {
        "status": "success",
        "company": company,
        "findings": "..."
    }

# Agent creation
manager = Agent(
    model="gemini-2.0-flash-exp",
    name="manager",
    tools=[_mock_research],  # Functions become tools
)

# Execution
result = manager.invoke(input_data)
```

## Comparison: LangGraph vs ADK

### LangGraph Approach (Current)
- ✅ More control over graph structure
- ✅ Explicit state management
- ✅ Rich ecosystem (LangChain integration)
- ✅ Better for complex branching logic

### ADK Approach (Alternative)
- ✅ Native Google integration
- ✅ Optimized for Gemini models
- ✅ Simpler for linear workflows
- ✅ Google Cloud native deployment

## Testing

Both modes are fully tested:

```bash
# Test with mock mode (default)
pytest tests/unit/test_adk.py

# Test with real ADK (if installed)
ADK_AVAILABLE=1 pytest tests/unit/test_adk.py
```

## References

- [Google ADK Repository](https://github.com/google/adk)
- [ADK Python Quickstart](https://github.com/google/adk/tree/main/python)
- [ADK Documentation](https://github.com/google/adk/blob/main/docs/README.md)

## Troubleshooting

### ADK Not Detected

**Symptom**: Streamlit shows "⚠️ Mock Mode" even after installing

**Solution**:
```bash
# Verify installation
pip list | grep google-adk

# Restart application
# Streamlit must be restarted to detect new packages
```

### Import Errors

**Symptom**: `ImportError: cannot import name 'Agent'`

**Solution**:
```bash
# Ensure correct version
pip install --upgrade google-adk

# Check import
python -c "from google.adk.agents.llm_agent import Agent; print('OK')"
```

### API Key Issues

**Symptom**: ADK available but execution fails

**Solution**:
```bash
# Set API key
export GOOGLE_API_KEY=your-key

# Verify
echo $GOOGLE_API_KEY
```

## Design Philosophy

This integration demonstrates **graceful degradation**:

1. **Primary Mode**: Full ADK integration when available
2. **Fallback Mode**: Mock implementation maintains functionality
3. **Seamless Switch**: No code changes needed to toggle modes
4. **Demo Ready**: Works out-of-the-box without API keys

This approach ensures the demo is always runnable while showcasing production-ready ADK integration patterns.

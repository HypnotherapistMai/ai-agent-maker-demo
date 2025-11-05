# System Architecture

## Overview

The AI Agent Maker is a blueprint-to-agent system that dynamically generates and executes multi-agent workflows based on user-provided specifications.

## Core Design Principles

1. **Separation of Concerns**: Blueprint parsing → Agent generation → Execution → Validation
2. **Dynamic Generation**: Workflows defined at runtime, not hardcoded
3. **Meta-Learning**: System improves based on execution history
4. **Graceful Degradation**: Falls back to mocks when external services unavailable
5. **Extensibility**: Easy to add new agent types and scenarios

## Component Architecture

### 1. Blueprint Parser (`src/core/blueprint_parser.py`)

**Purpose**: Converts user input (JSON or natural language) into standardized `Workflow` objects.

**Key Features**:
- Dual input support (structured JSON or NL)
- Pydantic validation
- Default step generation per scenario
- LLM-powered NL parsing

**Flow**:
```
User Input → Try JSON parse → Success? → Validate with Pydantic
              ↓ Fail
          NL Parser (LLM) → Extract intent → Generate JSON → Validate
```

### 2. Agent System (`src/agents/`)

**Base Agent** (`base.py`):
- Abstract class defining agent interface
- LLM client wrapper
- Common response generation logic

**Specialized Agents**:

#### Manager Agent (`manager.py`)
- **Role**: Orchestration and strategic decision-making
- **Responsibilities**:
  - Coordinate agent execution order
  - Apply meta-learning insights
  - Adjust prompts based on historical failures
  - Make go/no-go decisions
- **Inputs**: Workflow definition, execution history
- **Outputs**: Next agent decision, adjusted prompts, strategic notes

#### Researcher Agent (`researcher.py`)
- **Role**: Data gathering and analysis
- **Responsibilities**:
  - Research companies, markets, candidates
  - Gather relevant data (mocked for demo)
  - Provide structured findings
- **Inputs**: Company name, JD, or other research targets
- **Outputs**: Structured research findings

#### Writer Agent (`writer.py`)
- **Role**: Content generation
- **Responsibilities**:
  - Transform research into polished output
  - Follow formatting requirements
  - Incorporate validation feedback
  - Retry with improvements
- **Inputs**: Research findings, validation feedback (if retry)
- **Outputs**: Draft report or strategy document

#### QA Agent (`qa.py`)
- **Role**: Quality assurance
- **Responsibilities**:
  - Validate output completeness
  - Check formatting and structure
  - Provide actionable feedback
  - Make pass/fail decisions
- **Inputs**: Writer output, validation rules
- **Outputs**: Pass/fail decision, detailed feedback

### 3. LangGraph Orchestration (`src/graph/`)

**State Definition** (`state.py`):
```python
AgentState = TypedDict with:
  - workflow: Workflow definition
  - current_step: int
  - agent_outputs: Dict[str, Any]
  - messages: List[BaseMessage]
  - validation_passed: bool
  - retry_count: int
  - final_output: Optional[str]
  - status: str
```

**Graph Builder** (`builder.py`):

**Flow**:
```
START
  ↓
Manager (orchestration)
  ↓
Researcher (data gathering)
  ↓
Manager (strategic adjustment)
  ↓
Writer (content generation)
  ↓
QA (validation)
  ↓
Pass? → END
  ↓
Fail & retry < 2? → Writer (with feedback)
  ↓
Fail & retry >= 2? → END (with partial output)
```

**Key Features**:
- Conditional edges for retry logic
- Shared state across all nodes
- Checkpointing for resumability
- Automatic Mermaid diagram generation

### 4. Memory System (`src/core/memory.py`)

**Purpose**: Track execution history for meta-learning.

**Database Schema**:
```sql
execution_history:
  - id, workflow_name, blueprint
  - success, error_type, error_message
  - retry_count, duration_seconds
  - timestamp, learned_adjustments

failure_patterns:
  - workflow_name, failure_reason
  - frequency, last_seen
  - recommended_fix
```

**Meta-Learning Flow**:
1. Record every execution (success or failure)
2. Track failure patterns and frequency
3. Manager queries learning context before execution
4. Adjusts prompts based on common failures
5. System improves over time

**Example**:
- 1st run: Writer output too short → QA fails
- System records: "Output too short" pattern
- 2nd run: Manager tells Writer "ensure 300+ words"
- Success rate improves

### 5. Validation System (`src/core/validators.py`)

**Two-Level Validation**:

1. **Automated Checks**:
   - Minimum length
   - Section count
   - Required keywords
   - Format validation (markdown)

2. **LLM-Based Qualitative**:
   - Content quality
   - Completeness
   - Clarity and professionalism
   - Specific feedback for improvements

**Validation Process**:
```
Writer Output
  ↓
Automated Rules → Pass/Fail + Issues
  ↓
LLM Quality Check → Pass/Fail + Feedback
  ↓
Combined Result → Overall Pass/Fail
  ↓
Pass? → Final Output
Fail? → Feedback to Writer for retry
```

### 6. ADK Integration (`adk_app/`)

**Purpose**: Demonstrate equivalent workflow using Google ADK.

**Mapping**:
- LangGraph StateGraph ≈ ADK Workflow
- LangGraph Nodes ≈ ADK Agents
- LangGraph Tools ≈ Python Functions
- LangGraph State ≈ ADK Context

**Implementation**:
```python
# Tools are just Python functions
def research_tool(company: str) -> dict:
    return {"findings": "..."}

# Agents use tools
manager = Agent(
    model="gemini-2.0-flash-exp",
    tools=[research_tool],
    instruction="Coordinate agents"
)
```

**Graceful Degradation**:
- Detects ADK availability
- Falls back to mock mode if not installed
- All functionality works in both modes

### 7. API Layer (`api/`)

**FastAPI Application**:
- `POST /run` - Execute workflow
- `GET /health` - Health check
- `GET /stats/{workflow_name}` - Statistics
- `GET /learning/{workflow_name}` - Learning context
- `DELETE /history/{workflow_name}` - Clear history

**Request/Response Models** (Pydantic):
- Input validation
- Type safety
- Automatic OpenAPI docs

### 8. UI Layer (`ui/app.py`)

**Streamlit Application**:
- Scenario selection
- Blueprint input (JSON or NL)
- Execution triggering
- Real-time progress
- Results display
- Intermediate outputs (optional)
- Meta-learning insights
- Execution history

**Key UX Features**:
- ADK status indicator
- Load example blueprints
- Execution metrics
- Expandable details
- History tracking

## Data Flow

### End-to-End Execution:

```
1. User Input (UI or API)
     ↓
2. Blueprint Parser
   - Parse JSON or NL
   - Validate with Pydantic
   - Generate Workflow object
     ↓
3. Graph Builder
   - Create LangGraph
   - Initialize state
     ↓
4. Execution Loop:
   a. Manager → Strategic decisions
   b. Researcher → Gather data
   c. Manager → Adjust strategy
   d. Writer → Generate output
   e. QA → Validate quality
   f. Retry if needed (max 2)
     ↓
5. Memory Recording
   - Save execution record
   - Update failure patterns
     ↓
6. Response
   - Return final output
   - Include metadata
```

## Error Handling Strategy

1. **Input Level**: Pydantic validation errors → 400 Bad Request
2. **Execution Level**: Agent errors → Logged, fallback to mock
3. **Validation Level**: QA fails → Retry with feedback
4. **System Level**: Unexpected errors → Graceful degradation

## Extensibility Points

### Adding New Agent Type:
1. Create class in `src/agents/` inheriting from `BaseAgent`
2. Implement `process()` method
3. Add to graph in `builder.py`
4. Update `AgentRole` enum

### Adding New Scenario:
1. Create fixture in `fixtures/{scenario}/`
2. Add default steps in `blueprint_parser.py`
3. Add validation rules in `validators.py`
4. Create golden tests

### Adding New Tool/Integration:
1. Create adapter in `src/llm/` or similar
2. Add graceful fallback
3. Update ADK equivalence if applicable

## Performance Considerations

- **Caching**: LLM client can cache responses
- **Async**: FastAPI naturally async
- **Streaming**: Could add for long-running workflows
- **Parallelization**: Multiple independent agents could run in parallel

## Security Considerations

- API keys in environment variables
- Input validation with Pydantic
- No SQL injection (parameterized queries)
- No command injection (no user input to shell)
- Rate limiting (can be added to API)

## Future Enhancements

1. **Real External Tools**: Replace mocks with actual APIs
2. **Streaming UI**: Real-time agent output
3. **Parallel Execution**: Independent agents run concurrently
4. **Custom Agent Creation**: User-defined agent types
5. **Workflow Versioning**: Track blueprint evolution
6. **A/B Testing**: Compare workflow variations
7. **Human-in-the-Loop**: Approval steps for critical decisions

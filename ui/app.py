"""Streamlit UI for AI Agent Maker demo."""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import json
import time
from typing import Dict, Any

from src.core.blueprint_parser import BlueprintParser
from src.graph.builder import execute_workflow
from adk_app.manager_tool import ADK_AVAILABLE  # ⭐ Correct import
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

# Page config
st.set_page_config(
    page_title="AI Agent Maker Demo",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "execution_history" not in st.session_state:
    st.session_state["execution_history"] = []

# Header
st.title("🤖 AI Agent Maker - Blueprint to Execution")
st.markdown("**Transform workflow descriptions into executing multi-agent systems**")

# ⭐ ADK status display
adk_status = "✅ Google ADK Enabled" if ADK_AVAILABLE else "⚠️ Mock Mode"
st.sidebar.info(f"**ADK Status**: {adk_status}")

# Sidebar - Input
st.sidebar.header("📝 Input Blueprint")

# Scenario selection
scenario = st.sidebar.selectbox(
    "Select Scenario",
    ["due_diligence", "recruiting", "custom"],
    help="Choose a pre-configured scenario or create custom workflow"
)

# Example blueprints
EXAMPLES = {
    "due_diligence": {
        "workflow_name": "customer_due_diligence",
        "description": "Comprehensive due diligence analysis for M&A",
        "input": {
            "company_name": "TechStart Inc"
        },
        "expected_output": {
            "format": "markdown_report",
            "sections": ["financial", "legal", "market"]
        }
    },
    "recruiting": {
        "workflow_name": "jd_to_sourcing",
        "description": "Transform job description into sourcing strategy",
        "input": {
            "job_description": "Senior Software Engineer with 5+ years experience in Python, AWS, and machine learning. Must have strong communication skills."
        },
        "expected_output": {
            "format": "sourcing_package",
            "includes": ["boolean_search", "interview_outline"]
        }
    }
}

# Load example button
if scenario in EXAMPLES and st.sidebar.button("📋 Load Example"):
    st.session_state["blueprint_input"] = json.dumps(EXAMPLES[scenario], indent=2)

# Blueprint input
blueprint_input = st.sidebar.text_area(
    "Blueprint (JSON or Natural Language)",
    value=st.session_state.get("blueprint_input", ""),
    height=300,
    placeholder='{"workflow_name": "customer_due_diligence", "input": {"company_name": "ACME Corp"}}',
    help="Enter JSON blueprint or natural language description"
)

# Save to session state
st.session_state["blueprint_input"] = blueprint_input

# Execution options
st.sidebar.subheader("⚙️ Options")
show_intermediate = st.sidebar.checkbox("Show Intermediate Steps", value=True)
show_learning = st.sidebar.checkbox("Show Meta-Learning", value=True)

# Execute button
execute_button = st.sidebar.button("🚀 Execute Workflow", type="primary")

# Main content area
if execute_button and blueprint_input:
    try:
        # Parse blueprint
        with st.spinner("Parsing blueprint..."):
            parser = BlueprintParser()
            workflow = parser.parse(blueprint_input, scenario)

        st.success(f"✅ Parsed workflow: **{workflow.name}**")

        # Display workflow info
        with st.expander("📊 Workflow Details", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Name:**", workflow.name)
                st.write("**Description:**", workflow.description)
                st.write("**Steps:**", len(workflow.steps))

            with col2:
                st.write("**Input Data:**")
                st.json(workflow.input_data)

        # Execute workflow
        st.subheader("🔄 Execution Progress")

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Execute
        status_text.text("Executing workflow...")
        start_time = time.time()

        result = execute_workflow(workflow, blueprint_input)

        duration = time.time() - start_time
        progress_bar.progress(100)

        # ⭐ Store result in session_state (CRITICAL FIX)
        st.session_state["final_result"] = result
        st.session_state["workflow_name"] = workflow.name

        # Add to history
        st.session_state["execution_history"].append({
            "workflow": workflow.name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": result.get("status"),
            "duration": duration
        })

        if result["success"]:
            status_text.text(f"✅ Completed in {duration:.2f}s")
        else:
            status_text.text(f"⚠️ Completed with issues in {duration:.2f}s")

    except Exception as e:
        st.error(f"❌ Error: {e}")
        logger.error(f"UI execution error: {e}")
        st.stop()

elif execute_button and not blueprint_input:
    st.warning("⚠️ Please enter a blueprint")

# Display results
if "final_result" in st.session_state:
    result = st.session_state["final_result"]
    workflow_name = st.session_state.get("workflow_name", "Unknown")

    st.markdown("---")
    st.subheader("📊 Execution Results")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_icon = "✅" if result.get("status") == "completed" else "❌"
        st.metric("Status", f"{status_icon} {result.get('status', 'unknown')}")

    with col2:
        st.metric("Retry Count", result.get("retry_count", 0))

    with col3:
        validation_icon = "✅" if result.get("validation_passed") else "❌"
        st.metric("Validation", validation_icon)

    with col4:
        duration = result.get("duration_seconds", 0)
        st.metric("Duration", f"{duration:.2f}s")

    # Final output
    if result.get("final_output"):
        st.markdown("### 📄 Final Output")
        st.markdown(result["final_output"])
    else:
        st.warning("No final output generated")

        if result.get("validation_feedback"):
            st.error(f"**Validation Feedback**: {result['validation_feedback']}")

    # Intermediate steps
    if show_intermediate and result.get("agent_outputs"):
        with st.expander("🔍 Intermediate Agent Outputs", expanded=False):
            agent_outputs = result["agent_outputs"]

            for agent_name, output in agent_outputs.items():
                st.markdown(f"#### {agent_name.capitalize()} Agent")
                st.json(output)

    # Meta-learning insights
    if show_learning and result.get("agent_outputs", {}).get("manager"):
        manager_output = result["agent_outputs"]["manager"]

        if manager_output.get("learning_applied"):
            with st.expander("📚 Meta-Learning Insights", expanded=False):
                st.info("Manager applied historical learning to this execution")

                if "execution_stats" in manager_output:
                    stats = manager_output["execution_stats"]
                    st.write("**Historical Statistics:**")
                    st.write(f"- Total executions: {stats['total_executions']}")
                    st.write(f"- Success rate: {stats['success_rate']:.1f}%")
                    st.write(f"- Average duration: {stats['avg_duration']:.2f}s")
                    st.write(f"- Average retries: {stats['avg_retries']:.1f}")

# Execution history sidebar
if st.session_state["execution_history"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Execution History")

    for i, entry in enumerate(reversed(st.session_state["execution_history"][-5:])):
        status_icon = "✅" if entry["status"] == "completed" else "⚠️"
        st.sidebar.text(f"{status_icon} {entry['workflow']}")
        st.sidebar.caption(f"{entry['timestamp']} ({entry['duration']:.1f}s)")

    if st.sidebar.button("Clear History"):
        st.session_state["execution_history"] = []
        st.experimental_rerun()

# About section
with st.sidebar.expander("ℹ️ About"):
    st.markdown("""
    **AI Agent Maker Demo**

    A blueprint-to-agent system showcasing:
    - Dynamic multi-agent workflow generation
    - Meta-learning from execution history
    - LangGraph orchestration
    - Google ADK integration

    Built for the AI Agent Developer position.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("🤖 AI Agent Maker v1.0.0")

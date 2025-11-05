#!/usr/bin/env python3
"""Test script to verify demo scenarios show success status."""

import os
import json

# Set environment for mock mode
os.environ["MOCK"] = "1"
os.environ["PYTHONPATH"] = "."

from src.core.blueprint_parser import BlueprintParser
from src.graph.builder import execute_workflow


def test_scenario(name: str, blueprint_file: str):
    """Test a demo scenario and print results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

    # Load blueprint
    with open(blueprint_file, 'r') as f:
        blueprint = json.load(f)

    # Parse and execute
    parser = BlueprintParser()
    blueprint_str = json.dumps(blueprint)
    workflow = parser.parse(blueprint_str, name.lower().replace(' ', '_'))
    result = execute_workflow(workflow, blueprint_str)

    # Display results
    status = result.get("status", "unknown")
    validation_passed = result.get("validation_passed", False)
    retry_count = result.get("retry_count", 0)
    duration = result.get("duration_seconds", 0)

    status_icon = "✅" if status == "completed" else "❌"
    validation_icon = "✅" if validation_passed else "❌"

    print(f"\n📊 Results:")
    print(f"  Status: {status_icon} {status}")
    print(f"  Validation: {validation_icon} {'PASSED' if validation_passed else 'FAILED'}")
    print(f"  Retry Count: {retry_count}")
    print(f"  Duration: {duration:.2f}s")

    if result.get("final_output"):
        output = result["final_output"]
        print(f"\n📄 Output Preview (first 300 chars):")
        print(f"  {output[:300]}...")
        print(f"\n  Total length: {len(output)} characters")

        # Check for key elements
        has_headers = "##" in output
        print(f"  Markdown headers: {'✅' if has_headers else '❌'}")

        if "due_diligence" in name.lower():
            company_name = blueprint.get("input", {}).get("company_name", "")
            has_company = company_name.split()[0].lower() in output.lower() if company_name else False
            print(f"  Company name '{company_name}': {'✅' if has_company else '❌'}")

            sections = ["financial", "legal", "market"]
            for section in sections:
                has_section = section.lower() in output.lower()
                print(f"  Section '{section}': {'✅' if has_section else '❌'}")

        elif "recruit" in name.lower():
            has_boolean = "boolean" in output.lower()
            has_interview = "interview" in output.lower()
            has_operators = any(op in output.upper() for op in ["AND", "OR"])
            print(f"  Boolean search: {'✅' if has_boolean else '❌'}")
            print(f"  Interview outline: {'✅' if has_interview else '❌'}")
            print(f"  Boolean operators: {'✅' if has_operators else '❌'}")
    else:
        print(f"\n❌ No final output generated")
        if result.get("validation_feedback"):
            print(f"  Feedback: {result['validation_feedback']}")

    # Overall assessment
    success = status == "completed" and validation_passed and result.get("final_output")
    print(f"\n{'='*60}")
    if success:
        print(f"✅ {name}: SUCCESS - Ready for demo!")
    else:
        print(f"❌ {name}: FAILED - Needs fixes")
    print('='*60)

    return success


def main():
    """Run all demo scenario tests."""
    print("\n🤖 AI Agent Maker - Demo Scenario Test")
    print("Testing both scenarios in mock mode...\n")

    scenarios = [
        ("Due Diligence", "fixtures/consulting/due_diligence.json"),
        ("Recruiting", "fixtures/recruiting/jd_to_sourcing.json")
    ]

    results = {}
    for name, blueprint_file in scenarios:
        try:
            results[name] = test_scenario(name, blueprint_file)
        except Exception as e:
            print(f"\n❌ Error testing {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    all_passed = all(results.values())
    for name, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"{icon} {name}")

    print("="*60)
    if all_passed:
        print("✅ ALL SCENARIOS PASS - Demo is ready for recruiters!")
        print("\nNext steps:")
        print("1. Run: MOCK=1 make dev")
        print("2. Test both scenarios in UI")
        print("3. Verify green success indicators")
        print("4. Take screenshots for README")
    else:
        print("❌ Some scenarios failed - please review and fix")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

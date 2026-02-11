#!/usr/bin/env python3
"""
Script to add a Refactoring Goal with a single metric to showcase multiple goals in the frontend.
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1/domain"

# Existing evaluation program ID (from the existing goal)
EVALUATION_PROGRAM_ID = "053e9c72-f2ed-4287-b873-5b447a427d48"

# Existing LLM tool configuration IDs
LLM_CONFIGS = [
    "2464a4c7-27c1-4f2c-90b1-ecd203f41ba4",  # GitHub Copilot - Claude Sonnet 4.5
    "2986a642-fd29-4b56-bb88-0e553c0d7f7c",  # GitHub Copilot - OpenAI GPT-5
]


def create_goal():
    """Create a new goal for Refactoring."""
    goal_data = {
        "purpose": "Enhance code maintainability and reduce technical debt.",
        "focus": "Code Refactoring Quality",
        "viewpoint": "Development Team and Tech Leads",
        "context": "We need to track and measure the effectiveness of refactoring efforts to ensure code quality improvements and maintainability enhancements across the codebase.",
        "evaluation_program_id": EVALUATION_PROGRAM_ID
    }
    
    response = requests.post(f"{API_BASE_URL}/goals/", json=goal_data)
    response.raise_for_status()
    goal = response.json()
    print(f"✓ Created Goal: {goal['purpose']}")
    print(f"  ID: {goal['id']}")
    return goal


def create_evaluation_criterion(goal_id):
    """Create an evaluation criterion for the goal."""
    criterion_data = {
        "dimension": "Refactoring Impact",
        "description": "Measures the impact of refactoring efforts on code quality, focusing on complexity reduction, code duplication removal, and overall maintainability improvements.",
        "weight": 1.0,
        "aggregation_strategy": "weighted_average",
        "goal_id": goal_id
    }
    
    response = requests.post(f"{API_BASE_URL}/evaluation-criteria/", json=criterion_data)
    response.raise_for_status()
    criterion = response.json()
    print(f"✓ Created Evaluation Criterion: {criterion['dimension']}")
    print(f"  ID: {criterion['id']}")
    return criterion


def create_metric(criterion_id):
    """Create a metric for the evaluation criterion."""
    metric_data = {
        "name": "Code Complexity Reduction",
        "definition": "Measures the reduction in cyclomatic complexity after refactoring. Lower complexity indicates better code maintainability and readability.",
        "unit": "Percent",
        "scale_type": "ratio",
        "collection_method": "automated",
        "weight": 1.0,
        "target_value": 0.8,
        "direction": "higher_is_better",
        "evaluation_criterion_id": criterion_id
    }
    
    response = requests.post(f"{API_BASE_URL}/metrics/", json=metric_data)
    response.raise_for_status()
    metric = response.json()
    print(f"✓ Created Metric: {metric['name']}")
    print(f"  ID: {metric['id']}")
    return metric


def create_measurements(metric_id):
    """Create measurements for each LLM tool configuration."""
    measurements_data = [
        {
            "llm_config_id": LLM_CONFIGS[0],
            "value": 0.75,
            "evaluator": "Static Analysis Tool",
            "notes": "Complexity reduced from average of 12 to 3 after refactoring"
        },
        {
            "llm_config_id": LLM_CONFIGS[1],
            "value": 0.82,
            "evaluator": "Static Analysis Tool",
            "notes": "Complexity reduced from average of 15 to 2.7 after refactoring"
        }
    ]
    
    created_measurements = []
    for measurement_data in measurements_data:
        data = {
            "value": measurement_data["value"],
            "normalized_value": None,
            "evaluator": measurement_data["evaluator"],
            "notes": measurement_data["notes"],
            "llm_tool_configuration_id": measurement_data["llm_config_id"],
            "metric_id": metric_id,
            "date": datetime.now().isoformat()
        }
        
        response = requests.post(f"{API_BASE_URL}/measurements/", json=data)
        response.raise_for_status()
        measurement = response.json()
        created_measurements.append(measurement)
        print(f"✓ Created Measurement for LLM config {measurement_data['llm_config_id'][:8]}...")
        print(f"  Value: {measurement['value']}")
    
    return created_measurements


def main():
    """Main function to create the refactoring goal structure."""
    print("=" * 80)
    print("Creating Refactoring Goal with Metric and Measurements")
    print("=" * 80)
    print()
    
    try:
        # Create Goal
        goal = create_goal()
        print()
        
        # Create Evaluation Criterion
        criterion = create_evaluation_criterion(goal["id"])
        print()
        
        # Create Metric
        metric = create_metric(criterion["id"])
        print()
        
        # Create Measurements
        measurements = create_measurements(metric["id"])
        print()
        
        print("=" * 80)
        print("✓ Successfully created Refactoring Goal with complete structure!")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  Goal ID: {goal['id']}")
        print(f"  Criterion ID: {criterion['id']}")
        print(f"  Metric ID: {metric['id']}")
        print(f"  Measurements created: {len(measurements)}")
        print()
        print("You can now view this goal in the frontend alongside the existing testing goal.")
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

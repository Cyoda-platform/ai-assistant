#!/usr/bin/env python3
"""
Test script to validate the workflow converter_v2 migration.
Tests both old and new JSON formats.
"""

import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from common.workflow.converter_v2.workflow_converter import convert_to_dto

# Old format JSON
old_format_json = {
    "version": "1.0",
    "description": "Template FSM with structured states, transitions, actions, and conditions",
    "initial_state": "state_initial",
    "workflow_name": "template_workflow",
    "states": {
        "state_initial": {
            "transitions": {
                "transition_to_01": {
                    "next": "state_01"
                }
            }
        },
        "state_01": {
            "transitions": {
                "transition_to_02": {
                    "next": "state_02",
                    "action": {
                        "name": "example_function_name"
                    }
                }
            }
        },
        "state_02": {
            "transitions": {
                "transition_with_condition_simple": {
                    "next": "state_condition_check_01",
                    "condition": {
                        "type": "function",
                        "function": {
                            "name": "example_function_name_returns_bool"
                        }
                    }
                }
            }
        },
        "state_condition_check_01": {
            "transitions": {
                "transition_with_condition_group": {
                    "next": "state_terminal",
                    "condition": {
                        "type": "group",
                        "name": "condition_group_gamma",
                        "operator": "AND",
                        "parameters": [
                            {
                                "jsonPath": "sampleFieldA",
                                "operatorType": "equals (disregard case)",
                                "value": "template_value_01",
                                "type": "simple"
                            }
                        ]
                    }
                }
            }
        }
    }
}

# New format JSON
new_format_json = {
    "version": "1.0",
    "id": "customer_workflow",
    "name": "Customer workflow",
    "desc": "Description of the workflow",
    "initialState": "none",
    "states": {
        "none": {
            "transitions": [
                {
                    "id": "transition_to_01",
                    "next": "state_01"
                }
            ]
        },
        "state_01": {
            "transitions": [
                {
                    "id": "transition_to_02",
                    "next": "state_02",
                    "manual": True,
                    "processors": [
                        {
                            "name": "example_function_name",
                            "config": {
                                "calculationNodesTags": "ProcessorClassName"
                            }
                        }
                    ]
                }
            ]
        },
        "state_02": {
            "transitions": [
                {
                    "id": "transition_with_criterion_simple",
                    "next": "state_criterion_check_01",
                    "processors": [
                        {
                            "name": "example_function_name"
                        }
                    ],
                    "criterion": {
                        "type": "function",
                        "function": {
                            "name": "CriterionClassName"
                        }
                    }
                }
            ]
        }
    }
}

def test_conversion(input_json, format_name):
    """Test the conversion of a JSON format."""
    print(f"\n=== Testing {format_name} ===")
    
    try:
        result = convert_to_dto(
            input_workflow=input_json,
            calculation_node_tags="test_tag",
            model_name="TestModel",
            model_version=1,
            workflow_name="test_workflow",
            ai=False
        )
        
        print(f"✅ {format_name} conversion successful!")
        print(f"Generated {len(result.get('states', []))} states")
        print(f"Generated {len(result.get('transitions', []))} transitions")
        print(f"Generated {len(result.get('processes', []))} processes")
        print(f"Generated {len(result.get('criterias', []))} criteria")
        
        return True
        
    except Exception as e:
        print(f"❌ {format_name} conversion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("Testing Workflow Converter V2 Migration")
    print("=" * 50)
    
    old_success = test_conversion(old_format_json, "Old Format")
    new_success = test_conversion(new_format_json, "New Format")
    
    print("\n" + "=" * 50)
    if old_success and new_success:
        print("🎉 All tests passed! Migration successful!")
        return 0
    else:
        print("💥 Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

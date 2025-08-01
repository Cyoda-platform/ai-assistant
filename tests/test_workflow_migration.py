#!/usr/bin/env python3
"""
Tests for workflow migration functionality.

This module tests the migration of legacy workflows to the new processor-based architecture.
"""

import json
import tempfile
import unittest
from pathlib import Path
from migrate_workflows import WorkflowMigrator


class TestWorkflowMigration(unittest.TestCase):
    """Test cases for workflow migration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.migrator = WorkflowMigrator(self.temp_dir)

    def test_basic_workflow_migration(self):
        """Test migration of a basic workflow."""
        # Create test workflow
        test_workflow = {
            "initial_state": "none",
            "workflow_name": "test_workflow",
            "states": {
                "none": {
                    "transitions": {
                        "start": {
                            "next": "completed",
                            "action": {
                                "config": {
                                    "type": "agent",
                                    "model": {"provider": "openai", "model": "gpt-4"},
                                    "messages": [{"role": "user", "content": "Test message"}]
                                }
                            }
                        }
                    }
                },
                "completed": {
                    "transitions": {}
                }
            }
        }

        # Create temporary workflow file
        workflow_file = Path(self.temp_dir) / "test_workflow.json"
        with open(workflow_file, 'w') as f:
            json.dump(test_workflow, f)

        # Migrate workflow
        result = self.migrator.migrate_workflow(str(workflow_file))

        # Verify migration success
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow_name"], "test_workflow")
        self.assertGreater(len(result["created_files"]), 0)

        # Verify workflow file was created
        migrated_workflow_file = Path(self.temp_dir) / "workflows" / "test_workflow.json"
        self.assertTrue(migrated_workflow_file.exists())

        # Verify workflow structure
        with open(migrated_workflow_file) as f:
            migrated_workflow = json.load(f)

        self.assertEqual(migrated_workflow["version"], "1.0")
        self.assertEqual(migrated_workflow["name"], "test_workflow")
        self.assertEqual(migrated_workflow["initialState"], "none")
        self.assertTrue(migrated_workflow["active"])

    def test_agent_extraction(self):
        """Test extraction of inline agents to separate files."""
        test_workflow = {
            "initial_state": "none",
            "workflow_name": "agent_test",
            "states": {
                "none": {
                    "transitions": {
                        "process": {
                            "next": "completed",
                            "action": {
                                "config": {
                                    "type": "agent",
                                    "model": {"provider": "openai", "model": "gpt-4"},
                                    "messages": [{"role": "user", "content": "Process request"}],
                                    "publish": True,
                                    "approve": False,
                                    "allow_anonymous_users": True
                                }
                            }
                        }
                    }
                },
                "completed": {"transitions": {}}
            }
        }

        # Create and migrate workflow
        workflow_file = Path(self.temp_dir) / "test.json"
        with open(workflow_file, 'w') as f:
            json.dump(test_workflow, f)

        result = self.migrator.migrate_workflow(str(workflow_file))

        # Verify agent was created
        self.assertTrue(result["success"])
        self.assertEqual(result["agents_created"], 1)

        # Check agent file exists
        agent_dir = Path(self.temp_dir) / "agents" / "agent_test_none_process"
        agent_file = agent_dir / "agent.json"
        self.assertTrue(agent_file.exists())

        # Verify agent configuration
        with open(agent_file) as f:
            agent_config = json.load(f)

        self.assertEqual(agent_config["type"], "agent")
        self.assertTrue(agent_config["publish"])
        self.assertFalse(agent_config["approve"])
        self.assertTrue(agent_config["allow_anonymous_users"])

    def test_function_tool_creation(self):
        """Test creation of tool files for functions."""
        test_workflow = {
            "initial_state": "none",
            "workflow_name": "function_test",
            "states": {
                "none": {
                    "transitions": {
                        "execute": {
                            "next": "completed",
                            "action": {
                                "config": {
                                    "type": "function",
                                    "function": {
                                        "name": "test_function",
                                        "description": "Test function description",
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "param1": {"type": "string"}
                                            },
                                            "required": ["param1"]
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "completed": {"transitions": {}}
            }
        }

        # Create and migrate workflow
        workflow_file = Path(self.temp_dir) / "test.json"
        with open(workflow_file, 'w') as f:
            json.dump(test_workflow, f)

        result = self.migrator.migrate_workflow(str(workflow_file))

        # Verify tool was created
        self.assertTrue(result["success"])
        self.assertEqual(result["tools_created"], 1)

        # Check tool file exists
        tool_file = Path(self.temp_dir) / "tools" / "test_function.json"
        self.assertTrue(tool_file.exists())

        # Verify tool configuration
        with open(tool_file) as f:
            tool_config = json.load(f)

        self.assertEqual(tool_config["type"], "function")
        self.assertEqual(tool_config["function"]["name"], "test_function")
        self.assertEqual(tool_config["function"]["description"], "Test function description")

    def test_condition_migration(self):
        """Test migration of conditions to criteria."""
        test_workflow = {
            "initial_state": "none",
            "workflow_name": "condition_test",
            "states": {
                "none": {
                    "transitions": {
                        "check": {
                            "next": "completed",
                            "condition": {
                                "config": {
                                    "type": "function",
                                    "function": {
                                        "name": "is_ready",
                                        "description": "Check if ready"
                                    }
                                }
                            }
                        }
                    }
                },
                "completed": {"transitions": {}}
            }
        }

        # Create and migrate workflow
        workflow_file = Path(self.temp_dir) / "test.json"
        with open(workflow_file, 'w') as f:
            json.dump(test_workflow, f)

        result = self.migrator.migrate_workflow(str(workflow_file))

        # Verify migration success
        self.assertTrue(result["success"])

        # Check that condition function tool was created
        tool_file = Path(self.temp_dir) / "tools" / "is_ready.json"
        self.assertTrue(tool_file.exists())

        # Verify workflow has criterion
        workflow_file = Path(self.temp_dir) / "workflows" / "condition_test.json"
        with open(workflow_file) as f:
            migrated_workflow = json.load(f)

        transition = migrated_workflow["states"]["none"]["transitions"][0]
        self.assertIn("criterion", transition)
        self.assertEqual(transition["criterion"]["type"], "function")
        self.assertEqual(transition["criterion"]["function"]["name"], "is_ready")

    def test_message_extraction(self):
        """Test extraction of messages to separate files."""
        test_workflow = {
            "initial_state": "none",
            "workflow_name": "message_test",
            "states": {
                "none": {
                    "transitions": {
                        "notify": {
                            "next": "completed",
                            "action": {
                                "config": {
                                    "type": "notification",
                                    "notification": "Process completed successfully!"
                                }
                            }
                        }
                    }
                },
                "completed": {"transitions": {}}
            }
        }

        # Create and migrate workflow
        workflow_file = Path(self.temp_dir) / "test.json"
        with open(workflow_file, 'w') as f:
            json.dump(test_workflow, f)

        result = self.migrator.migrate_workflow(str(workflow_file))

        # Verify message was created
        self.assertTrue(result["success"])
        self.assertEqual(result["messages_created"], 1)

        # Check message file exists
        message_file = Path(self.temp_dir) / "messages" / "message_test" / "none_notify.md"
        self.assertTrue(message_file.exists())

        # Verify message content
        with open(message_file) as f:
            content = f.read()

        self.assertIn("# Notification", content)
        self.assertIn("Process completed successfully!", content)

    def test_complex_workflow_migration(self):
        """Test migration of a complex workflow with multiple components."""
        test_workflow = {
            "initial_state": "none",
            "workflow_name": "complex_test",
            "states": {
                "none": {
                    "transitions": {
                        "start": {
                            "next": "processing",
                            "action": {
                                "config": {
                                    "type": "agent",
                                    "model": {"provider": "openai", "model": "gpt-4"},
                                    "messages": [{"role": "user", "content": "Start processing"}],
                                    "tools": [
                                        {
                                            "type": "function",
                                            "function": {
                                                "name": "process_data",
                                                "description": "Process the data"
                                            }
                                        }
                                    ],
                                    "publish": True,
                                    "input": {"local_fs": ["input.json"]},
                                    "output": {"local_fs": ["output.json"]}
                                }
                            }
                        }
                    }
                },
                "processing": {
                    "transitions": {
                        "validate": {
                            "next": "completed",
                            "action": {
                                "config": {
                                    "type": "function",
                                    "function": {"name": "validate_result"}
                                }
                            },
                            "condition": {
                                "name": "is_valid"
                            }
                        }
                    }
                },
                "completed": {"transitions": {}}
            }
        }

        # Create and migrate workflow
        workflow_file = Path(self.temp_dir) / "test.json"
        with open(workflow_file, 'w') as f:
            json.dump(test_workflow, f)

        result = self.migrator.migrate_workflow(str(workflow_file))

        # Verify migration success
        self.assertTrue(result["success"])
        self.assertEqual(result["agents_created"], 1)
        self.assertGreaterEqual(result["tools_created"], 3)  # process_data, validate_result, is_valid

        # Verify workflow structure
        workflow_file = Path(self.temp_dir) / "workflows" / "complex_test.json"
        with open(workflow_file) as f:
            migrated_workflow = json.load(f)

        # Check processors and criteria
        none_transition = migrated_workflow["states"]["none"]["transitions"][0]
        self.assertEqual(len(none_transition["processors"]), 1)
        self.assertIn("input", none_transition["processors"][0])
        self.assertIn("output", none_transition["processors"][0])

        processing_transition = migrated_workflow["states"]["processing"]["transitions"][0]
        self.assertIn("criterion", processing_transition)


if __name__ == "__main__":
    unittest.main()

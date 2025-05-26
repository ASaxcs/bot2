"""
Patch for task loading issues in Lacia AI
"""
import json
import os

class TaskManagerPatch:
    def __init__(self, config_path_or_dict):
        """
        Initialize task manager with proper path handling
        """
        if isinstance(config_path_or_dict, str):
            # It's a file path
            self.config_path = config_path_or_dict
            self.load_from_file()
        elif isinstance(config_path_or_dict, dict):
            # It's already a dictionary
            self.tasks_data = config_path_or_dict
            self.config_path = None
        else:
            # Fallback to default
            self.config_path = "data/tasks.json"
            self.load_from_file()
    
    def load_from_file(self):
        """Load tasks from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.tasks_data = json.load(f)
            else:
                # Create default structure
                self.tasks_data = {
                    "scheduled_tasks": [],
                    "completed_tasks": [],
                    "pending_tasks": []
                }
                # Save default structure
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(self.tasks_data, f, indent=2)
        except Exception as e:
            print(f"Task loading error (patched): {e}")
            self.tasks_data = {"scheduled_tasks": [], "completed_tasks": [], "pending_tasks": []}
    
    def get_tasks(self):
        """Get all tasks"""
        return self.tasks_data
    
    def add_task(self, task):
        """Add a new task"""
        if "pending_tasks" not in self.tasks_data:
            self.tasks_data["pending_tasks"] = []
        self.tasks_data["pending_tasks"].append(task)
        self.save()
    
    def save(self):
        """Save tasks to file"""
        if self.config_path:
            try:
                with open(self.config_path, 'w') as f:
                    json.dump(self.tasks_data, f, indent=2)
            except Exception as e:
                print(f"Error saving tasks: {e}")

# Usage example:
# Replace TaskManager initialization with:
# task_manager = TaskManagerPatch("data/tasks.json")

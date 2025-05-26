"""
Task Manager stub for Lacia AI
Provides basic task management functionality
"""
import json
import os
from datetime import datetime

class TaskManager:
    def __init__(self, config_path="data/tasks.json"):
        """Initialize task manager with config file path"""
        self.config_path = config_path
        self.tasks_data = {}
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.tasks_data = json.load(f)
            else:
                self.tasks_data = {
                    "scheduled_tasks": [],
                    "completed_tasks": [],
                    "pending_tasks": []
                }
                self.save_tasks()
        except Exception as e:
            print(f"Task loading error: {e}")
            self.tasks_data = {
                "scheduled_tasks": [],
                "completed_tasks": [],
                "pending_tasks": []
            }
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, task_data):
        """Add a new task"""
        if "pending_tasks" not in self.tasks_data:
            self.tasks_data["pending_tasks"] = []
        
        task_data["id"] = f"task_{len(self.tasks_data['pending_tasks']):03d}"
        task_data["created_at"] = datetime.now().isoformat()
        task_data["status"] = "pending"
        
        self.tasks_data["pending_tasks"].append(task_data)
        self.save_tasks()
        return task_data["id"]
    
    def get_tasks(self, status=None):
        """Get tasks by status"""
        if status is None:
            return self.tasks_data
        
        return self.tasks_data.get(f"{status}_tasks", [])
    
    def complete_task(self, task_id):
        """Mark task as completed"""
        # Move from pending to completed
        pending = self.tasks_data.get("pending_tasks", [])
        completed = self.tasks_data.get("completed_tasks", [])
        
        for i, task in enumerate(pending):
            if task.get("id") == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                completed.append(task)
                pending.pop(i)
                self.save_tasks()
                return True
        
        return False

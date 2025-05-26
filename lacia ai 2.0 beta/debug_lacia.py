#!/usr/bin/env python3
"""
Debug script for Lacia AI errors
"""
import json
import traceback
import sys
import os

def debug_task_loading():
    """Debug task loading issues"""
    print("🔧 Debugging task loading...")
    
    # Check if data/tasks.json exists and is valid
    tasks_file = "data/tasks.json"
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, 'r') as f:
                tasks_data = json.load(f)
            print(f"✅ {tasks_file} is valid JSON")
            print(f"📊 Tasks data type: {type(tasks_data)}")
            print(f"📋 Keys: {list(tasks_data.keys()) if isinstance(tasks_data, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"❌ Error reading {tasks_file}: {e}")
    else:
        print(f"❌ {tasks_file} not found")
    
    # Look for task manager initialization
    try:
        # Try to import and check task-related modules
        sys.path.append('.')
        
        # Check if there's a task manager module
        possible_modules = [
            'core.cognition.processor',
            'system.task_manager', 
            'core.task_manager',
            'tasks.manager'
        ]
        
        for module_name in possible_modules:
            try:
                __import__(module_name)
                print(f"✅ Module {module_name} can be imported")
            except ImportError as e:
                print(f"⚠️  Module {module_name} not found: {e}")
            except Exception as e:
                print(f"❌ Error importing {module_name}: {e}")
                
    except Exception as e:
        print(f"❌ Error during module checking: {e}")

def debug_memory_error():
    """Debug memory retrieval issues"""
    print("\n🧠 Debugging memory retrieval...")
    
    # Check memory-related files
    memory_files = [
        "data/experiences.json",
        "data/memory.json",
        "data/short_term_memory.json"
    ]
    
    for memory_file in memory_files:
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    memory_data = json.load(f)
                print(f"✅ {memory_file} is valid")
                print(f"📊 Data type: {type(memory_data)}")
                if isinstance(memory_data, list):
                    print(f"📝 List length: {len(memory_data)}")
                elif isinstance(memory_data, dict):
                    print(f"🔑 Keys: {list(memory_data.keys())}")
            except Exception as e:
                print(f"❌ Error reading {memory_file}: {e}")
        else:
            print(f"ℹ️  {memory_file} not found")

if __name__ == "__main__":
    print("🔍 LACIA AI DEBUG TOOL")
    print("=" * 40)
    
    debug_task_loading()
    debug_memory_error()
    
    print("\n" + "=" * 40)
    print("🎯 Next steps:")
    print("1. Check the output above for specific errors")
    print("2. Look at the module import results")
    print("3. Verify all JSON files are properly formatted")
    print("=" * 40)

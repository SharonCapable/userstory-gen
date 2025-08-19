# check_structure.py - Run this to see your directory structure
import os

def show_tree(path, prefix="", max_depth=3, current_depth=0):
    """Display directory tree structure"""
    if current_depth >= max_depth:
        return
        
    items = []
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return
    
    for i, item in enumerate(items):
        if item.startswith('.'):
            continue
            
        item_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item}")
        
        if os.path.isdir(item_path) and not item.startswith('__pycache__'):
            next_prefix = prefix + ("    " if is_last else "│   ")
            show_tree(item_path, next_prefix, max_depth, current_depth + 1)

print("📁 Current Directory Structure:")
print("backend/")
show_tree(".", "")

print("\n📝 Checking for required model files:")
model_files = ['project.py', 'epic.py', 'user_story.py']
models_path = 'app/models'

for file in model_files:
    file_path = os.path.join(models_path, file)
    if os.path.exists(file_path):
        print(f"✅ {file_path} exists")
    else:
        print(f"❌ {file_path} is MISSING")
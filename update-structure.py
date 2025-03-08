import os
import shutil
from pathlib import Path

def create_directory_structure():
    """
    Create the directory structure for the updated application.
    This creates any missing directories and __init__.py files.
    """
    # Base directories
    directories = [
        "app/repositories",
        "app/utils",
        "app/api/routes"
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create __init__.py in each directory if it doesn't exist
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Auto-generated __init__.py\n")
    
    # Copy files to the right locations
    file_operations = [
        # Create storage_routes.py in the routes directory
        {
            "action": "create",
            "path": "app/api/routes/storage_routes.py",
            "content_from": "storage-routes"
        },
        # Create wine_routes.py in the routes directory
        {
            "action": "create",
            "path": "app/api/routes/wine_routes.py",
            "content_from": "wine-routes"
        },
        # Create storage_repository.py
        {
            "action": "create",
            "path": "app/repositories/storage_repository.py",
            "content_from": "storage-repository"
        },
        # Create wine_repository.py
        {
            "action": "create",
            "path": "app/repositories/wine_repository.py",
            "content_from": "wine-repository"
        },
        # Create position_validator.py
        {
            "action": "create",
            "path": "app/utils/position_validator.py",
            "content_from": "position-validator"
        },
        # Create dependencies.py
        {
            "action": "create",
            "path": "app/dependencies.py",
            "content_from": "dependencies"
        },
        # Update the main router
        {
            "action": "create",
            "path": "app/api/routes/__init__.py",
            "content_from": "main-router"
        },
        # Update storage model
        {
            "action": "update",
            "path": "app/models/storage.py",
            "content_from": "storage-model"
        },
        # Update storage schema
        {
            "action": "update",
            "path": "app/schemas/storage.py",
            "content_from": "storage-schema"
        },
        # Update wine model
        {
            "action": "update",
            "path": "app/models/wine.py",
            "content_from": "wine-model-update"
        }
    ]
    
    # Read content from artifacts
    artifacts = {
        "storage-routes": Path("storage-routes").read_text() if Path("storage-routes").exists() else "",
        "wine-routes": Path("wine-routes").read_text() if Path("wine-routes").exists() else "",
        "storage-repository": Path("storage-repository").read_text() if Path("storage-repository").exists() else "",
        "wine-repository": Path("wine-repository").read_text() if Path("wine-repository").exists() else "",
        "position-validator": Path("position-validator").read_text() if Path("position-validator").exists() else "",
        "dependencies": Path("dependencies").read_text() if Path("dependencies").exists() else "",
        "main-router": Path("main-router").read_text() if Path("main-router").exists() else "",
        "storage-model": Path("storage-model").read_text() if Path("storage-model").exists() else "",
        "storage-schema": Path("storage-schema").read_text() if Path("storage-schema").exists() else "",
        "wine-model-update": Path("wine-model-update").read_text() if Path("wine-model-update").exists() else ""
    }
    
    # Execute file operations
    for operation in file_operations:
        if operation["action"] == "create":
            with open(operation["path"], "w") as f:
                f.write(artifacts[operation["content_from"]])
            print(f"Created: {operation['path']}")
        elif operation["action"] == "update":
            with open(operation["path"], "w") as f:
                f.write(artifacts[operation["content_from"]])
            print(f"Updated: {operation['path']}")
    
    print("\nDirectory structure updated successfully!")
    print("You may need to run database migrations to apply the model changes.")

if __name__ == "__main__":
    create_directory_structure()
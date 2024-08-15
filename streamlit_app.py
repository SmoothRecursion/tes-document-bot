import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Add the 'app' directory to the Python path
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, app_dir)

from app.main import main

if __name__ == "__main__":
    main()

"""
Test script to verify analyzer router imports work correctly
"""

import sys
import os

# Add the Helper-APIs directory to the path
helper_apis_path = os.path.join(os.getcwd(), 'Helper-APIs')
sys.path.insert(0, helper_apis_path)

# Add the app directory to sys.path for proper imports
app_path = os.path.join(helper_apis_path, 'document-analyzer-api', 'app')
sys.path.insert(0, app_path)

try:
    # Try importing the analyzer router
    import importlib.util

    analyzer_router_path = os.path.join(helper_apis_path, 'document-analyzer-api', 'app', 'routers', 'analyzer.py')
    spec = importlib.util.spec_from_file_location("analyzer_router", analyzer_router_path)
    analyzer_router_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyzer_router_module)
    analyzer_router = analyzer_router_module.router

    print("✅ Analyzer router imported successfully!")
    print(f"Router: {analyzer_router}")
    print(f"Router routes: {len(analyzer_router.routes)}")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

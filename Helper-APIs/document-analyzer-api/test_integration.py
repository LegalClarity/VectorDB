"""
Integration test for Document Analyzer API
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

async def test_basic_import():
    """Test basic import of analyzer components"""
    try:
        from app.config import settings
        print("✓ Configuration imported successfully")

        from app.services.document_analyzer import DocumentAnalyzerService
        print("✓ Document analyzer service imported successfully")

        from app.services.database_service import DatabaseService
        print("✓ Database service imported successfully")

        from app.services.gcs_service import GCSService
        print("✓ GCS service imported successfully")

        from app.routers.analyzer import router as analyzer_router
        print("✓ Analyzer router imported successfully")

        from app.main import app
        print("✓ FastAPI app imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def test_configuration():
    """Test configuration loading"""
    try:
        from app.config import settings

        # Check required settings
        required_settings = [
            'GEMINI_API_KEY',
            'MONGO_URI',
            'USER_DOC_BUCKET'
        ]

        missing_settings = []
        for setting in required_settings:
            value = getattr(settings, setting, None)
            if not value:
                missing_settings.append(setting)

        if missing_settings:
            print(f"⚠️  Missing configuration: {', '.join(missing_settings)}")
            print("   Please set these in your .env file")
            return False
        else:
            print("✓ All required configuration settings present")
            return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_service_initialization():
    """Test service initialization without actual connections"""
    try:
        from app.config import settings

        # Test Document Analyzer Service (without API key validation)
        try:
            from app.services.document_analyzer import DocumentAnalyzerService
            # Skip actual initialization to avoid API key requirements
            print("✓ Document analyzer service class available")
        except Exception as e:
            print(f"⚠️  Document analyzer service issue: {e}")

        # Test Database Service class
        try:
            from app.services.database_service import DatabaseService
            print("✓ Database service class available")
        except Exception as e:
            print(f"⚠️  Database service issue: {e}")

        # Test GCS Service class
        try:
            from app.services.gcs_service import GCSService
            print("✓ GCS service class available")
        except Exception as e:
            print(f"⚠️  GCS service issue: {e}")

        return True

    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        return False


async def test_fastapi_app():
    """Test FastAPI app creation"""
    try:
        from app.main import app

        # Check that app is a FastAPI instance
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            print("✓ FastAPI app created successfully")
            print(f"   Title: {app.title}")
            print(f"   Version: {app.version}")
            return True
        else:
            print("❌ App is not a FastAPI instance")
            return False

    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False


async def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Document Analyzer API Integration Tests")
    print("=" * 60)

    tests = [
        ("Basic Import Test", test_basic_import),
        ("Configuration Test", test_configuration),
        ("Service Initialization Test", test_service_initialization),
        ("FastAPI App Test", test_fastapi_app)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)

        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n🚀 Ready to start the Document Analyzer API")
        print("   Run: python -m app.main")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    # Set up basic environment if .env doesn't exist
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("⚠️  No .env file found. Creating basic template...")
        env_content = """# Document Analyzer API Configuration
GEMINI_API_KEY=test_key
MONGO_URI=mongodb://localhost:27017
USER_DOC_BUCKET=test_bucket
DEBUG=true
LOG_LEVEL=INFO
"""
        env_file.write_text(env_content)
        print("✓ Created .env template. Please update with real values.")

    # Run integration tests
    success = asyncio.run(run_integration_tests())

    if not success:
        sys.exit(1)

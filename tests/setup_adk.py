#!/usr/bin/env python3
"""
Quick setup script for Google ADK migration
"""

import os
import subprocess
import sys


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required for Google ADK")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def install_google_adk():
    """Install Google ADK package"""
    print("📦 Installing Google ADK...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-adk"])
        print("✅ Google ADK installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Google ADK: {e}")
        return False


def check_authentication():
    """Check for authentication setup"""
    print("🔐 Checking authentication setup...")
    
    auth_methods = []
    
    # Check for service account
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if os.path.exists(creds_path):
            auth_methods.append("✅ Service Account (recommended)")
        else:
            print(f"⚠️  GOOGLE_APPLICATION_CREDENTIALS points to non-existent file: {creds_path}")
    
    # Check for API key
    if os.getenv('GOOGLE_API_KEY'):
        auth_methods.append("✅ API Key")
    
    # Check for gcloud
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'ACTIVE' in result.stdout:
            auth_methods.append("✅ Application Default Credentials")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    if auth_methods:
        print("Authentication methods found:")
        for method in auth_methods:
            print(f"  {method}")
        return True
    else:
        print("❌ No authentication found!")
        print("\n💡 Setup options:")
        print("1. API Key (easiest): export GOOGLE_API_KEY='your-key'")
        print("2. Service Account: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json'")
        print("3. gcloud CLI: gcloud auth application-default login")
        print("\nSee ADK_SETUP_GUIDE.md for detailed instructions")
        return False


def test_import():
    """Test if Google ADK can be imported"""
    print("🧪 Testing Google ADK import...")
    try:
        import google.adk
        print("✅ Google ADK import successful")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Google ADK: {e}")
        return False


def create_env_template():
    """Create a .env template file"""
    env_template = """# Google ADK Configuration
# Choose ONE of the following authentication methods:

# Option 1: API Key (easiest for testing)
# GOOGLE_API_KEY=your-api-key-here

# Option 2: Service Account (recommended for production)
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account.json
# GOOGLE_CLOUD_PROJECT=your-project-id

# Option 3: Application Default Credentials
# (Set up with: gcloud auth application-default login)
# GOOGLE_CLOUD_PROJECT=your-project-id

# Optional settings
# GOOGLE_CLOUD_REGION=us-central1
"""
    
    if not os.path.exists('.env.adk.template'):
        with open('.env.adk.template', 'w') as f:
            f.write(env_template)
        print("✅ Created .env.adk.template file")
        print("💡 Copy this to .env and fill in your credentials")
    else:
        print("ℹ️  .env.adk.template already exists")


def main():
    """Main setup function"""
    print("🚀 Google ADK Setup Script")
    print("=" * 40)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing Google ADK", install_google_adk),
        ("Testing import", test_import),
        ("Checking authentication", check_authentication),
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            results.append((step_name, False))
    
    # Create environment template
    print(f"\n--- Creating environment template ---")
    create_env_template()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {step_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} steps completed successfully")
    
    if passed == total:
        print("\n🎉 Setup completed successfully!")
        print("\n🔄 Next steps:")
        print("1. Set up authentication (see .env.adk.template)")
        print("2. Run: python test_adk_migration.py")
        print("3. Update factory configuration to use GoogleAdkAgent")
    else:
        print("\n⚠️  Some setup steps failed. Please address the issues above.")
        
        if not results[1][1]:  # Installation failed
            print("\n💡 Try manual installation:")
            print("pip install --upgrade pip")
            print("pip install google-adk")
        
        if not results[3][1]:  # Authentication failed
            print("\n💡 Set up authentication:")
            print("See ADK_SETUP_GUIDE.md for detailed instructions")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

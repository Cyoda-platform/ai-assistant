#!/usr/bin/env python3
"""
Quick verification script for correct MCP import
"""

def test_mcp_import():
    """Test the correct MCP import"""
    print("🔍 Testing correct MCP import...")
    
    try:
        # Test the correct import
        from google.adk.tools.mcp_tool import MCPTool
        print("✅ Correct import successful: from google.adk.tools.mcp_tool import MCPTool")
        return True
    except ImportError as e:
        print(f"❌ Correct import failed: {e}")
        
        # Try alternative imports to help debug
        alternatives = [
            "google.adk.tools.mcp",
            "google.adk.tools",
            "google.adk.mcp",
            "google.adk.mcp_tool"
        ]
        
        print("🔍 Trying alternative imports...")
        for alt in alternatives:
            try:
                __import__(alt)
                print(f"  ✅ {alt} - available")
            except ImportError:
                print(f"  ❌ {alt} - not available")
        
        return False


def test_google_adk_version():
    """Check Google ADK version"""
    print("📦 Checking Google ADK version...")
    
    try:
        import google.adk
        if hasattr(google.adk, '__version__'):
            print(f"✅ Google ADK version: {google.adk.__version__}")
        else:
            print("ℹ️  Google ADK installed (version not available)")
        return True
    except ImportError:
        print("❌ Google ADK not installed")
        print("💡 Install with: pip install google-adk")
        return False


def main():
    """Main verification function"""
    print("🚀 MCP Import Verification")
    print("=" * 40)
    
    # Test Google ADK installation
    adk_ok = test_google_adk_version()
    
    if not adk_ok:
        print("\n❌ Please install Google ADK first:")
        print("pip install google-adk")
        return False
    
    # Test MCP import
    mcp_ok = test_mcp_import()
    
    print("\n" + "=" * 40)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 40)
    
    if mcp_ok:
        print("✅ MCP import verification successful!")
        print("✅ You can use: from google.adk.tools.mcp_tool import MCPTool")
        print("\n🔄 Next steps:")
        print("1. Run: python test_mcp_integration.py")
        print("2. Configure MCP servers in your environment")
        print("3. Test with your application")
    else:
        print("❌ MCP import verification failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Update Google ADK: pip install --upgrade google-adk")
        print("2. Check if you have the latest version")
        print("3. Try reinstalling: pip uninstall google-adk && pip install google-adk")
    
    return mcp_ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

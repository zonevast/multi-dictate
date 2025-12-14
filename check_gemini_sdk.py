try:
    import google.generativeai as genai
    print("✅ google-generativeai SDK is installed")
except ImportError:
    print("❌ google-generativeai SDK is NOT installed")

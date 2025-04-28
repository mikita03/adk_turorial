"""
Google Agent Development Kit (ADK) Exploration
This script explores the Google Generative AI library to understand its capabilities
and how it relates to the Agent Development Kit (ADK).
"""

import os
import sys

try:
    import google.generativeai as genai
    print("Successfully imported google.generativeai")
    print("Available modules and functions:")
    print(dir(genai))
except ImportError as e:
    print(f"Error importing google.generativeai: {e}")
    sys.exit(1)

adk_related = [item for item in dir(genai) if 'agent' in item.lower() or 'adk' in item.lower()]
print("\nADK or Agent related modules/functions:")
print(adk_related if adk_related else "No ADK or Agent related modules/functions found")

print("\nVersion information:")
if hasattr(genai, '__version__'):
    print(f"google.generativeai version: {genai.__version__}")
else:
    print("Version information not available")

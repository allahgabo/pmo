"""
Verify the AI views.py file has the correct formatting code
This checks the actual Python file - no server needed
"""
import os

print("=" * 60)
print("FILE VERIFICATION CHECK")
print("=" * 60)

# Check if we're in the right directory
if not os.path.exists('ai_engine'):
    print("\n❌ ERROR: ai_engine folder not found!")
    print("Make sure you're in: D:\\pmo-ai-assistant\\pmo-ai-assistant-github")
    exit(1)

# Read the views.py file
views_path = 'ai_engine/views.py'
if not os.path.exists(views_path):
    print(f"\n❌ ERROR: {views_path} not found!")
    exit(1)

with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print(f"\n✅ File found: {views_path}")
print(f"   Size: {len(content)} bytes")
print(f"   Lines: {len(lines)}")

# Check for the critical fix on line 155
print("\n" + "-" * 60)
print("Checking Line 155 (response key handler):")
print("-" * 60)

if len(lines) >= 155:
    line_155 = lines[154]  # 0-indexed
    print(f"Line 155: {line_155.strip()}")
    
    if ".replace('\\n', '<br>')" in line_155 or '.replace("\\n", "<br>")' in line_155:
        print("✅ CORRECT! Has .replace('\\n', '<br>')")
    else:
        print("❌ WRONG! Missing or incorrect .replace()")
else:
    print("❌ ERROR: File too short!")

# Check for the _format_ai_response method
print("\n" + "-" * 60)
print("Checking _format_ai_response method:")
print("-" * 60)

if 'def _format_ai_response' in content:
    print("✅ Method exists")
    
    # Count <br> occurrences in the method
    method_start = content.find('def _format_ai_response')
    method_section = content[method_start:method_start+5000]
    br_count = method_section.count('<br>')
    
    print(f"   Contains {br_count} '<br>' tags")
    
    if br_count >= 20:
        print("   ✅ Has proper HTML formatting!")
    else:
        print("   ❌ Not enough <br> tags!")
else:
    print("❌ Method not found!")

# Check for new structure handlers
print("\n" + "-" * 60)
print("Checking for new JSON structure handlers:")
print("-" * 60)

checks = [
    ("'summary' handler", "'summary' in ai_response"),
    ("'critical_risks' handler", "'critical_risks' in ai_response"),
    ("'immediate_actions' handler", "'immediate_actions' in ai_response"),
]

for name, search in checks:
    if search in content:
        print(f"✅ {name}")
    else:
        print(f"❌ {name} - MISSING!")

# Final verdict
print("\n" + "=" * 60)

has_replace = ".replace('\\n', '<br>')" in content or '.replace("\\n", "<br>")' in content
has_method = 'def _format_ai_response' in content
has_br = content.count('<br>') >= 20

if has_replace and has_method and has_br:
    print("✅ FILE IS CORRECT!")
    print("\nYour views.py has all the fixes.")
    print("\nIf responses still show on one line, the issue is:")
    print("1. Python cache - Clear with: clear_cache.ps1")
    print("2. Server needs restart")
    print("3. Browser cache - Use Incognito mode")
else:
    print("❌ FILE NEEDS TO BE REPLACED!")
    print("\nDownload: ai_engine-views-COMPLETE.py")
    print("Replace: ai_engine\\views.py")

print("=" * 60)
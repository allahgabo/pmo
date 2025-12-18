import requests
import json

BASE_URL = 'http://localhost:8000'

def test_api():
    print("=" * 60)
    print("PMO AI Assistant - API Test Suite")
    print("=" * 60)
    print()
    
    tests = []
    
    # Test 1: Dashboard Stats
    print("Test 1: Dashboard Statistics")
    try:
        response = requests.get(f'{BASE_URL}/api/projects/dashboard_stats/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Total Projects: {data['total_projects']}")
            print(f"   On Track: {data['by_status']['on_track']}")
            print(f"   At Risk: {data['by_status']['at_risk']}")
            print(f"   Delayed: {data['by_status']['delayed']}")
            tests.append(True)
        else:
            print(f"❌ Failed with status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Error: {e}")
        tests.append(False)
    print()
    
    # Test 2: List Projects
    print("Test 2: List All Projects")
    try:
        response = requests.get(f'{BASE_URL}/api/projects/')
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', data) if isinstance(data, dict) else data
            print(f"✅ Success! Found {len(results)} projects")
            if results:
                print(f"   First project: {results[0]['name']}")
            tests.append(True)
        else:
            print(f"❌ Failed with status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Error: {e}")
        tests.append(False)
    print()
    
    # Test 3: At-Risk Projects
    print("Test 3: At-Risk Projects")
    try:
        response = requests.get(f'{BASE_URL}/api/projects/at_risk_projects/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} at-risk projects")
            for p in data[:3]:
                print(f"   - {p['name']} (SPI: {p['spi']})")
            tests.append(True)
        else:
            print(f"❌ Failed with status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Error: {e}")
        tests.append(False)
    print()
    
    # Test 4: Risks
    print("Test 4: List Risks")
    try:
        response = requests.get(f'{BASE_URL}/api/risks/')
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', data) if isinstance(data, dict) else data
            print(f"✅ Success! Found {len(results)} risks")
            high_risks = [r for r in results if r.get('severity') in ['high', 'critical']]
            print(f"   High/Critical risks: {len(high_risks)}")
            tests.append(True)
        else:
            print(f"❌ Failed with status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Error: {e}")
        tests.append(False)
    print()
    
    # Test 5: AI Portfolio Summary
    print("Test 5: AI Portfolio Summary")
    try:
        response = requests.get(f'{BASE_URL}/api/ai/portfolio-summary/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! AI Analysis received")
            if 'health_summary' in data:
                print(f"   Status: {data['health_summary'].get('status')}")
                print(f"   Assessment: {data['health_summary'].get('overall_assessment')[:60]}...")
            tests.append(True)
        else:
            print(f"❌ Failed with status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Error: {e}")
        tests.append(False)
    print()
    
    # Test 6: AI Question
    print("Test 6: Ask AI a Question")
    try:
        response = requests.post(
            f'{BASE_URL}/api/ai/ask/',
            json={'question': 'What is the overall portfolio health?'},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! AI Response received")
            print(f"   Response preview: {str(data)[:100]}...")
            tests.append(True)
        else:
            print(f"❌ Failed with status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Error: {e}")
        tests.append(False)
    print()
    
    # Summary
    print("=" * 60)
    print(f"Test Results: {sum(tests)}/{len(tests)} passed")
    if all(tests):
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    print("=" * 60)

if __name__ == '__main__':
    test_api()

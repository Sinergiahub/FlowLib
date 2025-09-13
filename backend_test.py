import requests
import sys
import json
from datetime import datetime
import os

class FlowLibAPITester:
    def __init__(self, base_url="https://flowlib.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.template_ids = []
        self.errors = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   Details: {details}")
                self.errors.append(f"{name}: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:100]}...")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.errors.append(f"{name}: Status {response.status_code}, Expected {expected_status}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.errors.append(f"{name}: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_templates(self):
        """Test getting all templates"""
        success, response = self.run_test(
            "Get All Templates",
            "GET",
            "templates",
            200
        )
        if success and isinstance(response, list):
            self.template_ids = [template.get('id') for template in response if template.get('id')]
            print(f"   Found {len(response)} templates")
            if response:
                template = response[0]
                required_fields = ['id', 'title', 'description', 'platform', 'author_name']
                missing_fields = [field for field in required_fields if field not in template]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in template: {missing_fields}")
                else:
                    print(f"   ✅ Template structure looks good")
        return success

    def test_get_template_by_id(self):
        """Test getting a specific template by ID"""
        if not self.template_ids:
            print("❌ No template IDs available for testing")
            return False
            
        template_id = self.template_ids[0]
        success, response = self.run_test(
            f"Get Template by ID ({template_id[:8]}...)",
            "GET",
            f"templates/{template_id}",
            200
        )
        if success:
            print(f"   Template title: {response.get('title', 'N/A')}")
        return success

    def test_get_categories(self):
        """Test getting categories"""
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "categories",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} categories")
            if response:
                category_names = [cat.get('name') for cat in response]
                print(f"   Categories: {', '.join(category_names[:3])}...")
        return success

    def test_get_tools(self):
        """Test getting tools"""
        success, response = self.run_test(
            "Get Tools",
            "GET",
            "tools",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} tools")
            if response:
                tool_names = [tool.get('name') for tool in response]
                print(f"   Tools: {', '.join(tool_names[:3])}...")
        return success

    def test_get_featured_templates(self):
        """Test getting featured templates"""
        success, response = self.run_test(
            "Get Featured Templates",
            "GET",
            "featured",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} featured templates")
        return success

    def test_search_functionality(self):
        """Test search functionality"""
        search_terms = ["IA", "SEO", "TikTok", "automação"]
        all_passed = True
        
        for term in search_terms:
            success, response = self.run_test(
                f"Search Templates - '{term}'",
                "GET",
                "templates",
                200,
                params={"search": term}
            )
            if success and isinstance(response, list):
                print(f"   Found {len(response)} results for '{term}'")
            all_passed = all_passed and success
            
        return all_passed

    def test_filter_functionality(self):
        """Test filter functionality"""
        filters = [
            {"platform": "n8n"},
            {"platform": "Make"},
            {"category": "marketing"},
            {"tool": "openai"}
        ]
        all_passed = True
        
        for filter_params in filters:
            filter_name = f"{list(filter_params.keys())[0]}={list(filter_params.values())[0]}"
            success, response = self.run_test(
                f"Filter Templates - {filter_name}",
                "GET",
                "templates",
                200,
                params=filter_params
            )
            if success and isinstance(response, list):
                print(f"   Found {len(response)} results for {filter_name}")
            all_passed = all_passed and success
            
        return all_passed

    def test_download_tracking(self):
        """Test download tracking"""
        if not self.template_ids:
            print("❌ No template IDs available for download testing")
            return False
            
        template_id = self.template_ids[0]
        success, response = self.run_test(
            f"Download Template ({template_id[:8]}...)",
            "POST",
            f"templates/{template_id}/download",
            200
        )
        return success

    def test_invalid_template_id(self):
        """Test error handling for invalid template ID"""
        success, response = self.run_test(
            "Invalid Template ID",
            "GET",
            "templates/invalid-id-123",
            404
        )
        return success

def main():
    print("🚀 Starting FlowLib API Tests")
    print("=" * 50)
    
    tester = FlowLibAPITester()
    
    # Run all tests
    tests = [
        tester.test_root_endpoint,
        tester.test_get_templates,
        tester.test_get_template_by_id,
        tester.test_get_categories,
        tester.test_get_tools,
        tester.test_get_featured_templates,
        tester.test_search_functionality,
        tester.test_filter_functionality,
        tester.test_download_tracking,
        tester.test_invalid_template_id
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
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

    def test_csv_import_basic(self):
        """Test CSV import with basic test file"""
        print("\n🔍 Testing CSV Import - Basic Import...")
        
        try:
            with open('/app/test-import.csv', 'rb') as f:
                files = {'file': ('test-import.csv', f, 'text/csv')}
                response = requests.post(f"{self.api_url}/import/templates", files=files)
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    expected_keys = ['inserted', 'updated', 'deleted', 'errors']
                    has_all_keys = all(key in data for key in expected_keys)
                    
                    if has_all_keys:
                        print(f"   📊 Import Results: Inserted: {data['inserted']}, Updated: {data['updated']}, Deleted: {data['deleted']}, Errors: {len(data['errors'])}")
                        if data['errors']:
                            print(f"   ⚠️  Errors: {data['errors']}")
                        success = data['inserted'] > 0 or data['updated'] > 0  # Should have some successful operations
                    else:
                        success = False
                        
                self.log_test("CSV Import - Basic", success, f"Status: {response.status_code}, Response: {response.text[:200] if not success else 'OK'}")
                return success
                
        except FileNotFoundError:
            self.log_test("CSV Import - Basic", False, "test-import.csv file not found")
            return False
        except Exception as e:
            self.log_test("CSV Import - Basic", False, str(e))
            return False

    def test_csv_import_update_delete(self):
        """Test CSV import with update and delete operations"""
        print("\n🔍 Testing CSV Import - Update & Delete...")
        
        try:
            with open('/app/test-update.csv', 'rb') as f:
                files = {'file': ('test-update.csv', f, 'text/csv')}
                response = requests.post(f"{self.api_url}/import/templates", files=files)
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    print(f"   📊 Update Results: Inserted: {data['inserted']}, Updated: {data['updated']}, Deleted: {data['deleted']}, Errors: {len(data['errors'])}")
                    if data['errors']:
                        print(f"   ⚠️  Errors: {data['errors']}")
                        
                self.log_test("CSV Import - Update/Delete", success, f"Status: {response.status_code}")
                return success
                
        except FileNotFoundError:
            self.log_test("CSV Import - Update/Delete", False, "test-update.csv file not found")
            return False
        except Exception as e:
            self.log_test("CSV Import - Update/Delete", False, str(e))
            return False

    def test_csv_import_validation_errors(self):
        """Test CSV import with validation errors"""
        print("\n🔍 Testing CSV Import - Validation Errors...")
        
        try:
            with open('/app/test-errors.csv', 'rb') as f:
                files = {'file': ('test-errors.csv', f, 'text/csv')}
                response = requests.post(f"{self.api_url}/import/templates", files=files)
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    print(f"   📊 Error Test Results: Inserted: {data['inserted']}, Updated: {data['updated']}, Deleted: {data['deleted']}, Errors: {len(data['errors'])}")
                    print(f"   ⚠️  Expected Errors: {data['errors']}")
                    
                    # Should have errors for validation failures
                    success = len(data['errors']) > 0
                        
                self.log_test("CSV Import - Validation Errors", success, f"Status: {response.status_code}, Errors found: {len(data.get('errors', [])) if success else 0}")
                return success
                
        except FileNotFoundError:
            self.log_test("CSV Import - Validation Errors", False, "test-errors.csv file not found")
            return False
        except Exception as e:
            self.log_test("CSV Import - Validation Errors", False, str(e))
            return False

    def test_csv_import_invalid_file(self):
        """Test CSV import with invalid file"""
        print("\n🔍 Testing CSV Import - Invalid File...")
        
        try:
            # Test with non-CSV file
            files = {'file': ('test.txt', b'not a csv file', 'text/plain')}
            response = requests.post(f"{self.api_url}/import/templates", files=files)
            
            # Should return 400 for non-CSV file
            success = response.status_code == 400
            self.log_test("CSV Import - Invalid File Type", success, f"Status: {response.status_code}")
            return success
            
        except Exception as e:
            self.log_test("CSV Import - Invalid File Type", False, str(e))
            return False

    def test_template_by_slug(self):
        """Test template by slug endpoint"""
        print("\n🔍 Testing Template by Slug Endpoint...")
        
        # First get a template to test with
        try:
            response = requests.get(f"{self.api_url}/templates")
            if response.status_code == 200 and response.json():
                template = response.json()[0]
                slug = template.get('slug')
                
                if slug:
                    # Test getting template by slug
                    slug_response = requests.get(f"{self.api_url}/templates/slug/{slug}")
                    success = slug_response.status_code == 200
                    self.log_test(f"Get template by slug ({slug})", success, f"Status: {slug_response.status_code}")
                    return success
                else:
                    self.log_test("Get template by slug", False, "No slug found in template")
                    return False
            else:
                self.log_test("Get template by slug", False, "No templates available for testing")
                return False
        except Exception as e:
            self.log_test("Get template by slug", False, str(e))
            return False

    def test_csv_preview_with_file(self):
        """Test CSV preview endpoint with file upload"""
        print("\n🔍 Testing CSV Preview - File Upload...")
        
        try:
            with open('/app/test-import.csv', 'rb') as f:
                files = {'file': ('test-import.csv', f, 'text/csv')}
                response = requests.post(f"{self.api_url}/import/preview", files=files)
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    expected_keys = ['total_rows', 'insert_count', 'update_count', 'delete_count', 'error_count', 'rows']
                    has_all_keys = all(key in data for key in expected_keys)
                    
                    if has_all_keys:
                        print(f"   📊 Preview Results: Total: {data['total_rows']}, Insert: {data['insert_count']}, Update: {data['update_count']}, Delete: {data['delete_count']}, Errors: {data['error_count']}")
                        
                        # Verify rows structure
                        if data['rows']:
                            row = data['rows'][0]
                            row_keys = ['line_number', 'slug', 'title', 'action', 'status', 'message', 'data']
                            has_row_structure = all(key in row for key in row_keys)
                            success = has_row_structure
                            print(f"   ✅ Row structure valid: {has_row_structure}")
                        else:
                            print(f"   ⚠️  No rows in preview")
                    else:
                        success = False
                        print(f"   ❌ Missing keys: {[k for k in expected_keys if k not in data]}")
                        
                self.log_test("CSV Preview - File Upload", success, f"Status: {response.status_code}")
                return success
                
        except FileNotFoundError:
            self.log_test("CSV Preview - File Upload", False, "test-import.csv file not found")
            return False
        except Exception as e:
            self.log_test("CSV Preview - File Upload", False, str(e))
            return False

    def test_csv_preview_with_errors(self):
        """Test CSV preview endpoint with validation errors"""
        print("\n🔍 Testing CSV Preview - Validation Errors...")
        
        try:
            with open('/app/test-errors.csv', 'rb') as f:
                files = {'file': ('test-errors.csv', f, 'text/csv')}
                response = requests.post(f"{self.api_url}/import/preview", files=files)
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    print(f"   📊 Preview Results: Total: {data['total_rows']}, Errors: {data['error_count']}")
                    
                    # Should have errors for validation failures
                    success = data['error_count'] > 0
                    
                    # Check that error rows have proper status
                    error_rows = [row for row in data['rows'] if row['status'] == 'error']
                    print(f"   🚨 Found {len(error_rows)} error rows")
                    
                    if error_rows:
                        print(f"   📝 Sample error: {error_rows[0]['message']}")
                        
                self.log_test("CSV Preview - Validation Errors", success, f"Status: {response.status_code}, Errors: {data.get('error_count', 0) if success else 0}")
                return success
                
        except FileNotFoundError:
            self.log_test("CSV Preview - Validation Errors", False, "test-errors.csv file not found")
            return False
        except Exception as e:
            self.log_test("CSV Preview - Validation Errors", False, str(e))
            return False

    def test_csv_preview_invalid_input(self):
        """Test CSV preview endpoint with invalid inputs"""
        print("\n🔍 Testing CSV Preview - Invalid Inputs...")
        
        try:
            # Test with no file and no URL
            response = requests.post(f"{self.api_url}/import/preview")
            success1 = response.status_code == 400
            self.log_test("CSV Preview - No Input", success1, f"Status: {response.status_code}")
            
            # Test with non-CSV file
            files = {'file': ('test.txt', b'not a csv file', 'text/plain')}
            response = requests.post(f"{self.api_url}/import/preview", files=files)
            success2 = response.status_code == 400
            self.log_test("CSV Preview - Invalid File Type", success2, f"Status: {response.status_code}")
            
            return success1 and success2
            
        except Exception as e:
            self.log_test("CSV Preview - Invalid Inputs", False, str(e))
            return False

    def test_google_sheets_url_conversion(self):
        """Test Google Sheets URL conversion (if available)"""
        print("\n🔍 Testing Google Sheets URL Conversion...")
        
        try:
            # Test with a mock Google Sheets URL (this will likely fail since we don't have a real public sheet)
            test_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
            
            data = {'sheet_url': test_url}
            response = requests.post(f"{self.api_url}/import/preview", data=data)
            
            # We expect this to fail with a specific error about accessing the sheet
            # but the URL conversion logic should work
            if response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get('detail', '')
                
                # Check if it's a URL access error (good) vs URL format error (bad)
                if 'buscar CSV da URL' in error_message or 'Erro ao buscar' in error_message:
                    success = True
                    print(f"   ✅ URL conversion working, failed at fetch stage as expected")
                elif 'URL deve ser um Google Sheets válido' in error_message:
                    success = False
                    print(f"   ❌ URL format validation failed")
                else:
                    success = True  # Other errors are acceptable for this test
                    print(f"   ⚠️  Other error (acceptable): {error_message}")
            else:
                success = response.status_code == 200  # If it somehow works, that's good too
                print(f"   📊 Unexpected success or different error: {response.status_code}")
                
            self.log_test("Google Sheets URL Conversion", success, f"Status: {response.status_code}")
            return success
            
        except Exception as e:
            self.log_test("Google Sheets URL Conversion", False, str(e))
            return False

    def verify_imported_data(self):
        """Verify that imported data appears correctly"""
        print("\n🔍 Verifying Imported Data...")
        
        try:
            # Check if imported templates exist
            test_slugs = ['chatbot-vendas-ia', 'automacao-email-marketing']
            success_count = 0
            
            for slug in test_slugs:
                try:
                    response = requests.get(f"{self.api_url}/templates/slug/{slug}")
                    if response.status_code == 200:
                        template = response.json()
                        
                        # Verify new fields are present
                        new_fields = ['slug', 'author_email', 'tutorial_url', 'external_id', 'categories', 'tools']
                        has_new_fields = all(field in template for field in new_fields)
                        
                        # Verify categories and tools are arrays
                        categories_valid = isinstance(template.get('categories', []), list)
                        tools_valid = isinstance(template.get('tools', []), list)
                        
                        success = has_new_fields and categories_valid and tools_valid
                        self.log_test(f"Verify imported template ({slug})", success, 
                                    f"New fields: {has_new_fields}, Categories array: {categories_valid}, Tools array: {tools_valid}")
                        
                        if success:
                            success_count += 1
                            print(f"   📋 Template '{template['title']}' has {len(template['categories'])} categories and {len(template['tools'])} tools")
                    else:
                        self.log_test(f"Verify imported template ({slug})", False, f"Template not found (Status: {response.status_code})")
                        
                except Exception as e:
                    self.log_test(f"Verify imported template ({slug})", False, str(e))
            
            return success_count > 0
                    
        except Exception as e:
            self.log_test("Verify Imported Data", False, str(e))
            return False

def main():
    print("🚀 Starting FlowLib API Tests - Including CSV Import Features")
    print("=" * 60)
    
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
        tester.test_invalid_template_id,
        tester.test_template_by_slug,
        tester.test_csv_preview_with_file,
        tester.test_csv_preview_with_errors,
        tester.test_csv_preview_invalid_input,
        tester.test_google_sheets_url_conversion,
        tester.test_csv_import_basic,
        tester.test_csv_import_update_delete,
        tester.test_csv_import_validation_errors,
        tester.test_csv_import_invalid_file,
        tester.verify_imported_data
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.errors.append(f"{test.__name__}: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.errors:
        print(f"\n🚨 Failed Tests:")
        for error in tester.errors:
            print(f"   • {error}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
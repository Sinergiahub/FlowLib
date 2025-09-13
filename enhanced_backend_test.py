import requests
import sys
import json
from datetime import datetime

class EnhancedFlowLibAPITester:
    def __init__(self, base_url="https://flowlib.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
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

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:100]}...")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_enhanced_templates_endpoint(self):
        """Test the enhanced templates endpoint with pagination"""
        print("\n🔧 TESTING ENHANCED TEMPLATES ENDPOINT")
        print("=" * 50)
        
        success, response = self.run_test(
            "Enhanced Templates Endpoint - Basic",
            "GET",
            "templates",
            200,
            params={"page": 1, "page_size": 12}
        )
        
        if success:
            # Verify response structure
            required_keys = ['items', 'total', 'page', 'page_size', 'total_pages', 'facets']
            missing_keys = [key for key in required_keys if key not in response]
            
            if missing_keys:
                self.log_test("Enhanced Response Structure", False, f"Missing keys: {missing_keys}")
                return False
            else:
                self.log_test("Enhanced Response Structure", True)
                print(f"   📊 Total templates: {response['total']}")
                print(f"   📄 Page: {response['page']}/{response['total_pages']}")
                print(f"   📦 Items in response: {len(response['items'])}")
                
                # Verify facets structure
                facets = response['facets']
                facet_keys = ['platforms', 'categories', 'tools']
                facets_valid = all(key in facets and isinstance(facets[key], list) for key in facet_keys)
                
                self.log_test("Facets Structure", facets_valid)
                if facets_valid:
                    print(f"   🏷️  Platforms: {len(facets['platforms'])} ({', '.join(facets['platforms'][:3])}...)")
                    print(f"   📂 Categories: {len(facets['categories'])} ({', '.join(facets['categories'][:3])}...)")
                    print(f"   🔧 Tools: {len(facets['tools'])} ({', '.join(facets['tools'][:3])}...)")
                
                return True
        
        self.log_test("Enhanced Templates Endpoint", success)
        return success

    def test_pagination_functionality(self):
        """Test pagination with different page sizes"""
        print("\n📄 TESTING PAGINATION")
        print("=" * 30)
        
        all_passed = True
        
        # Test different page sizes
        page_sizes = [6, 12, 24]
        for page_size in page_sizes:
            success, response = self.run_test(
                f"Pagination - Page Size {page_size}",
                "GET",
                "templates",
                200,
                params={"page": 1, "page_size": page_size}
            )
            
            if success:
                actual_items = len(response.get('items', []))
                expected_items = min(page_size, response.get('total', 0))
                items_correct = actual_items <= page_size
                
                self.log_test(f"Page Size {page_size} - Items Count", items_correct, 
                            f"Expected ≤{page_size}, got {actual_items}")
                all_passed = all_passed and items_correct
            else:
                all_passed = False
        
        # Test page 2 if there are enough templates
        success, response = self.run_test(
            "Pagination - Page 2",
            "GET",
            "templates",
            200,
            params={"page": 2, "page_size": 6}
        )
        
        if success:
            page_2_valid = response.get('page') == 2
            self.log_test("Page 2 Navigation", page_2_valid)
            all_passed = all_passed and page_2_valid
        else:
            all_passed = False
        
        return all_passed

    def test_search_functionality(self):
        """Test search functionality with real database data"""
        print("\n🔍 TESTING SEARCH FUNCTIONALITY")
        print("=" * 35)
        
        search_terms = ["SEO", "IA", "TikTok", "automação"]
        all_passed = True
        
        for term in search_terms:
            success, response = self.run_test(
                f"Search - '{term}'",
                "GET",
                "templates",
                200,
                params={"search": term, "page": 1, "page_size": 12}
            )
            
            if success:
                results_count = len(response.get('items', []))
                total_results = response.get('total', 0)
                
                print(f"   📊 Found {total_results} total results, showing {results_count}")
                
                # Verify search results contain the search term (case insensitive)
                if results_count > 0:
                    first_result = response['items'][0]
                    title = first_result.get('title', '').lower()
                    description = first_result.get('description', '').lower()
                    search_term_found = term.lower() in title or term.lower() in description
                    
                    self.log_test(f"Search Relevance - '{term}'", search_term_found,
                                f"Term found in title/description: {search_term_found}")
                    all_passed = all_passed and search_term_found
                else:
                    print(f"   ℹ️  No results for '{term}' - this may be expected")
            else:
                all_passed = False
        
        return all_passed

    def test_filtering_functionality(self):
        """Test filtering by platform, category, and tool"""
        print("\n🔧 TESTING FILTERING FUNCTIONALITY")
        print("=" * 40)
        
        all_passed = True
        
        # Test platform filtering
        platforms = ["n8n", "Make", "Zapier"]
        for platform in platforms:
            success, response = self.run_test(
                f"Filter by Platform - {platform}",
                "GET",
                "templates",
                200,
                params={"platform": platform, "page": 1, "page_size": 12}
            )
            
            if success:
                items = response.get('items', [])
                if items:
                    # Verify all results match the platform filter
                    platform_match = all(item.get('platform') == platform for item in items)
                    self.log_test(f"Platform Filter Accuracy - {platform}", platform_match)
                    all_passed = all_passed and platform_match
                    print(f"   📊 Found {len(items)} templates for {platform}")
                else:
                    print(f"   ℹ️  No templates found for platform {platform}")
            else:
                all_passed = False
        
        # Test category filtering
        categories = ["marketing", "produtividade", "redes-sociais"]
        for category in categories:
            success, response = self.run_test(
                f"Filter by Category - {category}",
                "GET",
                "templates",
                200,
                params={"category": category, "page": 1, "page_size": 12}
            )
            
            if success:
                items = response.get('items', [])
                if items:
                    # Verify all results contain the category
                    category_match = all(category in item.get('categories', []) for item in items)
                    self.log_test(f"Category Filter Accuracy - {category}", category_match)
                    all_passed = all_passed and category_match
                    print(f"   📊 Found {len(items)} templates for category {category}")
                else:
                    print(f"   ℹ️  No templates found for category {category}")
            else:
                all_passed = False
        
        # Test tool filtering
        tools = ["openai", "google-sheets", "zapier", "n8n"]
        for tool in tools:
            success, response = self.run_test(
                f"Filter by Tool - {tool}",
                "GET",
                "templates",
                200,
                params={"tool": tool, "page": 1, "page_size": 12}
            )
            
            if success:
                items = response.get('items', [])
                if items:
                    # Verify all results contain the tool
                    tool_match = all(tool in item.get('tools', []) for item in items)
                    self.log_test(f"Tool Filter Accuracy - {tool}", tool_match)
                    all_passed = all_passed and tool_match
                    print(f"   📊 Found {len(items)} templates for tool {tool}")
                else:
                    print(f"   ℹ️  No templates found for tool {tool}")
            else:
                all_passed = False
        
        return all_passed

    def test_combined_filters(self):
        """Test combining multiple filters"""
        print("\n🔗 TESTING COMBINED FILTERS")
        print("=" * 30)
        
        success, response = self.run_test(
            "Combined Filters - SEO + Marketing",
            "GET",
            "templates",
            200,
            params={
                "search": "SEO",
                "category": "marketing",
                "page": 1,
                "page_size": 12
            }
        )
        
        if success:
            items = response.get('items', [])
            if items:
                # Verify results match both search and category
                search_match = any("seo" in item.get('title', '').lower() or 
                                 "seo" in item.get('description', '').lower() for item in items)
                category_match = all("marketing" in item.get('categories', []) for item in items)
                
                combined_success = search_match and category_match
                self.log_test("Combined Filter Accuracy", combined_success)
                print(f"   📊 Found {len(items)} templates matching both criteria")
                return combined_success
            else:
                print("   ℹ️  No results for combined filter - may be expected")
                return True
        
        return False

    def test_legacy_endpoint_compatibility(self):
        """Test backward compatibility with legacy endpoint"""
        print("\n🔄 TESTING LEGACY ENDPOINT")
        print("=" * 30)
        
        success, response = self.run_test(
            "Legacy Templates Endpoint",
            "GET",
            "templates/legacy",
            200,
            params={"limit": 10}
        )
        
        if success:
            # Should return a list of templates (not paginated response)
            is_list = isinstance(response, list)
            self.log_test("Legacy Response Format", is_list, f"Expected list, got {type(response)}")
            
            if is_list and response:
                # Verify template structure
                template = response[0]
                required_fields = ['id', 'title', 'platform', 'categories', 'tools']
                has_required_fields = all(field in template for field in required_fields)
                self.log_test("Legacy Template Structure", has_required_fields)
                
                print(f"   📊 Legacy endpoint returned {len(response)} templates")
                return is_list and has_required_fields
            
            return is_list
        
        return False

    def test_facets_data_accuracy(self):
        """Test that facets contain real database data"""
        print("\n🏷️  TESTING FACETS DATA ACCURACY")
        print("=" * 35)
        
        success, response = self.run_test(
            "Facets Data Retrieval",
            "GET",
            "templates",
            200,
            params={"page": 1, "page_size": 50}  # Get more templates to verify facets
        )
        
        if success:
            facets = response.get('facets', {})
            items = response.get('items', [])
            
            if items:
                # Extract actual platforms, categories, and tools from templates
                actual_platforms = set(item.get('platform') for item in items if item.get('platform'))
                actual_categories = set()
                actual_tools = set()
                
                for item in items:
                    actual_categories.update(item.get('categories', []))
                    actual_tools.update(item.get('tools', []))
                
                # Verify facets contain data from actual templates
                facet_platforms = set(facets.get('platforms', []))
                facet_categories = set(facets.get('categories', []))
                facet_tools = set(facets.get('tools', []))
                
                platforms_accurate = actual_platforms.issubset(facet_platforms)
                categories_accurate = actual_categories.issubset(facet_categories)
                tools_accurate = actual_tools.issubset(facet_tools)
                
                self.log_test("Platforms Facets Accuracy", platforms_accurate)
                self.log_test("Categories Facets Accuracy", categories_accurate)
                self.log_test("Tools Facets Accuracy", tools_accurate)
                
                print(f"   🏷️  Actual platforms: {sorted(actual_platforms)}")
                print(f"   🏷️  Facet platforms: {sorted(facet_platforms)}")
                
                return platforms_accurate and categories_accurate and tools_accurate
            else:
                print("   ℹ️  No templates found to verify facets against")
                return True
        
        return False

    def test_database_content_verification(self):
        """Verify database contains expected imported data"""
        print("\n📊 TESTING DATABASE CONTENT")
        print("=" * 30)
        
        success, response = self.run_test(
            "Database Content Check",
            "GET",
            "templates",
            200,
            params={"page": 1, "page_size": 50}
        )
        
        if success:
            total_templates = response.get('total', 0)
            items = response.get('items', [])
            
            print(f"   📊 Total templates in database: {total_templates}")
            
            # Look for specific templates mentioned in the review request
            expected_templates = [
                "100% Automação SEO",
                "Assistente Virtual para TikTok"
            ]
            
            found_templates = []
            high_download_templates = []
            
            for item in items:
                title = item.get('title', '')
                downloads = item.get('downloads_count', 0)
                
                # Check for expected templates
                for expected in expected_templates:
                    if expected.lower() in title.lower():
                        found_templates.append(title)
                
                # Check for high download counts (indicating real imported data)
                if downloads > 1000:
                    high_download_templates.append(f"{title} ({downloads:,} downloads)")
            
            expected_found = len(found_templates) > 0
            has_high_downloads = len(high_download_templates) > 0
            
            self.log_test("Expected Templates Found", expected_found, 
                        f"Found: {found_templates}")
            self.log_test("High Download Templates", has_high_downloads,
                        f"Templates with >1000 downloads: {len(high_download_templates)}")
            
            if high_download_templates:
                print("   🔥 High-download templates:")
                for template in high_download_templates[:3]:
                    print(f"      • {template}")
            
            # Check if we have the expected 9 templates mentioned in review
            expected_count = total_templates >= 9
            self.log_test("Expected Template Count (≥9)", expected_count,
                        f"Expected ≥9, found {total_templates}")
            
            return expected_found and has_high_downloads and expected_count
        
        return False

    def test_template_details_structure(self):
        """Test individual template details have correct structure"""
        print("\n📋 TESTING TEMPLATE DETAILS STRUCTURE")
        print("=" * 40)
        
        # First get a template ID
        success, response = self.run_test(
            "Get Templates for Detail Test",
            "GET",
            "templates",
            200,
            params={"page": 1, "page_size": 1}
        )
        
        if success and response.get('items'):
            template_id = response['items'][0].get('id')
            
            if template_id:
                success, template = self.run_test(
                    f"Template Details - {template_id[:8]}...",
                    "GET",
                    f"templates/{template_id}",
                    200
                )
                
                if success:
                    # Verify enhanced template structure
                    required_fields = [
                        'id', 'slug', 'title', 'description', 'platform',
                        'author_name', 'categories', 'tools', 'downloads_count',
                        'rating_avg', 'status', 'created_at', 'updated_at'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in template]
                    structure_valid = len(missing_fields) == 0
                    
                    self.log_test("Template Structure Complete", structure_valid,
                                f"Missing fields: {missing_fields}")
                    
                    # Verify arrays are properly formatted
                    categories_valid = isinstance(template.get('categories', []), list)
                    tools_valid = isinstance(template.get('tools', []), list)
                    
                    self.log_test("Categories Array Format", categories_valid)
                    self.log_test("Tools Array Format", tools_valid)
                    
                    # Verify numeric fields
                    downloads_valid = isinstance(template.get('downloads_count', 0), int)
                    rating_valid = template.get('rating_avg') is None or isinstance(template.get('rating_avg'), (int, float))
                    
                    self.log_test("Downloads Count Format", downloads_valid)
                    self.log_test("Rating Format", rating_valid)
                    
                    print(f"   📋 Template: {template.get('title', 'N/A')}")
                    print(f"   🏷️  Categories: {template.get('categories', [])}")
                    print(f"   🔧 Tools: {template.get('tools', [])}")
                    print(f"   📊 Downloads: {template.get('downloads_count', 0):,}")
                    
                    return structure_valid and categories_valid and tools_valid and downloads_valid and rating_valid
        
        return False

def main():
    print("🚀 Starting Enhanced FlowLib API Tests - Database Integration")
    print("=" * 65)
    
    tester = EnhancedFlowLibAPITester()
    
    # Run enhanced tests focusing on new features
    tests = [
        tester.test_enhanced_templates_endpoint,
        tester.test_pagination_functionality,
        tester.test_search_functionality,
        tester.test_filtering_functionality,
        tester.test_combined_filters,
        tester.test_legacy_endpoint_compatibility,
        tester.test_facets_data_accuracy,
        tester.test_database_content_verification,
        tester.test_template_details_structure
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.errors.append(f"{test.__name__}: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 65)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.errors:
        print(f"\n🚨 Failed Tests:")
        for error in tester.errors:
            print(f"   • {error}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All enhanced API tests passed! Database integration is working correctly.")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
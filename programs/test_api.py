"""
Test script for CPE API endpoints.

This script tests the Flask API endpoints for CPE data retrieval and searching.
Run this after:
1. Creating the database: python database.py
2. Parsing XML and populating data: python parser.py
3. Starting the Flask app: python app.py (in another terminal)
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_health():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/api/health")
    print_response("Health Check", response)
    assert response.status_code == 200

def test_get_cpes_default():
    """Test getting CPEs with default pagination (page=1, limit=10)."""
    response = requests.get(f"{BASE_URL}/api/cpes")
    print_response("Get CPEs (Default Pagination)", response)
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert "data" in data
    assert data["page"] == 1
    assert data["limit"] == 10

def test_get_cpes_custom_pagination():
    """Test getting CPEs with custom pagination."""
    response = requests.get(f"{BASE_URL}/api/cpes?page=2&limit=20")
    print_response("Get CPEs (Custom Pagination - page=2, limit=20)", response)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 20

def test_get_cpes_invalid_page():
    """Test getting CPEs with invalid page number."""
    response = requests.get(f"{BASE_URL}/api/cpes?page=0")
    print_response("Get CPEs (Invalid Page=0)", response)
    assert response.status_code == 400

def test_get_cpes_invalid_limit():
    """Test getting CPEs with invalid limit."""
    response = requests.get(f"{BASE_URL}/api/cpes?limit=200")
    print_response("Get CPEs (Invalid Limit=200)", response)
    assert response.status_code == 400

def test_search_by_title():
    """Test searching CPEs by title."""
    response = requests.get(f"{BASE_URL}/api/cpes/search?cpe_title=example")
    print_response("Search CPEs by Title (cpe_title=example)", response)
    assert response.status_code == 200

def test_search_by_cpe_22_uri():
    """Test searching CPEs by CPE 2.2 URI."""
    response = requests.get(f"{BASE_URL}/api/cpes/search?cpe_22_uri=cpe:/a:")
    print_response("Search CPEs by CPE 2.2 URI", response)
    assert response.status_code == 200

def test_search_by_cpe_23_uri():
    """Test searching CPEs by CPE 2.3 URI."""
    response = requests.get(f"{BASE_URL}/api/cpes/search?cpe_23_uri=cpe:2.3:a:")
    print_response("Search CPEs by CPE 2.3 URI", response)
    assert response.status_code == 200

def test_search_by_deprecation_date():
    """Test searching CPEs by deprecation date."""
    response = requests.get(f"{BASE_URL}/api/cpes/search?deprecation_date=2023-01-01")
    print_response("Search CPEs by Deprecation Date (before 2023-01-01)", response)
    assert response.status_code == 200

def test_search_combined():
    """Test searching CPEs with multiple filters."""
    response = requests.get(
        f"{BASE_URL}/api/cpes/search?cpe_title=example&deprecation_date=2024-01-01"
    )
    print_response("Search CPEs (title + deprecation_date)", response)
    assert response.status_code == 200

def test_search_no_params():
    """Test searching with no parameters (should fail)."""
    response = requests.get(f"{BASE_URL}/api/cpes/search")
    print_response("Search CPEs (No Parameters - Should Fail)", response)
    assert response.status_code == 400

def test_response_format():
    """Test that response format matches specification."""
    response = requests.get(f"{BASE_URL}/api/cpes?limit=1")
    assert response.status_code == 200
    data = response.json()
    
    # Check structure
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert "data" in data
    
    if data["data"]:
        cpe = data["data"][0]
        assert "id" in cpe
        assert "cpe_title" in cpe
        assert "cpe_22_uri" in cpe
        assert "cpe_23_uri" in cpe
        assert "reference_links" in cpe
        assert isinstance(cpe["reference_links"], list)
        assert "cpe_22_deprecation_date" in cpe
        assert "cpe_23_deprecation_date" in cpe
    
    print_response("Response Format Validation", response)
    print("✓ Response format is correct!")

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("CPE API TEST SUITE")
    print(f"{'='*60}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        # Test health check
        test_health()
        
        # Test pagination
        test_get_cpes_default()
        test_get_cpes_custom_pagination()
        test_get_cpes_invalid_page()
        test_get_cpes_invalid_limit()
        
        # Test search
        test_search_by_title()
        test_search_by_cpe_22_uri()
        test_search_by_cpe_23_uri()
        test_search_by_deprecation_date()
        test_search_combined()
        test_search_no_params()
        
        # Test response format
        test_response_format()
        
        print(f"\n{'='*60}")
        print("✓ ALL TESTS PASSED!")
        print(f"{'='*60}\n")
        
    except AssertionError as e:
        print(f"\n{'='*60}")
        print(f"✗ TEST FAILED: {e}")
        print(f"{'='*60}\n")
    except requests.exceptions.ConnectionError:
        print(f"\n{'='*60}")
        print("✗ ERROR: Could not connect to Flask API")
        print(f"Make sure the Flask app is running on {BASE_URL}")
        print(f"Run: python app.py")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ ERROR: {e}")
        print(f"{'='*60}\n")

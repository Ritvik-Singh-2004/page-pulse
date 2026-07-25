import pytest
from main import is_valid_url, parse_html_content, app
from fastapi.testclient import TestClient

client = TestClient(app)

# 1. Happy Path Unit Test
def test_parse_html_content_happy_path():
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page Title</title>
        <meta name="description" content="This is a test meta description.">
    </head>
    <body>
        <h1>Main Heading</h1>
        <img src="logo.png" alt="Company Logo">
        <img src="banner.png">
        <p>Hello world, this is a test page containing words.</p>
    </body>
    </html>
    """
    result = parse_html_content(sample_html)
    
    assert result["title"] == "Test Page Title"
    assert result["meta_description"] == "This is a test meta description."
    assert result["h1_count"] == 1
    assert result["missing_alt_images_count"] == 1
    assert result["word_count"] > 0

# 2. Failure Case 1: Unreachable Domain (Our auto-https makes it valid format, but it won't connect)
def test_api_invalid_url_string():
    response = client.get("/api/audit?url=invalid-url-string")
    assert response.status_code == 502
    assert "Failed to connect" in response.json()["detail"]

# 3. Failure Case 2: Unreachable Domain / Connection Error
def test_api_unreachable_domain():
    response = client.get("/api/audit?url=https://nonexistent-domain-123456789.org")
    assert response.status_code == 502
    assert "Failed to connect" in response.json()["detail"]
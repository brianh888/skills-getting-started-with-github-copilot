"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from copy import deepcopy

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def original_activities():
    """Store the original activities state for restoration."""
    return deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities(original_activities):
    """Reset activities to original state before each test.
    
    This fixture is automatically used (autouse=True) to ensure test isolation
    when testing endpoints that mutate the activities data.
    """
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield
    # Clean up after test
    activities.clear()
    activities.update(deepcopy(original_activities))


@pytest.fixture
def sample_emails():
    """Provide a set of test email addresses."""
    return {
        "alice": "alice@mergington.edu",
        "bob": "bob@mergington.edu",
        "charlie": "charlie@mergington.edu",
        "diana": "diana@mergington.edu",
    }

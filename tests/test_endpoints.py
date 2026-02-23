"""
Tests for basic API endpoints (GET /activities and GET /).
"""

import pytest


def test_get_root_redirect(client):
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    # Should have 9 activities
    assert len(activities) == 9
    
    # Check some known activities exist
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Basketball Team" in activities


def test_activities_structure(client):
    """Test that activities have the correct structure."""
    response = client.get("/activities")
    activities = response.json()
    
    # Check Chess Club structure
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_activities_have_participant_lists(client):
    """Test that activities include participant information."""
    response = client.get("/activities")
    activities = response.json()
    
    # Chess Club should have existing participants
    chess_club = activities["Chess Club"]
    assert len(chess_club["participants"]) > 0
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]
    
    # Basketball Team should have no participants initially
    basketball = activities["Basketball Team"]
    assert len(basketball["participants"]) == 0


def test_activities_availability_calculation(client):
    """Test that we can calculate available spots correctly."""
    response = client.get("/activities")
    activities = response.json()
    
    chess_club = activities["Chess Club"]
    max_spots = chess_club["max_participants"]
    current_count = len(chess_club["participants"])
    available_spots = max_spots - current_count
    
    assert available_spots > 0
    assert available_spots <= max_spots

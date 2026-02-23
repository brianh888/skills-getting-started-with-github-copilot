"""
Tests for student signup functionality (POST /activities/{activity_name}/signup).
"""

import pytest


def test_signup_new_student(client, sample_emails):
    """Test that a new student can successfully sign up for an activity."""
    email = sample_emails["alice"]
    activity = "Basketball Team"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the student was added to the activity
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]


def test_signup_multiple_students(client, sample_emails):
    """Test that multiple students can sign up for the same activity."""
    activity = "Tennis Club"
    
    # Sign up first student
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": sample_emails["alice"]}
    )
    assert response1.status_code == 200
    
    # Sign up second student
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": sample_emails["bob"]}
    )
    assert response2.status_code == 200
    
    # Verify both are in the activity
    activities_response = client.get("/activities")
    activities = activities_response.json()
    participants = activities[activity]["participants"]
    assert sample_emails["alice"] in participants
    assert sample_emails["bob"] in participants
    assert len(participants) == 2


def test_signup_duplicate_rejected(client, sample_emails):
    """Test that duplicate signup is rejected with a 400 error."""
    email = sample_emails["alice"]
    activity = "Art Studio"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(client, sample_emails):
    """Test that signup to nonexistent activity returns 404."""
    response = client.post(
        f"/activities/Nonexistent Club/signup",
        params={"email": sample_emails["alice"]}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_response_message_format(client, sample_emails):
    """Test that signup response has proper message format."""
    email = sample_emails["alice"]
    activity = "Science Club"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity}"


def test_signup_activities_list_updates(client, sample_emails):
    """Test that activities list reflects signup immediately."""
    email = sample_emails["alice"]
    activity = "Theater Club"
    
    # Get initial state
    response1 = client.get("/activities")
    activities1 = response1.json()
    initial_count = len(activities1[activity]["participants"])
    
    # Sign up
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Get updated state
    response2 = client.get("/activities")
    activities2 = response2.json()
    updated_count = len(activities2[activity]["participants"])
    
    assert updated_count == initial_count + 1
    assert email in activities2[activity]["participants"]

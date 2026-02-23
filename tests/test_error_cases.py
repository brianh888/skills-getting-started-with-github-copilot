"""
Tests for error cases and edge cases across all endpoints.
"""

import pytest


def test_signup_with_special_characters_in_email(client):
    """Test that email addresses with special characters are handled."""
    email = "alice+testing@mergington.edu"
    activity = "Basketball Team"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_with_spaces_in_email(client):
    """Test email with spaces is handled correctly."""
    email = "alice extra@mergington.edu"
    activity = "Tennis Club"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Should still work - email is valid parameter
    assert response.status_code == 200


def test_activity_name_case_sensitivity(client, sample_emails):
    """Test that activity names are case-sensitive."""
    email = sample_emails["alice"]
    
    # Try with different case
    response = client.post(
        f"/activities/basketball team/signup",
        params={"email": email}
    )
    
    # Should fail because exact name is "Basketball Team"
    assert response.status_code == 404


def test_signup_to_existing_participant_activity(client, sample_emails):
    """Test signup to an activity that already has participants."""
    email = sample_emails["alice"]
    activity = "Chess Club"  # Already has participants
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_preserves_existing_participants(client, sample_emails):
    """Test that signing up a new student preserves existing participants."""
    activity = "Programming Class"
    email = sample_emails["alice"]
    
    # Get original participants
    activities1 = client.get("/activities").json()
    original_participants = activities1[activity]["participants"].copy()
    
    # Sign up new student
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Verify original participants are still there
    activities2 = client.get("/activities").json()
    new_participants = activities2[activity]["participants"]
    
    for original in original_participants:
        assert original in new_participants


def test_error_response_structure(client, sample_emails):
    """Test that error responses have correct structure."""
    # Try duplicate signup
    email = sample_emails["alice"]
    activity = "Art Studio"
    
    client.post(f"/activities/{activity}/signup", params={"email": email})
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)


def test_multiple_signup_errors(client, sample_emails):
    """Test multiple error conditions in sequence."""
    email = sample_emails["alice"]
    
    # Try nonexistent activity
    response1 = client.post(
        f"/activities/Fake Club/signup",
        params={"email": email}
    )
    assert response1.status_code == 404
    
    # Sign up successfully
    response2 = client.post(
        f"/activities/Basketball Team/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Try duplicate
    response3 = client.post(
        f"/activities/Basketball Team/signup",
        params={"email": email}
    )
    assert response3.status_code == 400


def test_unregister_from_empty_activity(client, sample_emails):
    """Test unregister from an activity with no participants."""
    email = sample_emails["alice"]
    activity = "Tennis Club"  # Empty activity
    
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"].lower()


def test_same_email_different_activities(client, sample_emails):
    """Test that same student can sign up for multiple different activities."""
    email = sample_emails["alice"]
    activities_list = ["Basketball Team", "Art Studio", "Science Club"]
    
    # Sign up for multiple activities
    for activity in activities_list:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify signup in all activities
    activities = client.get("/activities").json()
    for activity in activities_list:
        assert email in activities[activity]["participants"]

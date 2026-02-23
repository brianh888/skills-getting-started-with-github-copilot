"""
Tests for student unregistration functionality (DELETE /activities/{activity_name}/signup).
"""

import pytest


def test_unregister_existing_participant(client, sample_emails):
    """Test that a student can successfully unregister from an activity."""
    email = sample_emails["alice"]
    activity = "Basketball Team"
    
    # First, sign up
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Then unregister
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the student was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_activity(client, sample_emails):
    """Test that unregister from nonexistent activity returns 404."""
    response = client.delete(
        f"/activities/Nonexistent Club/signup",
        params={"email": sample_emails["alice"]}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_not_signed_up(client, sample_emails):
    """Test that unregistering non-signed-up student returns 400."""
    email = sample_emails["alice"]
    activity = "Debate Team"
    
    # Try to unregister without being signed up
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()


def test_unregister_from_existing_participants(client):
    """Test unregistering from an activity that has existing participants."""
    activity = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    
    # Verify student is initially signed up
    response1 = client.get("/activities")
    activities1 = response1.json()
    assert email_to_remove in activities1[activity]["participants"]
    initial_count = len(activities1[activity]["participants"])
    
    # Unregister
    response2 = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email_to_remove}
    )
    assert response2.status_code == 200
    
    # Verify student was removed
    response3 = client.get("/activities")
    activities3 = response3.json()
    assert email_to_remove not in activities3[activity]["participants"]
    assert len(activities3[activity]["participants"]) == initial_count - 1


def test_unregister_response_message_format(client, sample_emails):
    """Test that unregister response has proper message format."""
    email = sample_emails["alice"]
    activity = "Art Studio"
    
    # Sign up first
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Then unregister
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity}"


def test_signup_and_unregister_cycle(client, sample_emails):
    """Test complete signup and unregister cycle."""
    email = sample_emails["alice"]
    activity = "Science Club"
    
    # Sign up
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Verify signup
    activities1 = client.get("/activities").json()
    assert email in activities1[activity]["participants"]
    count_after_signup = len(activities1[activity]["participants"])
    
    # Unregister
    response2 = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify unregister
    activities2 = client.get("/activities").json()
    assert email not in activities2[activity]["participants"]
    assert len(activities2[activity]["participants"]) == count_after_signup - 1


def test_unregister_one_student_preserves_others(client, sample_emails):
    """Test that unregistering one student doesn't affect others."""
    activity = "Theater Club"
    alice = sample_emails["alice"]
    bob = sample_emails["bob"]
    
    # Sign up both students
    client.post(f"/activities/{activity}/signup", params={"email": alice})
    client.post(f"/activities/{activity}/signup", params={"email": bob})
    
    # Unregister alice
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": alice}
    )
    assert response.status_code == 200
    
    # Verify alice is removed but bob remains
    activities = client.get("/activities").json()
    assert alice not in activities[activity]["participants"]
    assert bob in activities[activity]["participants"]

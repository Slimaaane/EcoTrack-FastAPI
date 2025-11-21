"""Tests for zones endpoints."""
import pytest


@pytest.mark.crud
class TestZones:
    """Test zones CRUD operations."""
    
    def test_create_zone_as_admin(self, client, admin_token):
        """Test creating a zone as admin."""
        response = client.post(
            "/api/v1/zones",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Paris Centre",
                "postal_code": "75001",
                "description": "Centre de Paris"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Paris Centre"
        assert data["postal_code"] == "75001"
        assert "id" in data
    
    def test_create_zone_as_user(self, client, user_token):
        """Test creating a zone as normal user (should fail)."""
        response = client.post(
            "/api/v1/zones",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Test Zone",
                "postal_code": "75002"
            }
        )
        assert response.status_code == 403
    
    def test_list_zones(self, client, admin_token, sample_zone):
        """Test listing zones."""
        response = client.get(
            "/api/v1/zones",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "has_more" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
    
    def test_get_zone_by_id(self, client, admin_token, sample_zone):
        """Test getting a zone by ID."""
        response = client.get(
            f"/api/v1/zones/{sample_zone.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_zone.id
        assert data["name"] == sample_zone.name
    
    def test_get_zone_not_found(self, client, admin_token):
        """Test getting a nonexistent zone."""
        response = client.get(
            "/api/v1/zones/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
    
    def test_update_zone_as_admin(self, client, admin_token, sample_zone):
        """Test updating a zone as admin - PUT not implemented, skipping."""
        pytest.skip("PUT method not implemented for zones")
    
    def test_delete_zone_as_admin(self, client, admin_token, sample_zone):
        """Test deleting a zone as admin."""
        response = client.delete(
            f"/api/v1/zones/{sample_zone.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(
            f"/api/v1/zones/{sample_zone.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
    
    def test_search_zones_by_postal_code(self, client, admin_token, sample_zone):
        """Test searching zones by postal code."""
        response = client.get(
            f"/api/v1/zones?postal_code={sample_zone.postal_code}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(z["postal_code"] == sample_zone.postal_code for z in data["items"])

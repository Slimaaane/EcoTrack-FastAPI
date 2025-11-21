"""Tests for sources endpoints."""
import pytest


@pytest.mark.crud
class TestSources:
    """Test sources CRUD operations."""
    
    def test_create_source_as_admin(self, client, admin_token):
        """Test creating a source as admin."""
        response = client.post(
            "/api/v1/sources",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Data.gouv.fr",
                "url": "https://data.gouv.fr",
                "format": "CSV",
                "frequency": "daily",
                "description": "French open data portal"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Data.gouv.fr"
        assert data["format"] == "CSV"
        assert "id" in data
    
    def test_create_source_as_user(self, client, user_token):
        """Test creating a source as normal user (should fail)."""
        response = client.post(
            "/api/v1/sources",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Test Source",
                "url": "https://test.com",
                "format": "JSON"
            }
        )
        assert response.status_code == 403
    
    def test_list_sources(self, client, admin_token, sample_source):
        """Test listing sources."""
        response = client.get(
            "/api/v1/sources",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
    
    def test_get_source_by_id(self, client, admin_token, sample_source):
        """Test getting a source by ID."""
        response = client.get(
            f"/api/v1/sources/{sample_source.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_source.id
        assert data["name"] == sample_source.name
    
    def test_update_source(self, client, admin_token, sample_source):
        """Test updating a source - PUT not implemented, skipping."""
        pytest.skip("PUT method not implemented for sources")
    
    def test_delete_source(self, client, admin_token, sample_source):
        """Test deleting a source."""
        response = client.delete(
            f"/api/v1/sources/{sample_source.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(
            f"/api/v1/sources/{sample_source.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
    
    def test_filter_sources_by_format(self, client, admin_token, sample_source):
        """Test filtering sources by format."""
        response = client.get(
            f"/api/v1/sources?format={sample_source.format}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert all(s["format"] == sample_source.format for s in data["items"])

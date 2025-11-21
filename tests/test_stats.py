"""Tests for statistics endpoints."""
import pytest
from datetime import datetime, timedelta


@pytest.mark.integration
class TestStatistics:
    """Test statistics endpoints."""
    
    def test_get_distribution(self, client, admin_token, sample_indicator):
        """Test getting indicator type distribution."""
        response = client.get(
            "/api/v1/stats/distribution",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "distribution" in data
        assert isinstance(data["distribution"], list)
        assert len(data["distribution"]) > 0
    
    def test_get_summary_for_type(self, client, admin_token, sample_indicator):
        """Test getting summary statistics for a specific type."""
        response = client.get(
            f"/api/v1/stats/summary/{sample_indicator.type}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "avg" in data
        assert "min" in data
        assert "max" in data
        assert data["count"] >= 1
    
    def test_get_summary_invalid_type(self, client, admin_token):
        """Test getting summary for invalid type."""
        response = client.get(
            "/api/v1/stats/summary/invalid_type",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
    
    def test_get_stats_by_zone(self, client, admin_token, sample_indicator, sample_zone):
        """Test getting statistics by zone."""
        response = client.get(
            f"/api/v1/stats/zone/{sample_zone.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "statistics" in data
        assert isinstance(data["statistics"], list)
    
    def test_get_trend(self, client, admin_token, sample_indicator):
        """Test getting trend data."""
        response = client.get(
            f"/api/v1/stats/trend/{sample_indicator.type}?days=7",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "trend" in data
        assert isinstance(data["trend"], list)
    
    def test_compare_zones(self, client, admin_token, sample_indicator, sample_zone):
        """Test comparing zones - endpoint not implemented."""
        pytest.skip("Compare endpoint not yet implemented")

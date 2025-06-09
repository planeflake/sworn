import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import status

from app.api.fastapi import fastapi
from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(fastapi)


@pytest.fixture
def sample_theme_id():
    return uuid4()


@pytest.fixture
def sample_tool_tier():
    return ToolTierPydantic(
        entity_id=uuid4(),
        name="Steel Tools",
        theme_id=uuid4(),
        tier_name="Steel",
        tier_level=3,
        effectiveness_multiplier=1.5,
        description="High-quality steel tools",
        required_tech_level=2,
        color_hex="#4682B4"
    )


class TestToolTierRoutes:
    """Test suite for tool tier API routes."""
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    @patch('app.api.routes.tool_tier_routes.ToolTierManager')
    def test_create_tool_tier_success(self, mock_manager, mock_repository_class, mock_db_session, client, sample_theme_id):
        """Test successful tool tier creation."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        created_tier = ToolTierPydantic(
            entity_id=uuid4(),
            name="Steel Tools",
            theme_id=sample_theme_id,
            tier_name="Steel",
            tier_level=3,
            effectiveness_multiplier=1.5
        )
        
        mock_manager.create_tool_tier.return_value = created_tier
        mock_repository.create.return_value = created_tier
        
        # Test data
        tier_data = {
            "name": "Steel Tools",
            "theme_id": str(sample_theme_id),
            "tier_name": "Steel",
            "tier_level": 3,
            "effectiveness_multiplier": 1.5,
            "description": "High-quality steel tools",
            "required_tech_level": 2,
            "color_hex": "#4682B4"
        }
        
        # Make request
        response = client.post("/api/v1/tool-tiers/", json=tier_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Steel Tools"
        assert data["tier_name"] == "Steel"
        assert data["tier_level"] == 3
        assert data["effectiveness_multiplier"] == 1.5
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_get_tool_tiers_by_theme(self, mock_repository_class, mock_db_session, client, sample_theme_id):
        """Test getting tool tiers filtered by theme."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        tiers = [
            ToolTierPydantic(
                entity_id=uuid4(),
                name="Basic Tools",
                theme_id=sample_theme_id,
                tier_name="Basic",
                tier_level=1,
                effectiveness_multiplier=1.0
            ),
            ToolTierPydantic(
                entity_id=uuid4(),
                name="Steel Tools",
                theme_id=sample_theme_id,
                tier_name="Steel",
                tier_level=3,
                effectiveness_multiplier=1.5
            )
        ]
        
        mock_repository.get_by_theme.return_value = tiers
        
        # Make request
        response = client.get(f"/api/v1/tool-tiers/?theme_id={sample_theme_id}")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["tier_name"] == "Basic"
        assert data[1]["tier_name"] == "Steel"
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_get_theme_progression(self, mock_repository_class, mock_db_session, client, sample_theme_id):
        """Test getting complete theme progression."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        progression_tiers = [
            ToolTierPydantic(
                entity_id=uuid4(),
                name="Basic Tools",
                theme_id=sample_theme_id,
                tier_name="Basic",
                tier_level=1,
                effectiveness_multiplier=1.0
            ),
            ToolTierPydantic(
                entity_id=uuid4(),
                name="Iron Tools",
                theme_id=sample_theme_id,
                tier_name="Iron",
                tier_level=2,
                effectiveness_multiplier=1.2
            ),
            ToolTierPydantic(
                entity_id=uuid4(),
                name="Steel Tools",
                theme_id=sample_theme_id,
                tier_name="Steel",
                tier_level=3,
                effectiveness_multiplier=1.5
            )
        ]
        
        mock_repository.get_progression_for_theme.return_value = progression_tiers
        
        # Make request
        response = client.get(f"/api/v1/tool-tiers/progressions/{sample_theme_id}")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["theme_id"] == str(sample_theme_id)
        assert data["total_tiers"] == 3
        assert len(data["tiers"]) == 3
        assert data["tiers"][0]["tier_level"] == 1
        assert data["tiers"][1]["tier_level"] == 2
        assert data["tiers"][2]["tier_level"] == 3
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_get_theme_progression_not_found(self, mock_repository_class, mock_db_session, client):
        """Test getting progression when no tiers exist."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        mock_repository.get_progression_for_theme.return_value = []
        
        # Make request
        nonexistent_theme_id = uuid4()
        response = client.get(f"/api/v1/tool-tiers/progressions/{nonexistent_theme_id}")
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No tool tiers found for theme" in response.json()["detail"]
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    @patch('app.api.routes.tool_tier_routes.ToolTierManager')
    def test_create_theme_progression(self, mock_manager, mock_repository_class, mock_db_session, client, sample_theme_id):
        """Test creating a complete theme progression."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        # Mock manager to return tier entities
        tier_entities = [
            ToolTierPydantic(
                entity_id=uuid4(),
                name="Basic Tools",
                theme_id=sample_theme_id,
                tier_name="Basic",
                tier_level=1,
                effectiveness_multiplier=1.0
            ),
            ToolTierPydantic(
                entity_id=uuid4(),
                name="Magical Tools",
                theme_id=sample_theme_id,
                tier_name="Magical",
                tier_level=5,
                effectiveness_multiplier=3.0
            )
        ]
        
        mock_manager.create_theme_progression.return_value = tier_entities
        mock_repository.create.side_effect = tier_entities  # Return same entities when created
        
        # Test data
        progression_data = {
            "theme_id": str(sample_theme_id),
            "theme_name": "fantasy"
        }
        
        # Make request
        response = client.post("/api/v1/tool-tiers/progressions", json=progression_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["theme_id"] == str(sample_theme_id)
        assert data["theme_name"] == "fantasy"
        assert data["total_tiers"] == 2
        assert len(data["tiers"]) == 2
        assert data["tiers"][0]["tier_name"] == "Basic"
        assert data["tiers"][1]["tier_name"] == "Magical"
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_get_tool_tier_by_id(self, mock_repository_class, mock_db_session, client, sample_tool_tier):
        """Test getting a specific tool tier by ID."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        mock_repository.get_by_id.return_value = sample_tool_tier
        
        # Make request
        tier_id = sample_tool_tier.entity_id
        response = client.get(f"/api/v1/tool-tiers/{tier_id}")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["entity_id"] == str(tier_id)
        assert data["name"] == "Steel Tools"
        assert data["tier_level"] == 3
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_get_tool_tier_not_found(self, mock_repository_class, mock_db_session, client):
        """Test getting a tool tier that doesn't exist."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        mock_repository.get_by_id.return_value = None
        
        # Make request
        nonexistent_id = uuid4()
        response = client.get(f"/api/v1/tool-tiers/{nonexistent_id}")
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Tool tier not found" in response.json()["detail"]
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_update_tool_tier(self, mock_repository_class, mock_db_session, client, sample_tool_tier):
        """Test updating a tool tier."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        mock_repository.get_by_id.return_value = sample_tool_tier
        
        # Create updated tier
        updated_tier = ToolTierPydantic(
            entity_id=sample_tool_tier.entity_id,
            name="Enhanced Steel Tools",
            theme_id=sample_tool_tier.theme_id,
            tier_name="Steel",
            tier_level=3,
            effectiveness_multiplier=1.8,  # Increased
            description="Enhanced steel tools with better efficiency"
        )
        mock_repository.update.return_value = updated_tier
        
        # Update data
        update_data = {
            "name": "Enhanced Steel Tools",
            "effectiveness_multiplier": 1.8,
            "description": "Enhanced steel tools with better efficiency"
        }
        
        # Make request
        tier_id = sample_tool_tier.entity_id
        response = client.patch(f"/api/v1/tool-tiers/{tier_id}", json=update_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Enhanced Steel Tools"
        assert data["effectiveness_multiplier"] == 1.8
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_delete_tool_tier(self, mock_repository_class, mock_db_session, client):
        """Test deleting a tool tier."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        mock_repository.delete.return_value = True
        
        # Make request
        tier_id = uuid4()
        response = client.delete(f"/api/v1/tool-tiers/{tier_id}")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert "Tool tier deleted successfully" in response.json()["message"]
    
    @patch('app.api.routes.tool_tier_routes.get_async_db')
    @patch('app.api.routes.tool_tier_routes.ToolTierRepository')
    def test_delete_tool_tier_not_found(self, mock_repository_class, mock_db_session, client):
        """Test deleting a tool tier that doesn't exist."""
        # Setup mocks
        mock_db_session.return_value = AsyncMock()
        mock_repository = AsyncMock()
        mock_repository_class.return_value = mock_repository
        
        mock_repository.delete.return_value = False
        
        # Make request
        tier_id = uuid4()
        response = client.delete(f"/api/v1/tool-tiers/{tier_id}")
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Tool tier not found" in response.json()["detail"]
    
    def test_create_tool_tier_validation_error(self, client):
        """Test tool tier creation with invalid data."""
        # Invalid data - missing required fields
        invalid_data = {
            "name": "Test",
            "tier_level": -1,  # Invalid tier level
            "effectiveness_multiplier": -0.5  # Invalid multiplier
        }
        
        # Make request
        response = client.post("/api/v1/tool-tiers/", json=invalid_data)
        
        # Verify validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_tool_tier_invalid_color_hex(self, client, sample_theme_id):
        """Test tool tier creation with invalid color hex."""
        # Invalid color hex format
        invalid_data = {
            "name": "Test Tools",
            "theme_id": str(sample_theme_id),
            "tier_name": "Test",
            "tier_level": 1,
            "color_hex": "invalid-color"  # Invalid format
        }
        
        # Make request
        response = client.post("/api/v1/tool-tiers/", json=invalid_data)
        
        # Verify validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
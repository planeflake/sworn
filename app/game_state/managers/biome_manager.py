# --- START OF FILE app/game_state/managers/biome_manager.py ---
from typing import Optional, Dict, Any, List
import uuid

from app.game_state.entities.geography.biome_pydantic import BiomeEntityPydantic
from app.game_state.managers.base_manager import BaseManager

class BiomeManager(BaseManager):
    """
    Manager class for biome-specific domain logic.
    Provides factory methods and business operations for Biome entities.
    """
    
    @staticmethod
    def create_transient_biome(
        biome_id: str,
        name: str,
        display_name: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        base_movement_modifier: float = 1.0,
        danger_level_base: int = 1,
        resource_types: Optional[Dict[str, float]] = None,
        color_hex: Optional[str] = None,
        icon_path: Optional[str] = None
    ) -> BiomeEntityPydantic:
        """
        Creates a new BiomeEntity instance without persisting it.
        
        Args:
            biome_id: String identifier for the biome (e.g., "forest")
            name: The name of the biome
            display_name: User-friendly display name, defaults to name if not provided
            entity_id: Optional UUID for the entity
            description: Optional description of the biome
            base_movement_modifier: Movement speed multiplier (1.0 = normal)
            danger_level_base: Base danger level (1-5)
            resource_types: Dictionary of resource types and their abundance multipliers
            color_hex: Hexadecimal color code for map display
            icon_path: Path to biome icon image
            
        Returns:
            A new BiomeEntityPydantic instance
        """
        # Use display_name same as name if not provided
        if display_name is None:
            display_name = name
            
        # Initialize empty resource types dict if None
        if resource_types is None:
            resource_types = {}
            
        # Generate UUID if not provided
        if entity_id is None:
            entity_id = uuid.uuid4()
            
        # Create entity
        return BiomeEntityPydantic(
            entity_id=entity_id,
            biome_id=biome_id,
            name=name,
            display_name=display_name,
            description=description,
            base_movement_modifier=base_movement_modifier,
            danger_level_base=danger_level_base,
            resource_types=resource_types,
            color_hex=color_hex,
            icon_path=icon_path
        )
    
    @staticmethod
    def calculate_resource_abundance(
        biome: BiomeEntityPydantic,
        resource_type: str,
        base_quantity: float = 1.0,
        world_modifiers: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculates the actual abundance/availability of a resource in this biome.
        
        Args:
            biome: The BiomeEntity to calculate for
            resource_type: The type of resource to check
            base_quantity: Base quantity before modifiers
            world_modifiers: Additional modifiers from world state
            
        Returns:
            The modified resource quantity
        """
        # Get biome's modifier for this resource type
        biome_modifier = biome.resource_types.get(resource_type, 1.0)
        
        # Apply biome modifier
        result = base_quantity * biome_modifier
        
        # Apply world modifiers if provided
        if world_modifiers:
            world_modifier = world_modifiers.get(resource_type, 1.0)
            result *= world_modifier
            
        return result
    
    @staticmethod
    def calculate_travel_time(
        biome: BiomeEntityPydantic,
        distance: float,
        base_speed: float = 1.0,
        traveler_modifiers: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculates travel time through this biome.
        
        Args:
            biome: The BiomeEntity to calculate for
            distance: Distance to travel
            base_speed: Base travel speed
            traveler_modifiers: Additional modifiers from traveler
            
        Returns:
            Time required to travel the distance
        """
        # Start with biome's movement modifier
        effective_speed = base_speed * biome.base_movement_modifier
        
        # Apply traveler modifiers if provided
        if traveler_modifiers:
            # Check for biome-specific modifier
            biome_specific = traveler_modifiers.get(f"biome_{biome.biome_id}", 1.0)
            # Check for general terrain modifier
            general = traveler_modifiers.get("general_terrain", 1.0)
            
            effective_speed *= biome_specific * general
            
        # Calculate time (distance / speed)
        if effective_speed <= 0:
            return float('inf')  # Impassable
            
        return distance / effective_speed
    
    @staticmethod
    def get_danger_level(
        biome: BiomeEntityPydantic,
        time_of_day: Optional[str] = None,
        season: Optional[str] = None
    ) -> int:
        """
        Gets the effective danger level of the biome with modifiers.
        
        Args:
            biome: The BiomeEntity to check
            time_of_day: Optional time of day that might affect danger
            season: Optional season that might affect danger
            
        Returns:
            The effective danger level (1-5)
        """
        # Start with base danger level
        danger = biome.danger_level_base
        
        # Apply time of day modifiers
        if time_of_day == "night":
            danger += 1
        elif time_of_day == "dawn" or time_of_day == "dusk":
            danger += 0
            
        # Apply seasonal modifiers
        if season == "winter" and biome.biome_id in ["mountains", "tundra"]:
            danger += 1
        elif season == "summer" and biome.biome_id == "desert":
            danger += 1
            
        # Cap danger level between 1-5
        return max(1, min(5, danger))

# --- END OF FILE app/game_state/managers/biome_manager.py ---
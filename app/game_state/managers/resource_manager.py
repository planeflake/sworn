# --- START - app/game_state/managers/resource_manager.py ---

import logging
from uuid import UUID
from typing import Optional

# Import Domain Entity and Enums
from app.game_state.entities.resource import ResourceEntity
from app.game_state.enums.shared import RarityEnum, StatusEnum
# No Repository or DB Session imports needed here

class ResourceManager:
    """
    Manager containing domain logic related to Resource Types.
    Operates on ResourceEntity objects.
    """

    @staticmethod
    def create_resource_entity(
        resource_id: UUID, # Resource ID must be provided for types
        name: str,
        description: Optional[str] = None,
        stack_size: int = 100,
        rarity: RarityEnum = RarityEnum.COMMON,
        status: StatusEnum = StatusEnum.ACTIVE,
        theme_id: Optional[UUID] = None,
    ) -> ResourceEntity:
        """
        Creates a new transient (in-memory) ResourceEntity.
        Applies initial validation or default logic if any.

        Args:
            resource_id: The unique ID for this resource type.
            name: The required name for the resource.
            description: Optional description.
            stack_size: Maximum stack size.
            rarity: Rarity level.
            status: Initial status.
            theme_id: Optional theme ID.

        Returns:
            A new ResourceEntity instance.

        Raises:
            ValueError: If validation fails (e.g., invalid name).
        """
        logging.debug(f"Creating transient ResourceEntity: id={resource_id}, name='{name}'")

        # --- Domain Validation Example ---
        if not name or len(name) < 2:
            raise ValueError("Resource name must be at least 2 characters long.")
        if stack_size < 1:
            raise ValueError("Stack size must be at least 1.")
        # Add more validation based on game rules...

        # Create the entity using keyword arguments for clarity
        # after the required positional resource_id
        resource_entity = ResourceEntity(
            resource_id=resource_id,
            name=name,
            description=description,
            stack_size=stack_size,
            rarity=rarity,
            status=status,
            theme_id=theme_id,
            # created_at/updated_at are typically handled by persistence layer
        )
        logging.debug(f"Transient ResourceEntity created: {resource_entity}")
        return resource_entity

    @staticmethod
    def can_resource_be_used(resource: ResourceEntity) -> bool:
        """
        Example domain logic check: Can this resource type currently be used?
        """
        return resource.status == StatusEnum.ACTIVE

    # Add other methods representing resource-specific domain actions or checks...
    # For example:
    # @staticmethod
    # def get_resource_value(resource: ResourceEntity) -> int:
    #    # Calculate value based on rarity, other factors...
    #    pass


# --- END - app/game_state/managers/resource_manager.py ---
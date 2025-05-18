import enum

class BuildingStatus(enum.Enum):
    """Status of a constructed building instance."""
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    ACTIVE = "ACTIVE"            # Operational
    INACTIVE = "INACTIVE"        # Not operational (e.g., needs power/workers)
    DAMAGED = "DAMAGED"          # HP below a threshold but not destroyed
    DESTROYED = "DESTROYED"      # HP at or below 0
    UPGRADING = "UPGRADING"      # If upgrades take time
    # PLANNED = "PLANNED"        # Optional: Plot claimed, no resources spent yet
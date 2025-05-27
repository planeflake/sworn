# --- DEPRECATED FILE - KEPT ONLY FOR ALEMBIC COMPATIBILITY ---
# This file has been replaced by location_instance.py
# The model Location has been renamed to LocationInstance
# to avoid confusion with domain entities.

# This file is kept only for Alembic migration compatibility.
# Do not use this model in new code, use LocationInstance instead.

from app.db.models.location_instance import LocationInstance

# Alias for backward compatibility
Location = LocationInstance
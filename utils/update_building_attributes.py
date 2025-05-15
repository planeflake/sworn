"""
Utility script to update building blueprints with attributes based on their stats.
This helps migrate existing building blueprints to the new attribute-based system.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.async_session import get_db_session
from app.game_state.repositories.building_blueprint_repository import BuildingBlueprintRepository
from app.game_state.enums.building_attributes import BuildingAttributeType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def update_building_attributes():
    """
    Update building blueprints with attribute data based on their properties.
    This helps convert existing buildings to use the new attribute system.
    """
    async with get_db_session() as session:
        repo = BuildingBlueprintRepository(session)
        
        try:
            # Get all building blueprints
            logger.info("Fetching all building blueprints...")
            blueprints = await repo.find_all()
            logger.info(f"Found {len(blueprints)} building blueprints")
            
            # Process each blueprint
            for blueprint in blueprints:
                logger.info(f"Processing blueprint: {blueprint.name} (ID: {blueprint.entity_id})")
                
                # Initialize metadata and attributes
                if blueprint.metadata_ is None:
                    blueprint.metadata_ = {}
                    
                if 'attributes' not in blueprint.metadata_:
                    blueprint.metadata_['attributes'] = []
                    
                # Determine attributes based on existing fields
                # These are examples - adjust based on your actual fields
                attributes = set()
                
                # Get defensive attribute based on defense value
                if hasattr(blueprint, 'defense') and getattr(blueprint, 'defense', 0) > 5:
                    attributes.add(BuildingAttributeType.DEFENSIVE.value)
                    
                # Get economic attribute based on attractiveness value
                if hasattr(blueprint, 'attractiveness') and getattr(blueprint, 'attractiveness', 0) > 5:
                    attributes.add(BuildingAttributeType.ECONOMIC.value)
                    
                # Get military attribute based on garrison capacity
                if hasattr(blueprint, 'garrison_capacity') and getattr(blueprint, 'garrison_capacity', 0) > 5:
                    attributes.add(BuildingAttributeType.MILITARY.value)
                
                # Use current metadata
                if blueprint.metadata_ and '_metadata' in blueprint.metadata_:
                    nested_metadata = blueprint.metadata_.get('_metadata', {})
                    
                    # Check for population capacity in metadata
                    if nested_metadata.get('population_capacity', 0) > 10:
                        attributes.add(BuildingAttributeType.RESIDENTIAL.value)
                        
                    # Check for cultural flags
                    if 'cultural' in nested_metadata.get('tags', []):
                        attributes.add(BuildingAttributeType.CULTURAL.value)
                        
                # Determine primary category based on dominant attribute
                # This is a simple approach - you might want more sophisticated logic
                if attributes:
                    # Convert set to list
                    blueprint.metadata_['attributes'] = list(attributes)
                    
                    # Use the first attribute as the primary category
                    primary_category = next(iter(attributes))
                    blueprint.metadata_['category'] = primary_category
                    
                    logger.info(f"Adding attributes {attributes} to blueprint {blueprint.name}")
                    logger.info(f"Primary category: {primary_category}")
                else:
                    # Default to INFRASTRUCTURE if no attributes determined
                    blueprint.metadata_['attributes'] = [BuildingAttributeType.INFRASTRUCTURE.value]
                    blueprint.metadata_['category'] = BuildingAttributeType.INFRASTRUCTURE.value
                    logger.info(f"No specific attributes determined, defaulting to INFRASTRUCTURE for {blueprint.name}")
                
                # Additional metadata fields
                # Add any other schema fields you want to include
                if 'building_tags' not in blueprint.metadata_:
                    blueprint.metadata_['building_tags'] = []
                    
                # Save the updated blueprint
                await repo.save(blueprint)
                
            logger.info(f"Successfully updated attributes for {len(blueprints)} building blueprints")
            
        except Exception as e:
            logger.error(f"Error updating building attributes: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    asyncio.run(update_building_attributes())
#!/usr/bin/env python3
"""
Debug script to test resource conversion between JSON and entities.
"""

import logging
import asyncio
import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.async_session import async_session_local
from app.db.models.settlement import Settlement as SettlementModel
from app.game_state.entities.settlement import SettlementEntity
from app.game_state.repositories.settlement_repository import SettlementRepository
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_resource_conversion():
    """Test reading and writing resources for settlements"""
    logger.info("Starting resource conversion debugging")
    
    # Create an async session
    async with async_session_local() as db:
        db: AsyncSession = db
        
        # Get a settlement from the database
        stmt = select(SettlementModel).options(selectinload(SettlementModel.building_instances))
        result = await db.execute(stmt)
        db_settlement = result.scalar_one_or_none()
        
        if not db_settlement:
            logger.error("No settlements found in the database!")
            return
        
        logger.info(f"Found settlement: {db_settlement.name} (ID: {db_settlement.entity_id})")
        
        # Get the current resources
        logger.info(f"Current resources in DB: {db_settlement.resources}")
        
        # Convert DB model to entity
        repository = SettlementRepository(db=db)
        settlement_entity = await repository._convert_to_entity(db_settlement)
        
        logger.info(f"Entity resources after conversion: {settlement_entity.resources}")
        logger.info(f"Resource types in entity: {[(k, type(k)) for k in settlement_entity.resources.keys()]}")
        
        # Create a new settlement with resources
        logger.info("Creating a new settlement with explicit string resources")
        
        test_resources = {
            str(uuid.uuid4()): 10,
            str(uuid.uuid4()): 20,
            str(uuid.uuid4()): 30
        }
        
        logger.info(f"Test resources: {test_resources}")
        
        # Create a DB model with resources
        new_settlement = SettlementModel(
            name="Test Resource Settlement",
            world_id=db_settlement.world_id,
            resources=test_resources
        )
        
        db.add(new_settlement)
        await db.commit()
        await db.refresh(new_settlement)
        
        logger.info(f"New settlement created: {new_settlement.name} (ID: {new_settlement.entity_id})")
        logger.info(f"New settlement resources in DB: {new_settlement.resources}")
        
        # Convert DB model to entity
        new_entity = await repository._convert_to_entity(new_settlement)
        
        logger.info(f"New entity resources after conversion: {new_entity.resources}")
        logger.info(f"Resource types in new entity: {[(k, type(k)) for k in new_entity.resources.keys()]}")
        
        # Test to_dict conversion
        entity_dict = new_entity.to_dict()
        logger.info(f"Entity after to_dict: {entity_dict}")
        logger.info(f"Resource types in entity_dict: {[(k, type(k)) for k in entity_dict['resources'].keys()]}")
        
        # Let's try adding a resource with the UUID keys explicitly converted
        resource_id = uuid.uuid4()
        logger.info(f"Adding resource with explicit string conversion: {resource_id}")
        
        new_entity.add_resource(resource_id, 100)
        logger.info(f"Entity resources after add_resource: {new_entity.resources}")
        logger.info(f"Resource types after add: {[(k, type(k)) for k in new_entity.resources.keys()]}")
        
        # Update the DB model
        model_dict = await repository._entity_to_model_dict(new_entity)
        logger.info(f"Model dict for update: {model_dict}")
        
        for key, value in model_dict.items():
            setattr(new_settlement, key, value)
        
        await db.commit()
        await db.refresh(new_settlement)
        
        logger.info(f"Updated settlement resources in DB: {new_settlement.resources}")
        
        # Let's try one more fetch and conversion
        final_entity = await repository._convert_to_entity(new_settlement)
        logger.info(f"Final entity resources: {final_entity.resources}")
        logger.info(f"Final resource types: {[(k, type(k)) for k in final_entity.resources.keys()]}")

if __name__ == "__main__":
    asyncio.run(debug_resource_conversion())
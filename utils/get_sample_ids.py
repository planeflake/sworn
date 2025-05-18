#!/usr/bin/env python3
# utils/get_sample_ids.py

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

async def get_sample_ids():
    # Load environment variables from .env file
    load_dotenv()
    
    # Create async engine
    db_url = f"postgresql+asyncpg://{os.getenv('DBUSER')}:{os.getenv('DBPASSWORD')}@{os.getenv('DBHOST')}:{os.getenv('DBPORT')}/{os.getenv('DBNAME')}"
    engine = create_async_engine(db_url)
    
    # Get world ID
    async with engine.connect() as conn:
        # Get a world ID
        result = await conn.execute(text("SELECT id FROM worlds LIMIT 1"))
        world_id = result.scalar()
        print(f"World ID: {world_id}")
        
        # Get resource IDs
        result = await conn.execute(text("SELECT id FROM resources LIMIT 5"))
        resources = result.fetchall()
        print("\nResource IDs:")
        for r in resources:
            print(f"- {r[0]}")
    
    # Generate example JSON
    resource_dict = {}
    for i, r in enumerate(resources):
        resource_dict[str(r[0])] = (i + 1) * 10
    
    print("\nExample Settlement Create JSON:")
    print("{\n"
          f'  "world_id": "{world_id}",\n'
          '  "name": "Test Settlement",\n'
          '  "description": "A settlement for testing",\n'
          '  "population": 25,\n'
          '  "resources": {\n')
    
    # Add resources to JSON
    resource_entries = []
    for resource_id, quantity in resource_dict.items():
        resource_entries.append(f'    "{resource_id}": {quantity}')
    
    print(',\n'.join(resource_entries))
    print('  }\n}')

if __name__ == "__main__":
    asyncio.run(get_sample_ids())
#!/usr/bin/env python3
"""
Utility script to seed biome data using the FastAPI routes.
This script can be run directly or imported as a module.

IMPORTANT: Run this script AFTER running migrations with 'alembic upgrade head',
and AFTER starting the FastAPI server.

Usage:
    python utils/seed_biomes_api.py [--api-base-url http://localhost:8081]
"""

import argparse
import json
import logging
import os
import sys
import time
import requests
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to biomes data file
BIOMES_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "09_biomes.json")

def seed_biomes(api_base_url: str = "http://localhost:8000") -> None:
    """
    Seed biomes by calling the API endpoints.
    
    Args:
        api_base_url: Base URL of the API server
    """
    logger.info(f"Starting biome seeding using API at {api_base_url}")
    
    # Check if API server is running
    try:
        response = requests.get(f"{api_base_url}/status")
        if response.status_code != 200:
            logger.error(f"API server at {api_base_url} returned status code {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to API server at {api_base_url}. Is the server running?")
        return
    
    biomes_endpoint = f"{api_base_url}/api/v1/biomes"
    
    # Read biomes data from JSON file
    try:
        with open(BIOMES_DATA_FILE, 'r') as f:
            biomes_data = json.load(f)
        logger.info(f"Loaded {len(biomes_data)} biomes from {BIOMES_DATA_FILE}")
    except FileNotFoundError:
        logger.error(f"Biomes data file not found at {BIOMES_DATA_FILE}")
        return
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in biomes data file at {BIOMES_DATA_FILE}")
        return
    
    # Process each biome
    successful_count = 0
    for biome_data in biomes_data:
        try:
            # Check if biome already exists with this biome_id
            string_id = biome_data["biome_id"]
            response = requests.get(f"{biomes_endpoint}/by-biome-id/{string_id}")
            
            if response.status_code == 200:
                logger.info(f"Biome with ID '{string_id}' already exists. Skipping.")
                successful_count += 1
                continue
            
            # Create the biome
            response = requests.post(biomes_endpoint, json=biome_data)
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                logger.info(f"Created biome: {result.get('name')} (ID: {result.get('id')})")
                successful_count += 1
            else:
                error_detail = response.json().get("detail", response.text) if response.content else "No content"
                logger.error(f"Failed to create biome '{biome_data.get('name', 'unknown')}': {error_detail}")
        except Exception as e:
            logger.error(f"Error processing biome '{biome_data.get('name', 'unknown')}': {str(e)}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    logger.info(f"Biome seeding completed. Successfully processed {successful_count} out of {len(biomes_data)} biomes.")

def main():
    """Parse arguments and run the seeding script."""
    parser = argparse.ArgumentParser(description="Seed biomes using the API.")
    parser.add_argument("--api-base-url", default="http://localhost:8000", help="Base URL of the API server")
    args = parser.parse_args()
    
    seed_biomes(api_base_url=args.api_base_url)

if __name__ == "__main__":
    main()
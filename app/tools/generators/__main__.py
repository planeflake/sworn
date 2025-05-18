#!/usr/bin/env python
"""
Domain Entity Generator CLI

Command-line interface for generating domain entities from SQLAlchemy models.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add parent directory to Python path to allow running as script
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from app.tools.generators.model_analyzer import analyze_model
from app.tools.generators.code_generator import generate_code
from app.tools.generators.config import GeneratorConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("domain-entity-generator")

def configure_parser() -> argparse.ArgumentParser:
    """Configure the argument parser for the CLI"""
    parser = argparse.ArgumentParser(
        description="Generate domain entities and related components from SQLAlchemy models"
    )
    
    parser.add_argument(
        "model_class",
        help="SQLAlchemy model class name to generate from (e.g. 'World')"
    )
    
    parser.add_argument(
        "--model-module",
        dest="model_module",
        default=None,
        help="Python module path to the model (e.g. 'app.db.models.world')"
    )
    
    parser.add_argument(
        "-o", 
        "--output-dir",
        dest="output_dir",
        default=None,
        help="Output directory for generated files (default: app/game_state)"
    )
    
    parser.add_argument(
        "--no-entity",
        dest="generate_entity",
        action="store_false",
        help="Skip domain entity generation"
    )
    
    parser.add_argument(
        "--no-repository",
        dest="generate_repository",
        action="store_false",
        help="Skip repository generation"
    )
    
    parser.add_argument(
        "--no-manager",
        dest="generate_manager",
        action="store_false",
        help="Skip manager generation"
    )
    
    parser.add_argument(
        "--no-service",
        dest="generate_service",
        action="store_false",
        help="Skip service generation"
    )
    
    parser.add_argument(
        "--no-api-schema",
        dest="generate_api_schema",
        action="store_false",
        help="Skip API schema generation"
    )
    
    parser.add_argument(
        "--no-api-routes",
        dest="generate_api_routes",
        action="store_false",
        help="Skip API routes generation"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Overwrite existing files"
    )
    
    parser.add_argument(
        "--api-prefix",
        dest="api_route_prefix",
        default=None,
        help="API route prefix (default: pluralized snake_case of entity name)"
    )
    
    parser.add_argument(
        "--api-tag",
        dest="api_tag",
        default=None,
        help="API tag for documentation (default: entity name)"
    )
    
    parser.add_argument(
        "--tests",
        dest="create_test_files",
        action="store_true",
        help="Generate test files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Verbose output"
    )
    
    return parser

def main():
    """Main entry point for the CLI application"""
    parser = configure_parser()
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Configure generator
        config = GeneratorConfig(
            model_class_name=args.model_class,
            model_module=args.model_module,
            output_dir=args.output_dir or os.path.join(os.getcwd(), "app/game_state"),
            generate_entity=args.generate_entity,
            generate_repository=args.generate_repository,
            generate_manager=args.generate_manager,
            generate_service=args.generate_service,
            generate_api_schema=args.generate_api_schema,
            generate_api_routes=args.generate_api_routes,
            force_overwrite=args.force,
            api_route_prefix=args.api_route_prefix,
            api_tag=args.api_tag,
            create_test_files=args.create_test_files
        )
        
        # Log configuration
        logger.debug(f"Generator configuration: {vars(config)}")
        
        # Analyze model
        logger.info(f"Analyzing model: {args.model_class}")
        model_info = analyze_model(config)
        
        # Generate code
        logger.info("Generating code...")
        generated_files = generate_code(model_info, config)
        
        # Log results
        logger.info(f"Generated {len(generated_files)} files:")
        for file_path in generated_files:
            logger.info(f"  - {file_path}")
        
        logger.info("Domain entity generation complete!")
        return 0
        
    except Exception as e:
        logger.error(f"Error generating domain entity: {str(e)}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
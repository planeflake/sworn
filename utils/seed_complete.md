# Seed Script Improvements

## Problem Addressed
The original seed script was experiencing an issue where settlement creation with leader assignment failed because the character entities weren't fully committed to the database before trying to use them as foreign keys in settlements.

## Changes Made

1. **Two-Phase Approach**:
   - Phase 1: Create themes, world, characters, and resources
   - Phase 2: Create settlements with leaders and building blueprints
   - Added verification between phases and a pause to ensure database transactions are committed

2. **Character Creation Improvements**:
   - Added verification step that fetches characters from database after creation
   - Ensures character IDs are available before proceeding to settlement creation
   - Made a copy of templates to prevent modifying original data

3. **Settlement Creation Improvements**:
   - Added multiple leader assignment fallback methods
   - Created a dedicated helper function `try_assign_leader` with four different methods
   - Added verification that character exists in database before assignment
   - Better error handling and logging for settlement leader assignment

4. **Command Line Options**:
   - Added `--phase` option to run only specific phases
   - Phase 1 outputs useful information for running Phase 2 separately if needed

5. **Additional Features**:
   - Enhanced logging for troubleshooting
   - Added verification steps between operations
   - Increased timeouts between critical operations

## How to Use
```
python utils/seed_complete.py [--api-base-url http://localhost:8000] [--phase {1,2}] [--skip-truncate] [--force]
```

### Arguments
- `--api-base-url URL`: Base URL of the API server (default: http://localhost:8000)
- `--phase {1,2}`: Run only a specific phase (1 for foundation entities, 2 for settlements)
- `--skip-truncate`: Skip truncating tables before seeding
- `--force`: Continue seeding even if truncation fails

## Benefits
- Prevents foreign key constraint violations
- More deterministic seeding process
- Better error handling and debugging information
- More robust leader assignment with multiple fallback methods
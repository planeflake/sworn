#!/usr/bin/env python3
"""
API Test Seeder for Fantasy Settlement Location Subtypes
Tests the API endpoints while seeding data
"""

import asyncio
import httpx
import json
from typing import Any
import sys

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

# Your existing IDs from the database
FANTASY_MEDIEVAL_THEME_ID = "b2494b91-f7d1-4c8d-9da2-c628816ed9de"
AREA_LOCATION_TYPE_ID = "f1df65be-0db7-40d9-952f-3f8ff3b803c1"

# Complete fantasy settlement test data
fantasy_settlement_subtypes = [
    {
        "code": "metropolis",
        "name": "Metropolis",
        "description": "A massive city, the largest settlement type with over 100,000 inhabitants. Centers of trade, politics, and culture.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 100000,
                "max_value": 1000000
            },
            {
                "name": "wealth_level",
                "type": "string",
                "enum": ["wealthy", "very_wealthy", "extremely_wealthy"],
                "description": "Economic status of the metropolis"
            },
            {
                "name": "government_type",
                "type": "string",
                "enum": ["monarchy", "republic", "oligarchy", "theocracy"],
                "description": "Type of government ruling the metropolis"
            }
        ],
        "optional_attributes": [
            {
                "name": "has_university",
                "type": "boolean",
                "description": "Whether the metropolis has a university or academy"
            },
            {
                "name": "magical_district",
                "type": "boolean",
                "description": "Whether there's a dedicated magical quarter"
            }
        ],
        "tags": ["fantasy", "settlement", "urban", "large", "political"],
        "rarity": "rare",
        "generation_weight": 0.1
    },
    {
        "code": "large_city",
        "name": "Large City",
        "description": "A major urban center with 25,000-100,000 inhabitants. Important regional hubs with significant political and economic influence.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 25000,
                "max_value": 100000
            },
            {
                "name": "has_walls",
                "type": "boolean",
                "description": "Whether the city is fortified with walls"
            }
        ],
        "optional_attributes": [
            {
                "name": "guild_presence",
                "type": "array",
                "description": "List of major guilds present in the city",
                "items": {"type": "string"}
            },
            {
                "name": "notable_districts",
                "type": "integer",
                "description": "Number of distinct districts"
            }
        ],
        "tags": ["fantasy", "settlement", "urban", "fortified"],
        "rarity": "uncommon",
        "generation_weight": 0.3
    },
    {
        "code": "small_city",
        "name": "Small City",
        "description": "An urban settlement with 8,000-25,000 inhabitants. Regional trade centers with basic services and governance.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 8000,
                "max_value": 25000
            }
        ],
        "optional_attributes": [
            {
                "name": "market_days",
                "type": "array",
                "description": "Days of the week when markets are held",
                "items": {"type": "string"}
            },
            {
                "name": "specialty_craft",
                "type": "string",
                "description": "What the city is known for producing"
            }
        ],
        "tags": ["fantasy", "settlement", "urban", "trade"],
        "rarity": "common",
        "generation_weight": 0.8
    },
    {
        "code": "large_town",
        "name": "Large Town",
        "description": "A sizable town with 2,000-8,000 inhabitants. Local administrative centers with markets and basic services.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 2000,
                "max_value": 8000
            }
        ],
        "optional_attributes": [
            {
                "name": "has_inn",
                "type": "boolean",
                "description": "Whether the town has a proper inn"
            },
            {
                "name": "local_lord",
                "type": "string",
                "description": "Name or title of the local ruling authority"
            }
        ],
        "tags": ["fantasy", "settlement", "town", "administrative"],
        "rarity": "common",
        "generation_weight": 1.2
    },
    {
        "code": "small_town",
        "name": "Small Town",
        "description": "A modest town with 500-2,000 inhabitants. Local gathering places with basic crafts and services.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 500,
                "max_value": 2000
            }
        ],
        "optional_attributes": [
            {
                "name": "primary_trade",
                "type": "string",
                "description": "Main economic activity or trade"
            },
            {
                "name": "has_temple",
                "type": "boolean",
                "description": "Whether the town has a temple or shrine"
            }
        ],
        "tags": ["fantasy", "settlement", "town", "rural"],
        "rarity": "common",
        "generation_weight": 1.5
    },
    {
        "code": "village",
        "name": "Village",
        "description": "A rural settlement with 100-500 inhabitants. Agricultural communities centered around farming or resource extraction.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 100,
                "max_value": 500
            }
        ],
        "optional_attributes": [
            {
                "name": "primary_crop",
                "type": "string",
                "description": "Main agricultural product"
            },
            {
                "name": "village_elder",
                "type": "string",
                "description": "Name of the village leader or elder"
            }
        ],
        "tags": ["fantasy", "settlement", "village", "agricultural", "rural"],
        "rarity": "common",
        "generation_weight": 2.0
    },
    {
        "code": "hamlet",
        "name": "Hamlet",
        "description": "A tiny rural settlement with 20-100 inhabitants. Small farming communities or specialized settlements.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 20,
                "max_value": 100
            }
        ],
        "optional_attributes": [
            {
                "name": "founding_reason",
                "type": "string",
                "description": "Why this hamlet was established"
            }
        ],
        "tags": ["fantasy", "settlement", "hamlet", "tiny", "rural"],
        "rarity": "common",
        "generation_weight": 1.8
    },
    {
        "code": "homestead",
        "name": "Homestead",
        "description": "An isolated dwelling with 1-20 inhabitants. Single families or small groups living away from larger settlements.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 1,
                "max_value": 20
            }
        ],
        "optional_attributes": [
            {
                "name": "isolation_reason",
                "type": "string",
                "description": "Why this homestead is isolated"
            },
            {
                "name": "defensive_features",
                "type": "array",
                "description": "Defensive measures taken",
                "items": {"type": "string"}
            }
        ],
        "tags": ["fantasy", "settlement", "homestead", "isolated", "frontier"],
        "rarity": "common",
        "generation_weight": 1.0
    },
    {
        "code": "fortress",
        "name": "Fortress",
        "description": "A military stronghold with 200-2,000 inhabitants. Defensive installations designed to control territory.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 200,
                "max_value": 2000
            },
            {
                "name": "garrison_size",
                "type": "integer",
                "description": "Number of military personnel"
            },
            {
                "name": "fortification_level",
                "type": "string",
                "enum": ["basic", "advanced", "masterwork"],
                "description": "Quality of fortifications"
            }
        ],
        "optional_attributes": [
            {
                "name": "siege_equipment",
                "type": "array",
                "description": "Defensive siege weapons available",
                "items": {"type": "string"}
            },
            {
                "name": "strategic_importance",
                "type": "string",
                "description": "Why this location is strategically important"
            }
        ],
        "tags": ["fantasy", "settlement", "military", "fortified", "strategic"],
        "rarity": "uncommon",
        "generation_weight": 0.4
    },
    {
        "code": "monastery",
        "name": "Monastery",
        "description": "A religious settlement with 50-500 inhabitants. Centers of learning, worship, and spiritual guidance.",
        "location_type_id": AREA_LOCATION_TYPE_ID,
        "theme_id": FANTASY_MEDIEVAL_THEME_ID,
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 50,
                "max_value": 500
            },
            {
                "name": "religious_order",
                "type": "string",
                "description": "Which religious order runs the monastery"
            }
        ],
        "optional_attributes": [
            {
                "name": "library_size",
                "type": "string",
                "enum": ["small", "medium", "large", "vast"],
                "description": "Size of the monastery's library"
            },
            {
                "name": "specialization",
                "type": "string",
                "description": "What the monastery specializes in (healing, brewing, copying, etc.)"
            }
        ],
        "tags": ["fantasy", "settlement", "religious", "learning", "peaceful"],
        "rarity": "uncommon",
        "generation_weight": 0.5
    }
]


class LocationSubtypeAPITester:
    """Test class for location subtype API endpoints"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = None
        self.created_subtypes = []

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    @staticmethod
    def print_result(emoji: str, message: str, data: Any = None):
        """Helper to print test results"""
        print(f"{emoji} {message}")
        if data and isinstance(data, dict) and data.get("detail"):
            print(f"   Error: {data['detail']}")
        elif data:
            print(f"   Data: {json.dumps(data, indent=2)}")

    async def test_bulk_create(self) -> bool:
        """Test bulk creation of all fantasy settlement subtypes"""
        print("\n🚀 Testing Bulk Create Location Subtypes")
        print("=" * 50)

        try:
            response = await self.client.post(
                f"{self.base_url}/location-subtypes/bulk",
                json=fantasy_settlement_subtypes
            )

            if response.status_code == 201:
                self.created_subtypes = response.json()
                self.print_result("✅", f"Successfully created {len(self.created_subtypes)} location subtypes")

                # Show summary
                for subtype in self.created_subtypes:
                    print(f"   📍 {subtype['name']} ({subtype['code']}) - {subtype['rarity']}")

                return True
            else:
                self.print_result("❌", f"Bulk create failed: {response.status_code}", response.json())
                return False

        except Exception as error:
            self.print_result("💥", f"Exception during bulk create: {error}")
            return False

    async def test_get_endpoints(self) -> bool:
        """Test various GET endpoints"""
        if not self.created_subtypes:
            print("⚠️  No subtypes to test GET endpoints with")
            return False

        print("\n🔍 Testing GET Endpoints")
        print("=" * 30)

        success_count = 0
        test_count = 0

        # Test get by ID
        test_subtype = self.created_subtypes[0]
        test_count += 1

        try:
            response = await self.client.get(f"{self.base_url}/location-subtypes/{test_subtype['id']}")
            if response.status_code == 200:
                self.print_result("✅", f"Get by ID works: {test_subtype['name']}")
                success_count += 1
            else:
                self.print_result("❌", f"Get by ID failed: {response.status_code}")
        except Exception as error:
            self.print_result("💥", f"Get by ID exception: {error}")

        # Test get by code
        test_count += 1
        try:
            response = await self.client.get(f"{self.base_url}/location-subtypes/code/{test_subtype['code']}")
            if response.status_code == 200:
                self.print_result("✅", f"Get by code works: {test_subtype['code']}")
                success_count += 1
            else:
                self.print_result("❌", f"Get by code failed: {response.status_code}")
        except Exception as error:
            self.print_result("💥", f"Get by code exception: {error}")

        # Test search with filters
        test_count += 1
        try:
            response = await self.client.get(
                f"{self.base_url}/location-subtypes/",
                params={"theme_id": FANTASY_MEDIEVAL_THEME_ID, "limit": 5}
            )
            if response.status_code == 200:
                data = response.json()
                self.print_result("✅", f"Search by theme works: found {data['total']} items")
                success_count += 1
            else:
                self.print_result("❌", f"Search failed: {response.status_code}")
        except Exception as error:
            self.print_result("💥", f"Search exception: {error}")

        # Test get by location type
        test_count += 1
        try:
            response = await self.client.get(f"{self.base_url}/location-subtypes/location-type/{AREA_LOCATION_TYPE_ID}")
            if response.status_code == 200:
                data = response.json()
                self.print_result("✅", f"Get by location type works: found {len(data)} items")
                success_count += 1
            else:
                self.print_result("❌", f"Get by location type failed: {response.status_code}")
        except Exception as error:
            self.print_result("💥", f"Get by location type exception: {error}")

        # Test get by rarity
        test_count += 1
        try:
            response = await self.client.get(f"{self.base_url}/location-subtypes/rarity/common")
            if response.status_code == 200:
                data = response.json()
                self.print_result("✅", f"Get by rarity works: found {len(data)} common items")
                success_count += 1
            else:
                self.print_result("❌", f"Get by rarity failed: {response.status_code}")
        except Exception as error:
            self.print_result("💥", f"Get by rarity exception: {error}")

        print(f"\n📊 GET Tests: {success_count}/{test_count} passed")
        return success_count == test_count

    async def test_update_endpoint(self) -> bool:
        """Test update endpoint"""
        if not self.created_subtypes:
            print("⚠️  No subtypes to test update endpoint with")
            return False

        print("\n✏️  Testing Update Endpoint")
        print("=" * 30)

        test_subtype = self.created_subtypes[0]
        update_data = {
            "description": f"Updated description for {test_subtype['name']} - tested at API level",
            "generation_weight": 99.9
        }

        try:
            response = await self.client.put(
                f"{self.base_url}/location-subtypes/{test_subtype['id']}",
                json=update_data
            )

            if response.status_code == 200:
                updated = response.json()
                self.print_result("✅", f"Update works: {updated['name']}")
                print(f"   📝 New description: {updated['description'][:50]}...")
                return True
            else:
                self.print_result("❌", f"Update failed: {response.status_code}", response.json())
                return False

        except Exception as error:
            self.print_result("💥", f"Update exception: {error}")
            return False

    async def test_delete_endpoint(self) -> bool:
        """Test delete endpoint (deletes one test item)"""
        if len(self.created_subtypes) < 2:
            print("⚠️  Need at least 2 subtypes to safely test delete")
            return False

        print("\n🗑️  Testing Delete Endpoint")
        print("=" * 30)

        # Delete the last item (keep most for other tests)
        test_subtype = self.created_subtypes[-1]

        try:
            response = await self.client.delete(f"{self.base_url}/location-subtypes/{test_subtype['id']}")

            if response.status_code == 204:
                self.print_result("✅", f"Delete works: removed {test_subtype['name']}")
                self.created_subtypes.pop()  # Remove from our list
                return True
            else:
                self.print_result("❌", f"Delete failed: {response.status_code}")
                return False

        except Exception as error:
            self.print_result("💥", f"Delete exception: {error}")
            return False

    async def run_all_tests(self) -> bool:
        """Run complete test suite"""
        print("🧪 Starting Location Subtype API Test Suite")
        print("🎯 This will seed fantasy settlement data AND test all endpoints")
        print("=" * 60)

        results = [await self.test_bulk_create(), await self.test_get_endpoints(), await self.test_update_endpoint(),
                   await self.test_delete_endpoint()]

        # Summary
        passed = sum(results)
        total = len(results)

        print(f"\n🏆 Test Suite Complete: {passed}/{total} test groups passed")

        if passed == total:
            print("🎉 All tests passed! Your API is working correctly.")
            print(f"📊 You now have {len(self.created_subtypes)} fantasy settlement subtypes in your database.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")

        return passed == total


async def main():
    """Main function to run the test suite"""
    print("🏰 Fantasy Settlement Location Subtype API Tester")
    print(f"🔗 Testing API at: {API_BASE_URL}")
    print()

    async with LocationSubtypeAPITester() as tester:
        success = await tester.run_all_tests()

        if success:
            print("\n✨ Data seeding and API testing completed successfully!")
            sys.exit(0)
        else:
            print("\n💀 Some tests failed. Check your API implementation.")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
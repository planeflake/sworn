#!/usr/bin/env python3
"""
Comprehensive Location Subtype Import and Review Script
Imports ALL location subtypes and provides detailed analysis
"""

import asyncio
import httpx
import json
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 60.0  # Increased for large imports

# Theme and Location Type mappings for reporting
THEMES = {
    "104275ef-4ae9-4364-86f1-2cbeb886c3ad": "Sci-Fi",
    "1265b705-778e-4df1-b7ac-2a3f7a01ac22": "Post-Apocalyptic",
    "72aab8f1-2e04-45aa-8075-6936e716f09b": "Lovecraftian",
    "7cdd3506-4828-4269-a96e-e7fea047132b": "Warhammer 40K",
    "b2494b91-f7d1-4c8d-9da2-c628816ed9de": "Fantasy Medieval",
    "c0d8944d-4ebf-42bc-b7ad-8e5edf9c296e": "Runeslicer",
    "cdef42d5-6d3a-4773-bb34-0668e0dea89e": "Warhammer Fantasy"
}

LOCATION_TYPES = {
    "f76847fe-05ef-4b84-892e-d2c87d8894b6": "Dimension",
    "59df72e8-3b86-4b6b-a435-f891fa31a2ea": "Cosmos",
    "503879ac-acc4-43d6-afa4-29d4a5bb2348": "Galaxy",
    "14852fa2-b3b3-43b9-8e79-e96e8b717f29": "Star System",
    "a6a0d734-8de1-4a6a-bb7b-fdef23236fdd": "World",
    "cabcc823-46fa-437d-b91f-d70f06df022f": "Celestial Body",
    "3d1c462a-eeb4-436b-aa8c-34944762bfd6": "Constructed Habitat",
    "899ea475-99e2-4a59-9f02-bf460a7314a8": "Elemental Plane",
    "87e024f8-6e82-4f91-aa65-e9cf5cec464e": "Zone",
    "f1df65be-0db7-40d9-952f-3f8ff3b803c1": "Area",
    "1e93492f-4630-49aa-99f2-b714a590c600": "Point of Interest"
}

# Import the comprehensive subtypes data
from expanded_location_subtypes import all_comprehensive_subtypes


class ComprehensiveLocationSubtypeManager:
    """Manages comprehensive import and analysis of location subtypes"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = None
        self.imported_subtypes = []
        self.existing_subtypes = []
        self.import_stats = {}

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    def print_header(self, title: str, emoji: str = "🔥"):
        """Print a formatted header"""
        print(f"\n{emoji} {title}")
        print("=" * (len(title) + 4))

    def print_result(self, emoji: str, message: str, data: Any = None):
        """Print formatted result"""
        print(f"{emoji} {message}")
        if data and isinstance(data, dict) and data.get("detail"):
            print(f"   Error: {data['detail']}")

    async def get_existing_subtypes(self) -> List[Dict]:
        """Get all existing location subtypes"""
        self.print_header("Fetching Existing Location Subtypes", "📋")

        try:
            response = await self.client.get(
                f"{self.base_url}/location-subtypes/",
                params={"limit": 1000}  # Get all
            )

            if response.status_code == 200:
                data = response.json()
                existing = data.get("items", [])
                self.existing_subtypes = existing

                self.print_result("✅", f"Found {len(existing)} existing subtypes")

                # Show breakdown by theme
                theme_counts = Counter()
                for subtype in existing:
                    theme_name = THEMES.get(subtype["theme_id"], "Unknown")
                    theme_counts[theme_name] += 1

                if theme_counts:
                    print("   📊 Existing breakdown by theme:")
                    for theme, count in theme_counts.most_common():
                        print(f"      {theme}: {count} subtypes")

                return existing
            else:
                self.print_result("❌", f"Failed to fetch existing subtypes: {response.status_code}")
                return []

        except Exception as e:
            self.print_result("💥", f"Exception fetching existing subtypes: {e}")
            return []

    async def import_all_subtypes(self) -> bool:
        """Import all comprehensive location subtypes"""
        self.print_header("Importing All Location Subtypes", "🚀")

        print(f"📦 Preparing to import {len(all_comprehensive_subtypes)} new subtypes...")

        # Show what we're about to import
        import_theme_counts = Counter()
        import_location_counts = Counter()

        for subtype in all_comprehensive_subtypes:
            theme_name = THEMES.get(subtype["theme_id"], "Unknown")
            location_name = LOCATION_TYPES.get(subtype["location_type_id"], "Unknown")
            import_theme_counts[theme_name] += 1
            import_location_counts[location_name] += 1

        print("   📊 Import breakdown by theme:")
        for theme, count in import_theme_counts.most_common():
            print(f"      {theme}: {count} subtypes")

        print("   🏗️ Import breakdown by location type:")
        for location, count in import_location_counts.most_common():
            print(f"      {location}: {count} subtypes")

        try:
            print(f"\n🔄 Starting bulk import...")
            response = await self.client.post(
                f"{self.base_url}/location-subtypes/bulk",
                json=all_comprehensive_subtypes
            )

            if response.status_code == 201:
                imported = response.json()
                self.imported_subtypes = imported

                self.print_result("✅", f"Successfully imported {len(imported)} location subtypes!")

                # Store stats for later analysis
                self.import_stats = {
                    "total_imported": len(imported),
                    "themes": import_theme_counts,
                    "location_types": import_location_counts,
                    "import_time": datetime.now()
                }

                return True
            else:
                try:
                    error_data = response.json()
                    self.print_result("❌", f"Bulk import failed: {response.status_code}", error_data)
                except:
                    self.print_result("❌", f"Bulk import failed: {response.status_code}")
                    print(f"   Raw response: {response.text[:500]}")
                return False

        except Exception as e:
            self.print_result("💥", f"Exception during bulk import: {e}")
            return False

    async def test_key_endpoints(self) -> Dict[str, bool]:
        """Test key API endpoints with imported data"""
        self.print_header("Testing Key API Endpoints", "🧪")

        if not self.imported_subtypes:
            self.print_result("⚠️", "No imported subtypes to test with")
            return {}

        test_results = {}
        test_subtype = self.imported_subtypes[0]

        # Test 1: Get by ID
        try:
            response = await self.client.get(f"{self.base_url}/location-subtypes/{test_subtype['id']}")
            test_results["get_by_id"] = response.status_code == 200
            self.print_result("✅" if test_results["get_by_id"] else "❌",
                              f"Get by ID: {response.status_code}")
        except Exception as e:
            test_results["get_by_id"] = False
            self.print_result("💥", f"Get by ID failed: {e}")

        # Test 2: Get by code
        try:
            response = await self.client.get(f"{self.base_url}/location-subtypes/code/{test_subtype['code']}")
            test_results["get_by_code"] = response.status_code == 200
            self.print_result("✅" if test_results["get_by_code"] else "❌",
                              f"Get by code: {response.status_code}")
        except Exception as e:
            test_results["get_by_code"] = False
            self.print_result("💥", f"Get by code failed: {e}")

        # Test 3: Search by theme
        try:
            theme_id = test_subtype['theme_id']
            response = await self.client.get(
                f"{self.base_url}/location-subtypes/",
                params={"theme_id": theme_id, "limit": 50}
            )
            if response.status_code == 200:
                data = response.json()
                found_count = data.get("total", 0)
                test_results["search_by_theme"] = found_count > 0
                self.print_result("✅" if test_results["search_by_theme"] else "❌",
                                  f"Search by theme: found {found_count} items")
            else:
                test_results["search_by_theme"] = False
                self.print_result("❌", f"Search by theme failed: {response.status_code}")
        except Exception as e:
            test_results["search_by_theme"] = False
            self.print_result("💥", f"Search by theme failed: {e}")

        # Test 4: Get by rarity
        try:
            response = await self.client.get(f"{self.base_url}/location-subtypes/rarity/common")
            if response.status_code == 200:
                common_items = response.json()
                test_results["get_by_rarity"] = len(common_items) > 0
                self.print_result("✅" if test_results["get_by_rarity"] else "❌",
                                  f"Get by rarity: found {len(common_items)} common items")
            else:
                test_results["get_by_rarity"] = False
                self.print_result("❌", f"Get by rarity failed: {response.status_code}")
        except Exception as e:
            test_results["get_by_rarity"] = False
            self.print_result("💥", f"Get by rarity failed: {e}")

        passed = sum(test_results.values())
        total = len(test_results)
        self.print_result("📊", f"Endpoint tests: {passed}/{total} passed")

        return test_results

    async def analyze_complete_dataset(self) -> Dict[str, Any]:
        """Analyze the complete dataset of location subtypes"""
        self.print_header("Complete Dataset Analysis", "📈")

        # Get fresh data from API
        try:
            response = await self.client.get(
                f"{self.base_url}/location-subtypes/",
                params={"limit": 1000}
            )

            if response.status_code != 200:
                self.print_result("❌", f"Failed to fetch complete dataset: {response.status_code}")
                return {}

            data = response.json()
            all_subtypes = data.get("items", [])

        except Exception as e:
            self.print_result("💥", f"Exception fetching complete dataset: {e}")
            return {}

        if not all_subtypes:
            self.print_result("⚠️", "No subtypes found in dataset")
            return {}

        # Comprehensive analysis
        analysis = {
            "total_subtypes": len(all_subtypes),
            "by_theme": defaultdict(list),
            "by_location_type": defaultdict(list),
            "by_rarity": defaultdict(list),
            "coverage_matrix": defaultdict(lambda: defaultdict(int))
        }

        # Categorize all subtypes
        for subtype in all_subtypes:
            theme_name = THEMES.get(subtype["theme_id"], "Unknown")
            location_name = LOCATION_TYPES.get(subtype["location_type_id"], "Unknown")
            rarity = subtype.get("rarity", "unknown")

            analysis["by_theme"][theme_name].append(subtype)
            analysis["by_location_type"][location_name].append(subtype)
            analysis["by_rarity"][rarity].append(subtype)
            analysis["coverage_matrix"][theme_name][location_name] += 1

        # Print comprehensive report
        print(f"📊 COMPREHENSIVE DATASET ANALYSIS")
        print(f"   Total Location Subtypes: {analysis['total_subtypes']}")
        print()

        print("🎭 BREAKDOWN BY THEME:")
        for theme, subtypes in sorted(analysis["by_theme"].items()):
            print(f"   {theme}: {len(subtypes)} subtypes")
            # Show a few examples
            examples = [s["name"] for s in subtypes[:3]]
            if len(subtypes) > 3:
                examples.append(f"... +{len(subtypes) - 3} more")
            print(f"      Examples: {', '.join(examples)}")
        print()

        print("🏗️ BREAKDOWN BY LOCATION TYPE:")
        for location, subtypes in sorted(analysis["by_location_type"].items()):
            print(f"   {location}: {len(subtypes)} subtypes")
            # Show theme diversity
            themes = set(THEMES.get(s["theme_id"], "Unknown") for s in subtypes)
            print(f"      Themes: {', '.join(sorted(themes))}")
        print()

        print("💎 BREAKDOWN BY RARITY:")
        for rarity, subtypes in sorted(analysis["by_rarity"].items()):
            print(f"   {rarity.title()}: {len(subtypes)} subtypes")
        print()

        print("🎯 COVERAGE MATRIX (Theme × Location Type):")
        print("   " + "".ljust(18) + " ".join(f"{loc[:8]:>8}" for loc in sorted(set(LOCATION_TYPES.values()))))
        for theme in sorted(analysis["coverage_matrix"].keys()):
            row = f"   {theme[:16]:16} "
            for location in sorted(set(LOCATION_TYPES.values())):
                count = analysis["coverage_matrix"][theme][location]
                row += f"{count:>8}"
            print(row)
        print()

        # Coverage statistics
        total_possible = len(THEMES) * len(LOCATION_TYPES)
        actual_coverage = sum(1 for theme in analysis["coverage_matrix"].values()
                              for count in theme.values() if count > 0)
        coverage_percent = (actual_coverage / total_possible) * 100

        print(f"📈 COVERAGE STATISTICS:")
        print(f"   Matrix Coverage: {actual_coverage}/{total_possible} ({coverage_percent:.1f}%)")
        print(f"   Average Subtypes per Theme: {analysis['total_subtypes'] / len(analysis['by_theme']):.1f}")
        print(
            f"   Average Subtypes per Location Type: {analysis['total_subtypes'] / len(analysis['by_location_type']):.1f}")

        return analysis

    async def generate_summary_report(self, test_results: Dict[str, bool], analysis: Dict[str, Any]):
        """Generate final summary report"""
        self.print_header("FINAL SUMMARY REPORT", "🏆")

        print(f"🕒 Import completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        if self.import_stats:
            print("📦 IMPORT SUMMARY:")
            print(f"   ✅ Successfully imported: {self.import_stats['total_imported']} subtypes")
            print(f"   🎭 Themes covered: {len(self.import_stats['themes'])}")
            print(f"   🏗️ Location types covered: {len(self.import_stats['location_types'])}")
            print()

        if analysis:
            print("📊 DATASET HEALTH:")
            print(f"   📈 Total subtypes in system: {analysis['total_subtypes']}")
            print(f"   🎯 Unique themes: {len(analysis['by_theme'])}")
            print(f"   🏗️ Unique location types: {len(analysis['by_location_type'])}")
            print()

        if test_results:
            passed_tests = sum(test_results.values())
            total_tests = len(test_results)
            print("🧪 API HEALTH:")
            print(f"   ✅ Endpoint tests passed: {passed_tests}/{total_tests}")
            for test_name, result in test_results.items():
                status = "✅" if result else "❌"
                print(f"   {status} {test_name.replace('_', ' ').title()}")
            print()

        # Success determination
        import_success = bool(self.import_stats and self.import_stats["total_imported"] > 0)
        test_success = bool(test_results and sum(test_results.values()) == len(test_results))

        overall_success = import_success and test_success

        if overall_success:
            print("🎉 OVERALL STATUS: SUCCESS!")
            print("   ✨ All location subtypes imported successfully")
            print("   ✨ All API endpoints working correctly")
            print("   ✨ Your location subtype system is fully operational!")
        else:
            print("⚠️ OVERALL STATUS: PARTIAL SUCCESS")
            if not import_success:
                print("   ❌ Import had issues")
            if not test_success:
                print("   ❌ Some API tests failed")
            print("   💡 Check the detailed output above for specific issues")

        print()
        print("🚀 NEXT STEPS:")
        print("   1. Create location instances using these subtypes")
        print("   2. Build procedural generation with rarity weights")
        print("   3. Expand to remaining themes/location types")
        print("   4. Integrate with your game mechanics")

        return overall_success


async def main():
    """Main execution function"""
    print("🌟 COMPREHENSIVE LOCATION SUBTYPE IMPORT & ANALYSIS")
    print("🎯 This will import ALL location subtypes and provide complete analysis")
    print("=" * 70)

    async with ComprehensiveLocationSubtypeManager() as manager:

        # Step 1: Get existing data for comparison
        await manager.get_existing_subtypes()

        # Step 2: Import all new subtypes
        import_success = await manager.import_all_subtypes()

        if not import_success:
            print("\n💀 Import failed. Exiting.")
            sys.exit(1)

        # Step 3: Test key endpoints
        test_results = await manager.test_key_endpoints()

        # Step 4: Comprehensive analysis
        analysis = await manager.analyze_complete_dataset()

        # Step 5: Final summary
        success = await manager.generate_summary_report(test_results, analysis)

        if success:
            print("\n✨ Mission accomplished! Your location subtype system is ready! 🎮")
            sys.exit(0)
        else:
            print("\n⚠️ Some issues encountered. Check the detailed output above.")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Import interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
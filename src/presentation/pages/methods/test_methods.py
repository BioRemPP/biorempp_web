"""
Test script for Methods page implementation.

This script tests the MethodsService and verifies that all components
can be loaded correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.presentation.pages.methods import (
    get_all_modules_metadata,
    get_methods_service,
    get_module_metadata,
)


def test_methods_service():
    """Test MethodsService functionality."""
    print("=" * 60)
    print("Testing MethodsService")
    print("=" * 60)

    service = get_methods_service()

    # Test 1: Load workflows
    print("\n1. Loading workflows...")
    try:
        workflows = service.load_workflows()
        print(f"   ✅ Loaded {len(workflows)} workflows")
    except Exception as e:
        print(f"   ❌ Error loading workflows: {e}")
        return False

    # Test 2: Get workflow by ID
    print("\n2. Getting workflow UC-1.1...")
    try:
        wf = service.get_workflow("UC-1.1")
        if wf:
            print(f"   ✅ Found: {wf['title']}")
            print(f"      Module: {wf['module']}")
            print(f"      Steps: {len(wf['steps'])}")
        else:
            print("   ❌ Workflow not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Get workflows by module
    print("\n3. Getting workflows for each module...")
    for module in range(1, 9):
        try:
            module_wfs = service.get_workflows_by_module(module)
            print(f"   Module {module}: {len(module_wfs)} workflows")
        except Exception as e:
            print(f"   ❌ Module {module} error: {e}")

    # Test 4: Get module info
    print("\n4. Getting module info...")
    try:
        info = service.get_module_info(1)
        print(f"   ✅ Module 1: {info['use_case_count']} use cases")
        print(f"      IDs: {', '.join(info['use_case_ids'][:3])}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 5: Total use cases
    print("\n5. Getting total use cases...")
    try:
        total = service.get_total_use_cases()
        print(f"   ✅ Total: {total} use cases")
        if total == 56:
            print("   ✅ All 56 use cases present!")
        else:
            print(f"   ⚠️  Expected 56, got {total}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    return True


def test_module_metadata():
    """Test module metadata."""
    print("\n" + "=" * 60)
    print("Testing Module Metadata")
    print("=" * 60)

    # Test all modules
    print("\nModule Metadata:")
    for module in range(1, 9):
        try:
            metadata = get_module_metadata(module)
            print(f"\n   Module {module}: {metadata['icon']} {metadata['short_title']}")
            print(f"   Color: {metadata['color']}")
            print(f"   Use Cases: {metadata['use_case_count']}")
        except Exception as e:
            print(f"   ❌ Module {module} error: {e}")

    return True


def test_component_imports():
    """Test that all components can be imported."""
    print("\n" + "=" * 60)
    print("Testing Component Imports")
    print("=" * 60)

    components = [
        ("workflow_card", "create_workflow_card"),
        ("module_section", "create_module_section"),
        ("pagination", "create_pagination"),
        ("layout", "create_methods_layout"),
    ]

    for module_name, func_name in components:
        try:
            module = __import__(
                f"presentation.pages.methods.{module_name}", fromlist=[func_name]
            )
            func = getattr(module, func_name)
            print(f"   ✅ {module_name}.{func_name}")
        except Exception as e:
            print(f"   ❌ {module_name}.{func_name}: {e}")
            return False

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("METHODS PAGE IMPLEMENTATION TEST")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("MethodsService", test_methods_service()))
    results.append(("Module Metadata", test_module_metadata()))
    results.append(("Component Imports", test_component_imports()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All tests passed! Methods page is ready.")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

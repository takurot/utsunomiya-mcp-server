"""
Test script for Utsunomiya Open Data MCP Server
"""
import asyncio
import json
from utsunomiya_mcp.server import load_dataset, analyze_dataset, query_dataset, analyze_dataset

async def test_server_functions():
    print("Testing Utsunomiya Open Data MCP Server functions...")
    
    # Test 1: List datasets
    print("\n1. Testing list_datasets:")
    try:
        datasets = await list_datasets()
        print(f"Found {len(datasets)} datasets:")
        for ds in datasets:
            print(f"  - {ds['id']}: {ds['name']}")
    except Exception as e:
        print(f"Error in list_datasets: {e}")
    
    # Test 2: Get schema for first dataset
    print("\n2. Testing get_dataset_schema:")
    try:
        if datasets:
            dataset_id = datasets[0]['id']
            schema = await get_dataset_schema(dataset_id)
            print(f"Schema for {dataset_id}:")
            print(f"  - Total rows: {schema['total_rows']}")
            print(f"  - Number of columns: {len(schema['columns'])}")
            print(f"  - Column names: {[col['name'] for col in schema['columns']]}")
            print(f"  - Sample data: {schema['sample_data'][:2]}")  # Show first 2 samples
    except Exception as e:
        print(f"Error in get_dataset_schema: {e}")
    
    # Test 3: Query dataset
    print("\n3. Testing query_dataset:")
    try:
        if datasets:
            dataset_id = datasets[0]['id']
            data = await query_dataset(dataset_id, limit=5)
            print(f"Retrieved {len(data)} rows from {dataset_id}")
            if data:
                print(f"Sample record: {data[0]}")
    except Exception as e:
        print(f"Error in query_dataset: {e}")
    
    # Test 4: Analyze dataset
    print("\n4. Testing analyze_dataset:")
    try:
        if datasets:
            dataset_id = datasets[0]['id']
            analysis = await analyze_dataset(dataset_id)
            print(f"Analysis for {dataset_id}:")
            print(f"  - Total rows: {analysis['total_rows']}")
            print(f"  - Total columns: {analysis['total_columns']}")
            print(f"  - Numeric columns: {analysis['numeric_columns']}")
            print(f"  - Statistics: {json.dumps(analysis['statistics'], indent=2, ensure_ascii=False)[:200]}...")  # Truncate for readability
    except Exception as e:
        print(f"Error in analyze_dataset: {e}")

if __name__ == "__main__":
    asyncio.run(test_server_functions())
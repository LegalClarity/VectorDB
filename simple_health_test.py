#!/usr/bin/env python3
"""
Simple API Health Test
"""

import asyncio
import aiohttp
import json

async def test_api_health():
    """Test API health endpoints"""
    
    print("🔍 Testing API Health...")
    
    # Test analyzer API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                data = await response.json()
                print(f"✅ Analyzer API Health: {response.status} - {data}")
    except Exception as e:
        print(f"❌ Analyzer API Health: {e}")
    
    # Test main API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/health") as response:
                data = await response.json()
                print(f"✅ Main API Health: {response.status} - {data}")
    except Exception as e:
        print(f"❌ Main API Health: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_health())
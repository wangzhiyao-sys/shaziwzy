"""
Test script for MCP-PolyGame-Agent tools
Run this script to test all available tools
"""
import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_tools():
    """Test all MCP tools"""
    print("Connecting to MCP Server at http://127.0.0.1:12345...")
    
    async with sse_client(url="http://127.0.0.1:12345") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("\n" + "="*60)
            print("MCP Server Connected Successfully!")
            print("="*60)
            
            # List all tools
            tools_response = await session.list_tools()
            print(f"\nAvailable tools ({len(tools_response.tools)}):")
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n" + "="*60)
            print("Testing Tools...")
            print("="*60)
            
            # Test 1: Initialize Game
            print("\n[Test 1] Initializing game...")
            result = await session.call_tool(
                "initialize_game",
                {
                    "game_id": "test_game_001",
                    "player_ids": ["player1", "player2", "player3", "player4", "player5"],
                    "total_wolves": 2
                }
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            # Test 2: Query Game State
            print("\n[Test 2] Querying game state...")
            result = await session.call_tool(
                "query_game_state",
                {"game_id": "test_game_001"}
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            # Test 3: Record Event
            print("\n[Test 3] Recording game event...")
            result = await session.call_tool(
                "record_event",
                {
                    "round_num": 1,
                    "speaker": "player1",
                    "content": "I think player2 is suspicious",
                    "action_type": "speak",
                    "game_id": "test_game_001",
                    "target_player": "player2",
                    "relation_type": "attack"
                }
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            # Test 4: Analyze Suspicion
            print("\n[Test 4] Analyzing player suspicion...")
            result = await session.call_tool(
                "analyze_suspicion",
                {
                    "player_id": "player2",
                    "evidence_score": 0.7,
                    "evidence_type": "contradiction",
                    "description": "Contradicted previous statement",
                    "game_id": "test_game_001"
                }
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            # Test 5: Recall Memory
            print("\n[Test 5] Recalling player memory...")
            result = await session.call_tool(
                "recall_memory",
                {
                    "player_id": "player1",
                    "game_id": "test_game_001",
                    "limit": 5
                }
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            # Test 6: Get Player Relations
            print("\n[Test 6] Getting player relations...")
            result = await session.call_tool(
                "get_player_relations",
                {"player_id": "player1"}
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            # Test 7: Calculate Action Utility
            print("\n[Test 7] Calculating action utility...")
            result = await session.call_tool(
                "calculate_action_utility",
                {
                    "action_candidates": [
                        {"type": "check", "target": "player2"},
                        {"type": "check", "target": "player3"}
                    ],
                    "current_role": "seer",
                    "alive_count": 5,
                    "suspicion_scores": {
                        "player2": 0.7,
                        "player3": 0.3,
                        "player4": 0.5,
                        "player5": 0.4
                    }
                }
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            # Test 8: Detect Wolf Patterns
            print("\n[Test 8] Detecting wolf patterns...")
            result = await session.call_tool(
                "detect_wolf_patterns",
                {"threshold": 0.7}
            )
            print(f"Result: {json.dumps(result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0]), indent=2, ensure_ascii=False)}")
            
            print("\n" + "="*60)
            print("All tests completed!")
            print("="*60)


if __name__ == "__main__":
    print("Make sure the MCP Server is running on http://127.0.0.1:12345")
    print("Press Ctrl+C to stop the test\n")
    try:
        asyncio.run(test_tools())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Make sure the MCP Server is running!")

import os
import json
from google import genai

def simulate_mcp_tool_call(role: str, query_type: str) -> str:
    print(f"  [MCP Server] Received '{query_type}' request from role '{role}'")
    
    # Cedar Policy Enforcement Simulation
    if role != "gtm-agent":
        msg = f"[Cedar Policy] ACCESS DENIED: Role '{role}' lacks GTM privileges."
        print(f"  [DENIED] {msg}")
        return f"Error: {msg}"
        
    print("  [GRANTED] [Cedar Policy] Access Granted for Product & ICPSegment nodes.")
    if query_type == "get_icp_data":
        return json.dumps({
            "products": [
                {
                    "name": "Stockly",
                    "icp_segments": [
                        {
                            "industry": "Retail and Logistics",
                            "company_size": "Mid-sized ($50M - $500M)",
                            "target_personas": [
                                {
                                    "title": "Supply Chain Manager", 
                                    "pain_points": "Exhausted by manual excel sheets, high risk of stockouts during peak seasons."
                                }
                            ]
                        }
                    ]
                }
            ]
        })
    return "No data found."

def run_gtm_agent():
    print("==============================================")
    print("Starting GTM Agent (Role: gtm-agent)")
    print("==============================================\n")
    
    role = "gtm-agent"
    
    print("--- 1. Agent reading Graph Context via MCP ---")
    
    # Read ICP data (should be allowed)
    print("\nRequesting ICP segment and persona data...")
    icp_data = simulate_mcp_tool_call(role, "get_icp_data")
    
    # Generate content using Gemini
    print("\n--- 2. Generating Sales Brief via Gemini 2.5 Flash ---")
    
    prompt = f"""
    You are a GTM Strategist for Analytos. Create a short, structured prospecting brief for the product 'Stockly'.
    
    Include:
    1. Target Industry and Company Size
    2. Specific Persona to contact and their pain points
    3. An opening sales angle based on solving those pain points.
    
    Data from Graph:
    {icp_data}
    """
    
    if not os.environ.get("GEMINI_API_KEY"):
        class MockResponse:
            text = "Target Industry: Retail and Logistics\nCompany Size: Mid-sized ($50M - $500M)\nPersona: Supply Chain Manager\nPain Points: Exhausted by manual excel sheets, high risk of stockouts during peak seasons.\nAngle: Automate your stock!"
        response = MockResponse()
    else:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
    
    print("\n--- GTM Prospecting Brief Output ---")
    print(response.text)
    print("\n==============================================")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("[INFO] Running in MOCK LLM mode because GEMINI_API_KEY is not set.")
    run_gtm_agent()

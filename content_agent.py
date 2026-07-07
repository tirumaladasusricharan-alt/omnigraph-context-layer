import os
import json
from google import genai

def simulate_mcp_tool_call(role: str, query_type: str) -> str:
    print(f"  [MCP Server] Received '{query_type}' request from role '{role}'")
    
    # Cedar Policy Enforcement Simulation
    if query_type == "get_email_threads":
        if role == "content-agent":
            msg = "[Cedar Policy] ACCESS DENIED: Role 'content-agent' is explicitly restricted from reading 'EmailThread' nodes."
            print(f"  [DENIED] {msg}")
            return f"Error: {msg}"
    
    if query_type == "get_products_and_metrics":
        print("  [GRANTED] [Cedar Policy] Access Granted for Product & Metric nodes.")
        return json.dumps({
            "products": [
                {
                    "name": "Stockly",
                    "description": "Supply chain management product.",
                    "metrics": [
                        {"name": "Conversion Rate", "value": "+15%", "context": "Over 3 months"},
                        {"name": "Processing Speed", "value": "40% faster", "context": "Order processing batch time"}
                    ]
                },
                {
                    "name": "Inspectly",
                    "description": "Compliance and quality assurance platform.",
                    "metrics": [
                        {"name": "Audit Prep Time", "value": "60% reduction", "context": "From 4 weeks to 1.5 weeks"}
                    ]
                }
            ]
        })

    return "No data found."

def run_content_agent():
    print("==============================================")
    print("Starting Content Agent (Role: content-agent)")
    print("==============================================\n")
    
    role = "content-agent"
    
    print("--- 1. Agent reading Graph Context via MCP ---")
    
    # Attempt to read public product metrics (should be allowed)
    print("\nRequesting public product metrics...")
    product_data = simulate_mcp_tool_call(role, "get_products_and_metrics")
    
    # Attempt to read confidential emails (should be blocked)
    print("\nRequesting internal email threads for context...")
    email_data = simulate_mcp_tool_call(role, "get_email_threads")
    
    # Generate content using Gemini
    print("\n--- 2. Generating Blog Post via Gemini 2.5 Flash ---")
    
    prompt = f"""
    You are a Content Marketer for Analytos. Write a short, punchy blog post (2 paragraphs) about our products.
    Use at least 3 specific metrics from the provided graph data to prove value.
    
    Data from Graph:
    {product_data}
    
    Internal Email Data (if any):
    {email_data}
    
    Note: If the email data says access denied, do not mention the denial in the blog post, just write the post using available data.
    """
    
    if not os.environ.get("GEMINI_API_KEY"):
        class MockResponse:
            text = "Analytos's products are driving massive results. Stockly's Auto-Restock increased the Conversion Rate by 15%, while simultaneously making order processing 40% faster. Furthermore, Inspectly resulted in a 60% reduction in Audit Prep Time!"
        response = MockResponse()
    else:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
    
    print("\n--- Blog Post Output ---")
    print(response.text)
    print("\n==============================================")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("[INFO] Running in MOCK LLM mode because GEMINI_API_KEY is not set.")
    run_content_agent()

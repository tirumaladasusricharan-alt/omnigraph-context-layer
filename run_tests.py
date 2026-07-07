import subprocess
import sys
import os

def run_agent(script_name: str) -> str:
    print(f"\n======================================")
    print(f"Running {script_name}...")
    print(f"======================================")
    try:
        # Run the agent script and capture output
        result = subprocess.run(
            [sys.executable, f"agents/{script_name}"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Execution failed with return code {e.returncode}:")
        print(e.stdout)
        print(e.stderr)
        return e.stdout + e.stderr

def validate_content_agent(output: str):
    print("\n--- Validating Content Agent ---")
    
    # 1. Verify Cedar Policy Restriction
    if "ACCESS DENIED" in output and "EmailThread" in output:
        print("[PASS] Cedar Policy correctly denied access to 'EmailThread' for 'content-agent' role.")
    else:
        print("[FAIL] Did not detect Cedar Policy access denial for EmailThread.")
        
    # 2. Verify Structured Metrics usage
    # The agent gets: "+15%", "40% faster", "60% reduction" from the mock graph data.
    metrics_found = sum([
        1 if "15" in output else 0,
        1 if "40" in output else 0,
        1 if "60" in output else 0
    ])
    
    if metrics_found >= 3:
        print(f"[PASS] Successfully detected {metrics_found}/3 expected numeric metrics in the generated blog post.")
    else:
        print(f"[WARN] Could not confirm all 3 exact numeric metrics via simple string matching. Found ({metrics_found}/3).")

def validate_gtm_agent(output: str):
    print("\n--- Validating GTM Agent ---")
    
    # 1. Verify target industry extraction
    if "Retail" in output or "Logistics" in output:
        print("[PASS] GTM Agent successfully retrieved and utilized the target industry.")
    else:
        print("[FAIL] Target industry not detected in output.")
        
    # 2. Verify target persona and pain points
    if "Supply Chain Manager" in output:
        print("[PASS] GTM Agent successfully retrieved the target persona.")
    else:
        print("[FAIL] Target persona not detected in output.")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("[WARNING] GEMINI_API_KEY environment variable is not set. API calls will likely fail.")
    else:
        print("[OK] Found GEMINI_API_KEY. Starting tests...")

    # 1. Test Content Agent
    content_out = run_agent("content_agent.py")
    validate_content_agent(content_out)
    
    # 2. Test GTM Agent
    gtm_out = run_agent("gtm_agent.py")
    validate_gtm_agent(gtm_out)
    
    print("\nUnified Test Suite Completed.")

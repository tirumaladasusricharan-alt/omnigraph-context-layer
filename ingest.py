import os
import json
import uuid
import subprocess
from datetime import datetime
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ------------------------------------------------------------------------------
# Pydantic Schemas for Structured Output Extraction
# ------------------------------------------------------------------------------

# Entities
class Product(BaseModel):
    id: str = Field(description="Unique identifier for the product (slug format)")
    name: str = Field(description="Name of the product")
    description: str = Field(description="Short description of the product")

class Feature(BaseModel):
    id: str = Field(description="Unique identifier for the feature (slug format)")
    name: str = Field(description="Name of the feature")
    description: str = Field(description="Description of the feature")

class Metric(BaseModel):
    id: str = Field(description="Unique identifier for the metric (slug format)")
    metric_name: str = Field(description="Name or type of metric (e.g., 'Conversion Rate')")
    value: str = Field(description="The numeric value or proof point")
    context: str = Field(description="Context or timeframe for the metric")

class ICPSegment(BaseModel):
    id: str = Field(description="Unique identifier for the ICP segment (slug format)")
    industry: str = Field(description="Target industry")
    company_size: str = Field(description="Target company size or revenue")

class Persona(BaseModel):
    id: str = Field(description="Unique identifier for the persona (slug format)")
    title: str = Field(description="Job title or role of the persona")
    pain_points: str = Field(description="Primary pain points of this persona")

class EmailThread(BaseModel):
    id: str = Field(description="Unique identifier for the email thread (slug format)")
    subject: str = Field(description="Subject line of the email thread")
    body: str = Field(description="Summary or content of the email body")
    is_internal: bool = Field(description="True if the email is internal-only")

# Edges
class HasFeature(BaseModel):
    product_id: str
    feature_id: str

class ProvenBy(BaseModel):
    feature_id: str
    metric_id: str

class Targets(BaseModel):
    product_id: str
    icp_segment_id: str

class HasPersona(BaseModel):
    icp_segment_id: str
    persona_id: str

class DiscussedIn(BaseModel):
    product_id: str
    email_thread_id: str

# Master Graph Extraction Model
class GraphExtraction(BaseModel):
    products: list[Product] = []
    features: list[Feature] = []
    metrics: list[Metric] = []
    icp_segments: list[ICPSegment] = []
    personas: list[Persona] = []
    email_threads: list[EmailThread] = []
    
    has_feature_edges: list[HasFeature] = []
    proven_by_edges: list[ProvenBy] = []
    targets_edges: list[Targets] = []
    has_persona_edges: list[HasPersona] = []
    discussed_in_edges: list[DiscussedIn] = []

# ------------------------------------------------------------------------------
# Ingestion Logic
# ------------------------------------------------------------------------------

def extract_graph_from_text(text: str) -> GraphExtraction:
    """Uses Gemini 2.5 Flash to extract structured graph data from the text."""
    # Ensure API key is set
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    client = genai.Client()
    
    prompt = (
        "You are an expert data extraction assistant. "
        "Extract the products, features, metrics, ICP segments, personas, and email threads "
        "from the provided text, along with the relationships between them. "
        "Use slug format for all IDs."
    )
    
    # Configure the generation using the google-genai SDK 
    # and Pydantic for structured outputs.
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, text],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GraphExtraction,
            temperature=0.1
        )
    )
    
    # Parse the structured JSON response
    data = json.loads(response.text)
    return GraphExtraction(**data)

def simulate_omnigraph_mutations(graph_data: GraphExtraction):
    """
    Simulates sending the extracted data to Omnigraph.
    In a real scenario, this would use the Omnigraph CLI or SDK to apply idempotent mutations.
    """
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"ingest/{run_id}"
    
    print(f"[Omnigraph] Creating new branch: {branch_name}")
    # Example actual CLI call: 
    # subprocess.run(["omnigraph", "branch", "create", branch_name, "--from", "main"], check=True)
    
    print(f"[Omnigraph] Switching to branch: {branch_name}")
    
    # Process Entities (Upsert ensures idempotency by ID)
    for product in graph_data.products:
        print(f"  -> Upserting Node [Product] ID: {product.id} - {product.name}")
        # Example: omnigraph mutate upsert_product --params '{"id": "...", "name": "..."}'
        
    for feature in graph_data.features:
        print(f"  -> Upserting Node [Feature] ID: {feature.id} - {feature.name}")
        
    for metric in graph_data.metrics:
        print(f"  -> Upserting Node [Metric] ID: {metric.id} - {metric.metric_name}: {metric.value}")
        
    for icp in graph_data.icp_segments:
        print(f"  -> Upserting Node [ICPSegment] ID: {icp.id}")
        
    for persona in graph_data.personas:
        print(f"  -> Upserting Node [Persona] ID: {persona.id}")
        
    for email in graph_data.email_threads:
        print(f"  -> Upserting Node [EmailThread] ID: {email.id}")

    # Process Edges (Upsert based on source/target ensures idempotency)
    for edge in graph_data.has_feature_edges:
        print(f"  -> Upserting Edge [HAS_FEATURE] {edge.product_id} -> {edge.feature_id}")

    for edge in graph_data.proven_by_edges:
        print(f"  -> Upserting Edge [PROVEN_BY] {edge.feature_id} -> {edge.metric_id}")

    for edge in graph_data.targets_edges:
        print(f"  -> Upserting Edge [TARGETS] {edge.product_id} -> {edge.icp_segment_id}")

    for edge in graph_data.has_persona_edges:
        print(f"  -> Upserting Edge [HAS_PERSONA] {edge.icp_segment_id} -> {edge.persona_id}")

    for edge in graph_data.discussed_in_edges:
        print(f"  -> Upserting Edge [DISCUSSED_IN] {edge.product_id} -> {edge.email_thread_id}")

    print(f"[Omnigraph] Finished applying mutations to branch '{branch_name}'.")
    print(f"Review and merge with: omnigraph branch merge {branch_name} --into main")

def process_document(file_path: str):
    """Reads a document, extracts structured graph data, and pushes to Omnigraph."""
    print(f"Starting ingestion for: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        text_content = f.read()

    print("Extracting structured graph data via Gemini 2.5 Flash...")
    try:
        graph_data = extract_graph_from_text(text_content)
    except Exception as e:
        print(f"Extraction failed: {e}")
        return
        
    print("Extraction successful. Applying to graph...")
    simulate_omnigraph_mutations(graph_data)

if __name__ == "__main__":
    # Example usage: read a sample file from seed-data
    seed_file = os.path.join("seed-data", "stockly-product-overview.md")
    
    # Create a dummy file if it doesn't exist just for demonstration
    os.makedirs("seed-data", exist_ok=True)
    if not os.path.exists(seed_file):
        print(f"Creating mock seed file at {seed_file} for demonstration.")
        with open(seed_file, 'w', encoding='utf-8') as f:
            f.write("# Stockly Product Overview\n\n"
                    "Stockly is a supply chain management product. It has a feature called 'Auto-Restock' "
                    "which improved Conversion Rate by 15% over 3 months. It targets the Retail industry for "
                    "mid-sized companies, reaching Supply Chain Managers who struggle with stockouts.\n\n"
                    "From internal thread 'Pilot Results': The stockly pilot went great.")
    
    process_document(seed_file)

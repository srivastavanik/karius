import os
import json
import requests
from typing import Dict, List, Any, Optional
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# Constants
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Set page configuration
st.set_page_config(
    page_title="Karius Market Expansion AI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86C1;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #777;
        margin-top: 0px;
    }
    .answer-box {
        background-color: #f7f7f7;
        border-radius: 5px;
        padding: 20px;
        margin-top: 20px;
        border-left: 5px solid #2E86C1;
    }
    .source-box {
        background-color: #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    .metrics-box {
        background-color: #EBF5FB;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Functions for API communication
def get_stats() -> Dict[str, Any]:
    """Fetch statistics from the API."""
    try:
        response = requests.get(f"{API_URL}/stats")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching statistics: {str(e)}")
        return {"total_records": 0, "by_source": {}}

def get_filters() -> List[Dict[str, Any]]:
    """Fetch available filters from the API."""
    try:
        response = requests.get(f"{API_URL}/filters")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching filters: {str(e)}")
        return []

def query_assistant(question: str, query_type: str, metadata_filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Submit a query to the assistant API."""
    try:
        payload = {
            "question": question,
            "query_type": query_type,
            "metadata_filters": metadata_filters
        }
        response = requests.post(f"{API_URL}/query", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error querying assistant: {str(e)}")
        return {"answer": f"Error: {str(e)}", "sources": []}

def create_relationship_graph(answer: str, sources: List[Dict[str, Any]]):
    """Create a visual graph of relationships from the answer and sources."""
    # This is a simplified example - in a real implementation, you would
    # analyze the answer text to extract entities and relationships
    
    # Extract unique sources for nodes
    nodes = [Node(id="Karius", label="Karius", size=25, color="#2E86C1")]
    
    # Extract unique regions/countries from sources
    regions = set()
    partners = set()
    
    for source in sources:
        metadata = source.get("metadata", {})
        if "country" in metadata and metadata["country"]:
            regions.add(metadata["country"])
        if "partner" in metadata and metadata["partner"]:
            partners.add(metadata["partner"])
    
    # Add region nodes
    for region in regions:
        nodes.append(Node(id=region, label=region, size=15, color="#5DADE2"))
    
    # Add partner nodes
    for partner in partners:
        nodes.append(Node(id=partner, label=partner, size=20, color="#58D68D"))
    
    # Create edges (connections)
    edges = []
    
    # Connect Karius to all regions
    for region in regions:
        edges.append(Edge(source="Karius", target=region, type="SOLID"))
    
    # Connect Karius to all partners
    for partner in partners:
        edges.append(Edge(source="Karius", target=partner, type="DASHED"))
    
    # Graph configuration
    config = Config(
        width=750,
        height=500,
        directed=True,
        physics=True,
        hierarchical=False,
    )
    
    return nodes, edges, config

# Page Header
st.markdown("<h1 class='main-header'>Karius Market Expansion AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>AI-Driven Market Expansion & Partner Discovery Tool</p>", unsafe_allow_html=True)

# Sidebar with statistics and filters
with st.sidebar:
    st.header("Data Overview")
    
    # Get and display statistics
    stats = get_stats()
    st.metric("Total Records", stats.get("total_records", 0))
    
    # Display source breakdown
    st.subheader("Data Sources")
    source_stats = stats.get("by_source", {})
    for source, count in source_stats.items():
        st.text(f"{source}: {count} records")
    
    # Metadata filters
    st.header("Filters")
    
    filter_options = get_filters()
    selected_filters = {}
    
    for filter_option in filter_options:
        field = filter_option.get("field", "")
        values = filter_option.get("values", [])
        
        if field and values:
            st.subheader(field.capitalize())
            selected_value = st.selectbox(f"Select {field}", ["Any"] + values)
            
            if selected_value != "Any":
                selected_filters[field] = selected_value
    
    # Query type selection
    st.header("Query Type")
    query_type = st.radio(
        "Select Analysis Type",
        ["Market Expansion", "Partner Discovery"],
        index=0,
    )
    
    query_type_value = "market" if query_type == "Market Expansion" else "partner"

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    # Input area
    st.subheader("Ask the AI Assistant")
    
    # Example questions
    st.markdown("### Example Questions:")
    
    example_questions = {
        "market": [
            "Which regions have the highest prevalence of infectious diseases?",
            "What are the emerging diagnostic markets in Southeast Asia?",
            "How does healthcare spending in Europe correlate with diagnostic adoption?",
        ],
        "partner": [
            "Which hospital networks have the most comprehensive infectious disease programs?",
            "What research institutions are leaders in microbiology diagnostics?",
            "Which distributors have the strongest presence in Latin America?",
        ]
    }
    
    for q in example_questions[query_type_value]:
        if st.button(q):
            st.session_state.question = q
    
    # Text input for question
    question = st.text_area(
        "Enter your question:",
        value=st.session_state.get("question", ""),
        height=100,
        key="question_input",
    )
    
    # Submit button
    if st.button("Submit", type="primary"):
        if question:
            with st.spinner("Analyzing data and generating answer..."):
                # Process filters
                metadata_filters = selected_filters if selected_filters else None
                
                # Query the API
                result = query_assistant(question, query_type_value, metadata_filters)
                
                # Store in session state
                st.session_state.last_result = result
                st.session_state.question = question
        else:
            st.warning("Please enter a question.")
    
    # Display answer if available
    if "last_result" in st.session_state:
        answer = st.session_state.last_result.get("answer", "")
        sources = st.session_state.last_result.get("sources", [])
        
        st.markdown("### Answer:")
        st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
        
        # Display sources (collapsible)
        with st.expander("View Sources", expanded=False):
            for i, source in enumerate(sources):
                st.markdown(f"**Source {i+1}**: {source.get('source', 'Unknown')}")
                st.markdown(f"<div class='source-box'>{source.get('content', '')}</div>", unsafe_allow_html=True)
                st.markdown("---")

with col2:
    # Visualization area
    st.subheader("Relationship Visualization")
    
    if "last_result" in st.session_state:
        answer = st.session_state.last_result.get("answer", "")
        sources = st.session_state.last_result.get("sources", [])
        
        # Create relationship graph
        nodes, edges, config = create_relationship_graph(answer, sources)
        
        # Display graph
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.info("Submit a question to see relationship visualizations.")
    
    # Key metrics and insights area
    st.subheader("Key Metrics")
    
    # Example metrics (in a real application, these would be derived from the data)
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Growth Potential", "+24%", delta="+4%")
        st.metric("Market Size", "$1.2B", delta="+8%")
    with col_b:
        st.metric("Competitive Index", "0.72", delta="-0.05")
        st.metric("Adoption Rate", "18%", delta="+2%")
    
    # Additional insights
    st.markdown("<div class='metrics-box'>", unsafe_allow_html=True)
    st.markdown("### Regional Insights")
    st.markdown("- North America: High adoption, strong reimbursement")
    st.markdown("- Europe: Diverse regulations, growing research focus")
    st.markdown("- Asia: Rapid growth in China, emerging opportunities in India")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("© 2023 Karius, Inc. | AI-Driven Market Expansion Tool") 
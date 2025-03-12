import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from neo4j import GraphDatabase



# Neo4j connection details
NEO4J_URI = "bolt://localhost:7689"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "gcKSdlYTISt1WIhK4Thh7E08bY1JW08RMmUqHFWSfM8"



# Function to connect to Neo4j and run a query
def run_neo4j_query(query):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        result = session.run(query)
        return [record for record in result]

# Function to get response from LLama 2 model
def getLLamaresponse(input_text, no_words, style):
  
    llm = CTransformers(
        model='models/llama-2-7b-chat.ggmlv3.q8_0.bin',
        model_type='llama',
        config={'max_new_tokens': 256, 'temperature': 0.01}
    )

    ## Prompt Template
    template = """
        Answer a query in {style} about {input_text}
        within {no_words} words.
    """
    prompt = PromptTemplate(
        input_variables=["style", "input_text", "no_words"],
        template=template
    )

    ## Generate the response from the LLama 2 model
    response = llm(prompt.format(style=style, input_text=input_text, no_words=no_words))
    print(response)
    return response

# Function to detect if the input is a Cypher query
def is_cypher_query(input_text):
    # Check if the input starts with a Cypher keyword
    cypher_keywords = [
        "MATCH", "RETURN", "CREATE", "DELETE", "SET", "WITH", "UNWIND", "MERGE", "CALL"
    ]
    return any(input_text.strip().upper().startswith(keyword) for keyword in cypher_keywords)

# Function to convert a natural language question to a Cypher query
def convert_to_cypher(question):
    # Simple mapping of natural language questions to Cypher queries
    if "proteins are part of the" in question.lower() and "pathway" in question.lower():
        pathway = question.split('"')[1]  # Extract the pathway name from the question
        return f"""
        MATCH (p:protein)-[:part_of]->(pw:pathway {{pathway_name: "{pathway}"}})
        RETURN p.protein_name AS protein_name
        """
    else:
        return None

# Streamlit app configuration
st.set_page_config(
    page_title="Neo4j Query and LLama 2 Response",
    page_icon='🤖',
    layout='centered',
    initial_sidebar_state='collapsed'
)

st.header("Neo4j Query and LLama 2 Response 🤖")

# Input fields
input_text = st.text_input("Enter your query or question")

col1, col2 = st.columns([5, 5])

with col1:
    no_words = st.text_input('No of Words')
with col2:
    style = st.selectbox('Response Style', ('Text', 'Cypher', 'Both'), index=0)

submit = st.button("Generate")


query1 = """
MATCH (t:transcript)-[:translates_to]->(pr:protein)
RETURN t.transcript_name AS transcript_name, pr.protein_name AS protein_name
"""
query2 = """
MATCH (e:enhancer)-[:associated_with]->(g:gene)
RETURN e.enhancer_id AS enhancer_id, g.gene_name AS gene_name
"""
query3 = """
MATCH (s:snp)
WHERE s.chr = "chr1"
RETURN s.id AS snp_id, s.ref AS ref, s.alt AS alt
"""

# Display predefined query options
st.sidebar.header("Predefined Neo4j Queries")
query_option = st.sidebar.selectbox(
    "Choose a predefined query",
    ("Transcripts Translated to Proteins", "Enhancers Associated with Genes", "SNPs in a Specific Chromosome")
)

# Run the selected predefined query
if st.sidebar.button("Run Predefined Query"):
    if query_option == "Transcripts Translated to Proteins":
        query = query1
    elif query_option == "Enhancers Associated with Genes":
        query = query2
    elif query_option == "SNPs in a Specific Chromosome":
        query = query3
    try:
        query_result = run_neo4j_query(query)
        st.write("### Predefined Query Result:")
        st.write(query_result)
    except Exception as e:
        st.error(f"Error running predefined query: {e}")

# Final response for user input
if submit:

    if style == "Text" or style == "Both":
        # Generate a text response using LLama 2
        st.write("### LLama 2 Response:")
        st.write(getLLamaresponse(input_text, no_words, style))
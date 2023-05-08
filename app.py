import streamlit as st
import openai
import pinecone
import os


# Check if environment variables are present. If not, throw an error
if os.getenv('PINECONE_API_KEY') is None:
    st.error("PINECONE_API_KEY not set. Please set this environment variable and restart the app.")
if os.getenv('PINECONE_ENVIRONMENT') is None:
    st.error("PINECONE_ENVIRONMENT not set. Please set this environment variable and restart the app.")
if os.getenv('PINECONE_INDEX') is None:
    st.error("PINECONE_INDEX not set. Please set this environment variable and restart the app.")
if os.getenv('AZURE_OPENAI_APIKEY') is None:
    st.error("AZURE_OPENAI_APIKEY not set. Please set this environment variable and restart the app.")
if os.getenv('AZURE_OPENAI_BASE_URI') is None:
    st.error("AZURE_OPENAI_BASE_URI not set. Please set this environment variable and restart the app.")
if os.getenv('AZURE_OPENAI_EMBEDDINGS_MODEL_NAME') is None:
    st.error("AZURE_OPENAI_EMBEDDINGS_MODEL_NAME not set. Please set this environment variable and restart the app.")
if os.getenv('AZURE_OPENAI_GPT4_MODEL_NAME') is None:
    st.error("AZURE_OPENAI_GPT4_MODEL_NAME not set. Please set this environment variable and restart the app.")


st.title("Q&A App 🔎")
query = st.text_input("What do you want to know?")

if st.button("Search"):
   
    # # get Pinecone API environment variables
    pinecone_api = os.getenv('PINECONE_API_KEY')
    pinecone_env = os.getenv('PINECONE_ENVIRONMENT')
    pinecone_index = os.getenv('PINECONE_INDEX')
    
    # # get Azure OpenAI environment variables
    openai.api_key = os.getenv('AZURE_OPENAI_APIKEY')
    openai.api_base = os.getenv('AZURE_OPENAI_BASE_URI')
    openai.api_type = 'azure'
    openai.api_version = '2023-03-15-preview'
    embeddings_model_name = os.getenv('AZURE_OPENAI_EMBEDDINGS_MODEL_NAME')
    gpt4_model_name = os.getenv('AZURE_OPENAI_GPT4_MODEL_NAME')
 
    # Initialize Pinecone client and set index
    pinecone.init(api_key=pinecone_api, environment=pinecone_env)
    index = pinecone.Index(pinecone_index)
 
    # Convert your query into a vector using Azure OpenAI
    try:
        query_vector = openai.Embedding.create(
            input=query,
            engine=embeddings_model_name,
        )["data"][0]["embedding"]
    except Exception as e:
        st.error(f"Error calling OpenAI Embedding API: {e}")
        st.stop()
 
    # Search for the most similar vectors in Pinecone
    search_response = index.query(
        top_k=3,
        vector=query_vector,
        include_metadata=True)

    chunks = [item["metadata"]['text'] for item in search_response['matches']]
 
    # Combine texts into a single chunk to insert in the prompt
    joined_chunks = "\n".join(chunks)

    # Write the selected chunks into the UI
    with st.expander("Chunks"):
        for i, t in enumerate(chunks):
            t = t.replace("\n", " ")
            st.write("Chunk ", i, " - ", t)
    
    with st.spinner("Summarizing..."):
        try:
            # Build the prompt
            prompt = f"""
            Answer the following question based on the context below.
            If you don't know the answer, just say that you don't know. Don't try to make up an answer. Do not answer beyond this context.
            ---
            QUESTION: {query}                                            
            ---
            CONTEXT:
            {joined_chunks}
            """
 
            # Run chat completion using GPT-4
            response = openai.ChatCompletion.create(
                engine=gpt4_model_name,
                messages=[
                    { "role": "system", "content":  "You are a Q&A assistant." },
                    { "role": "user", "content": prompt }
                ],
                temperature=0.7,
                max_tokens=1000
            )
 
            # Write query answer
            st.markdown("### Answer:")
            st.write(response.choices[0]['message']['content'])
   
   
        except Exception as e:
            st.error(f"Error with OpenAI Chat Completion: {e}")
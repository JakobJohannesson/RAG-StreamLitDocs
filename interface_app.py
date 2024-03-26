import streamlit as st
from document_processor import DocumentProcessor
from openai_ import OpenAIModel
from vector_store_manager import ChromaDBStorage
from text_chunker import TextChunker


st.set_page_config(layout='wide', initial_sidebar_state='expanded')


def main():

    # with st.sidebar:
        # st.image('icons8-pdf-100.png', width=100)  
        # st.header('PDOC')

#      st.title('Document Query Application')
#      st.markdown(
# """
#   This application enhances your documents by extracting text,
#   generating embeddings, and creating augmented text based on the content.
# """
#                 )


    # Sidebar
    st.sidebar.title("Settings")
    uploaded_files = st.sidebar.file_uploader("Upload Documents", type=['pdf', 'docx'], accept_multiple_files=True)
    openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

    # Main content area
    st.sidebar.markdown("---")
    user_query = st.sidebar.text_input("Enter your query:", max_chars=300)
    
    if not uploaded_files or not openai_api_key:
        st.warning("Please upload documents and enter your OpenAI API Key.")
        st.stop()

    process_button = st.sidebar.button('Process Documents')
    vector_store_manager = ChromaDBStorage()
    rag_handler = OpenAIModel(api_key=openai_api_key)     

    if process_button:
        with st.spinner("Processing documents..."):
            for uploaded_file in uploaded_files:
                if uploaded_file is not None:
                    text = DocumentProcessor.get_text(uploaded_file)
                    text_chunker = TextChunker()
                    chunks = text_chunker.chunk_text(text)
                    for chunk in chunks:
                        embedding = rag_handler.create_embedding(chunk)
                        vector_store_manager.store_embedding(uploaded_file.name, embedding)

        st.sidebar.success("Documents processed and embeddings stored.")

    if user_query:
        with st.spinner("Querying..."):
            query_embedding = rag_handler.create_embedding(user_query)
            similar_embeddings = vector_store_manager.query_embedding(query_embedding, n_results=5)
            context_texts = [result['text'] for result in similar_embeddings]
            context = " ".join(context_texts)
            answer = rag_handler.generate_augmented_text(user_query, context=context) 
        st.write('Answer', answer)

if __name__ == "__main__":
    main()

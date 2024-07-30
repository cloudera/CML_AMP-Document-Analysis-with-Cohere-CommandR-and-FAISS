from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings, ChatCohere
import json
import PyPDF2
import streamlit as st
import os
from dotenv import load_dotenv
    
st.set_page_config("Chatbot | Cohere","💬")

load_dotenv()

# API Keys
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

# Use Cohere embed-english-v3.0 embedding model
embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-v3.0")

# For Cohere Command-R LLM
llm = ChatCohere(temperature=0, cohere_api_key=COHERE_API_KEY, model="command-r")


def read_pdf(files):
    file_content = ""
    for file in files:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            file_content += page.extract_text()
    return file_content


def display_chat():
    for i in st.session_state.conversation:
        user_msg = st.chat_message("human", avatar="😄")
        user_msg.write(i[0])
        computer_msg = st.chat_message("ai", avatar="🤖")
        computer_msg.write(i[1])


def get_retriever(chunks_to_retrieve=5):
    return st.session_state.book_docsearch.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": chunks_to_retrieve}
    )


def get_answer(prompt):
    retriever = get_retriever()
    qa = RetrievalQA.from_llm(llm=llm, retriever=retriever, verbose=True)
    return qa({"query": prompt})["result"]


def show_chunks_with_score(prompt, chunks_to_retrieve=5):
    doc_score = st.session_state.book_docsearch.similarity_search_with_score(prompt, k=chunks_to_retrieve)
    with st.popover("See chunks..."):
        st.write(doc_score)


def chatbot():
    st.subheader("Ask questions from the loaded PDFs")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.book_docsearch:
        prompt = st.chat_input("Say something")
        display_chat()
        if prompt:
            user_text = prompt
            user_msg = st.chat_message("human", avatar="😄")
            user_msg.write(user_text)
            with st.spinner("Getting Answer..."):
                answer = get_answer(prompt)
                computer_msg = st.chat_message("ai", avatar="✨")
                computer_msg.write(answer)
                show_chunks_with_score(prompt)
                st.session_state.conversation.append((prompt, answer))
    else:
        st.warning("Please upload a file")


def initialize_session_state(flag=False):
    path = "/home/cdsw/faiss_db"
    if 'existing_indices' not in st.session_state or flag:
        st.session_state.existing_indices = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    if 'selected_option' not in st.session_state or flag:
        st.session_state.selected_option = st.session_state.existing_indices[0] if st.session_state.existing_indices else None
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'book_docsearch' not in st.session_state:
        st.session_state.book_docsearch = None


def load_selected_index():
    if st.session_state.selected_option:
        index_path = f"/home/cdsw/faiss_db/{st.session_state.selected_option}"
        st.session_state.book_docsearch = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)


def main():
    initialize_session_state(True)
    st.title("💬 Cohere PDF Chatbot")
    st.page_link("pages/upload_files.py", label="Upload Files", icon="⬆️")
    file_list = [",".join(json.load(open(f"/home/cdsw/faiss_db/{index}/desc.json"))["file_names"]) for index in st.session_state.existing_indices]
    with st.popover("Select index", help="👉 Select the datastore from which data will be retrieved"):
        st.session_state.selected_option = st.radio("Select a Document...", st.session_state.existing_indices, captions=file_list, index=0)
    st.write(f"*Selected index* : **{st.session_state.selected_option}**")
    load_selected_index()
    if st.session_state.selected_option:
        chatbot()
    else:
        st.warning("No index present! Please add a new index.")
        st.page_link("pages/upload_files.py", label="Upload Files", icon="⬆️")

main()

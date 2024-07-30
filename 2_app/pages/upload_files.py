import os
import time
import json
import shutil
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
import PyPDF2
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_cohere import CohereEmbeddings

st.set_page_config("Upload Files | Cohere", "⬆️")

load_dotenv()
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-v3.0")

recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=20
)

def read_pdf(files):
    file_content = ""
    for file in files:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            file_content += page.extract_text()
    return file_content

def update_description(index_option, file_names):
    with open(f'/home/cdsw/faiss_db/{index_option}/desc.json', 'r') as openfile:
        description = json.load(openfile)
        description["file_names"] = file_names + description["file_names"]
    with open(f"/home/cdsw/faiss_db/{index_option}/desc.json", "w") as outfile:
        json.dump(description, outfile)
    return description

def process_files(uploaded_file):
    file_content = read_pdf(uploaded_file)
    book_documents = recursive_text_splitter.create_documents([file_content])
    book_documents = [Document(page_content=text.page_content.replace("\n", " ").replace(".", "").replace("-", "")) for text in book_documents]
    return book_documents

def merge_and_store_documents(index_option, book_documents):
    new_docsearch = FAISS.from_documents(book_documents, embeddings)
    old_docsearch = FAISS.load_local(f"/home/cdsw/faiss_db/{index_option}", embeddings, allow_dangerous_deserialization=True)
    new_docsearch.merge_from(old_docsearch)
    new_docsearch.save_local(f"/home/cdsw/faiss_db/{index_option}")

def create_new_index(index_option, book_documents, file_names):
    os.makedirs(f"/home/cdsw/faiss_db/{index_option}", exist_ok=True)
    docsearch = FAISS.from_documents(book_documents, embeddings)
    docsearch.save_local(f"/home/cdsw/faiss_db/{index_option}")
    description = {
        "name": index_option,
        "about": "",
        "file_names": file_names
    }
    with open(f"/home/cdsw/faiss_db/{index_option}/desc.json", "w") as f:
        json.dump(description, f)
    return description

def store_index(uploaded_file, index_option, file_names):
    if os.path.exists(f"/home/cdsw/faiss_db/{index_option}/index.faiss"):
        st.toast(f"Storing in **existing index** :green[**{index_option}**]...", icon="🗂️")
        description = update_description(index_option, file_names)
        with st.spinner("Processing..."):
            book_documents = process_files(uploaded_file)
            merge_and_store_documents(index_option, book_documents)
    else:
        st.toast(f"Storing in **new index** :green[**{index_option}**]...", icon="🗂️")
        with st.spinner("Processing..."):
            book_documents = process_files(uploaded_file)
            description = create_new_index(index_option, book_documents, file_names)
    st.success(f"Successfully added to **{description['name']}**!")

def initialize_indices(flag=False):
    path = "/home/cdsw/faiss_db"
    if 'existing_indices' not in st.session_state or flag:
        st.session_state.existing_indices = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

def display_stored_indices():
    st.subheader("💽 Stored Indices", help="💽 See all the indices you have previously stored.")
    with st.expander("🗂️ See existing indices"):
        st.divider()
        if not st.session_state.existing_indices:
            st.warning("No existing indices. Please upload a PDF to start.")
        for index in st.session_state.existing_indices:
            if os.path.exists(f"/home/cdsw/faiss_db/{index}/desc.json"):
                col1, col2 = st.columns([6, 1], gap="large")
                with col1:
                    with open(f"/home/cdsw/faiss_db/{index}/desc.json", "r") as openfile:
                        description = json.load(openfile)
                        file_list = ",".join(description["file_names"])
                        st.markdown(f"<h4>{index}</h4>", unsafe_allow_html=True)
                        st.caption(f"***Desc :*** {description['about']}")
                        st.caption(f"***Files :*** {file_list}")
                with col2:
                    if st.button("🗑️", key=index, help="❌ :red[Clicking on this will delete this index]"):
                        shutil.rmtree(f"/home/cdsw/faiss_db/{index}")
                        initialize_indices(flag=True)
                        st.toast(f"**{index}** :red[deleted]", icon='🗑️')
                        time.sleep(1)
                        # Trigger a rerun without experimental features
                        st.rerun()

def main():
    initialize_indices()
    st.title("⬆️ Upload new files")
    uploaded_file = st.file_uploader("&nbsp;Upload PDF", type="pdf", accept_multiple_files=True, help="Upload PDF files to store")
    
    if uploaded_file:
        file_names = [file.name for file in uploaded_file]
        st.subheader("Select Index")
        st.caption("Create and select a new index or use an existing one")
        with st.popover("➕ Create new index"):
            form = st.form("new_index")
            index_name = form.text_input("Enter Index Name*")
            about = form.text_area("Enter description for Index")
            if form.form_submit_button("Submit", type="primary"):
                os.makedirs(f"/home/cdsw/faiss_db/{index_name}", exist_ok=True)
                description = {"name": index_name, "about": about, "file_names": []}
                with open(f"/home/cdsw/faiss_db/{index_name}/desc.json", "w") as f:
                    json.dump(description, f)
                st.session_state.existing_indices = [index_name] + st.session_state.existing_indices
                st.success(f"New Index **{index_name}** created successfully")
        index_option = st.selectbox('Add to existing Indices', st.session_state.existing_indices)
        if st.button("Store", type="primary"):
            store_index(uploaded_file, index_option, file_names)
    
    display_stored_indices()

main()

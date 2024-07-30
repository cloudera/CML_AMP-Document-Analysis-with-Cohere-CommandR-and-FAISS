import os
import json
import shutil
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_cohere import CohereEmbeddings

def read_pdf(files):
    file_content = ""
    for file in files:
        # Create a PDF file reader object
        pdf_reader = PyPDF2.PdfReader(file)
        # Get the total number of pages in the PDF
        num_pages = len(pdf_reader.pages)
        # Iterate through each page and extract text
        for page_num in range(num_pages):
            # Get the page object
            page = pdf_reader.pages[page_num]
            file_content += page.extract_text()
    return file_content

def store_index(uploaded_files, index_option, file_names):
    # If index exists
    if os.path.exists(f"/home/cdsw/faiss_db/{index_option}/index.faiss"):
        # Opening JSON file
        with open(f'/home/cdsw/faiss_db/{index_option}/desc.json', 'r') as openfile:
            description = json.load(openfile)
            description["file_names"] = file_names + description["file_names"]

        # Read the pdf file
        file_content = read_pdf(uploaded_files)
        # Create document chunks
        book_documents = recursive_text_splitter.create_documents([file_content])
        # Limit the no of characters
        book_documents = [Document(page_content=text.page_content.replace("\n", " ").replace(".", "").replace("-", "")) for text in book_documents]
        docsearch = FAISS.from_documents(book_documents, embeddings)
        old_docsearch = FAISS.load_local(f"/home/cdsw/faiss_db/{index_option}", embeddings, allow_dangerous_deserialization=True)
        docsearch.merge_from(old_docsearch)
        docsearch.save_local(f"/home/cdsw/faiss_db/{index_option}")
        # Write the json file
        with open(f"/home/cdsw/faiss_db/{index_option}/desc.json", "w") as outfile:
            json.dump(description, outfile)
    else:
        os.makedirs(f"/home/cdsw/faiss_db/{index_option}", exist_ok=True)

        description = {
            "name": index_option,
            "about": "Index created via CLI",
            "file_names": file_names
        }

        # Read the pdf file
        file_content = read_pdf(uploaded_files)
        # Create document chunks
        book_documents = recursive_text_splitter.create_documents([file_content])
        # Limit the no of characters, remove \n
        book_documents = [Document(page_content=text.page_content.replace("\n", " ").replace(".", "").replace("-", "")) for text in book_documents]
        docsearch = FAISS.from_documents(book_documents, embeddings)

        docsearch.save_local(f"/home/cdsw/faiss_db/{index_option}")
        # Write the json file
        with open(f"/home/cdsw/faiss_db/{index_option}/desc.json", "w") as outfile:
            json.dump(description, outfile)

def initial():
    path = "/home/cdsw/faiss_db"
    existing_indices = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    return existing_indices

def find_pdfs(root_dir):
    pdf_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def main():
    pdf_files = find_pdfs("/home/cdsw/docs")
    if not pdf_files:
        print("No PDF files found in /home/cdsw/docs")
        return

    existing_indices = initial()
    index_option = "Default Index"  # Name of the default index

    if index_option not in existing_indices:
        os.makedirs(f"/home/cdsw/faiss_db/{index_option}", exist_ok=True)
        description = {
            "name": index_option,
            "about": "Default index for storing PDF files",
            "file_names": []
        }
        with open(f"/home/cdsw/faiss_db/{index_option}/desc.json", "w") as f:
            json.dump(description, f)

    with open(f"/home/cdsw/faiss_db/{index_option}/desc.json", "r") as f:
        description = json.load(f)

    new_files = [file for file in pdf_files if os.path.basename(file) not in description["file_names"]]
    
    if not new_files:
        print("All PDF files are already indexed.")
        return

    store_index(new_files, index_option, [os.path.basename(file) for file in new_files])
    print(f"Successfully added to index: {index_option}")

if __name__ == "__main__":
    load_dotenv()
    COHERE_API_KEY = os.getenv('COHERE_API_KEY')
    embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-v3.0")

    recursive_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=20)

    main()

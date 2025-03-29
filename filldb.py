from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

# setting the environment
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="youtube_summaries")

# loading the document
loader = PyPDFDirectoryLoader(DATA_PATH)
raw_documents = loader.load()

# splitting the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

# Get existing IDs to prevent overwriting
existing_data = collection.get()
existing_ids = set(existing_data["ids"]) if existing_data["ids"] else set()

# preparing to be added in chromadb
documents = []
metadata = []
ids = []

# Start ID numbering after the last existing ID
i = len(existing_ids)

for chunk in chunks:
    new_id = "ID" + str(i)

    # Avoid ID duplication
    while new_id in existing_ids:
        i += 1
        new_id = "ID" + str(i)

    documents.append(chunk.page_content)
    ids.append(new_id)
    metadata.append(chunk.metadata)

    i += 1

# adding to chromadb
collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)

print(f"Added {len(documents)} new documents to ChromaDB.")
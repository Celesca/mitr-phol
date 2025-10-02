import os
import unicodedata
import pandas as pd
from tqdm.auto import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PDFPlumberLoader, UnstructuredPDFLoader

def is_scanned_pdf(filepath: str, min_chars: int = 30) -> bool:
    """Check if a PDF is scanned by trying to extract text from the first page."""
    try:
        loader = PDFPlumberLoader(filepath)
        docs = loader.load()
        if not docs:
            return True
        sample_text = docs[0].page_content.strip()
        # If text is too short or mostly non-Thai, assume scanned
        if len(sample_text) < min_chars:
            return True
        return False
    except Exception:
        return True

# -----------------------------
# Load metadata
# -----------------------------
df = pd.read_csv("metadata.csv")
df["category_list"] = df["category"].apply(lambda x: [c.strip() for c in str(x).split(",")])
df["filename"] = df["filename"].str.strip().str.lower()

# -----------------------------
# Process PDFs
# -----------------------------
pdf_dir = "./sugar_data"
all_chunks = []
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)

for file in tqdm(os.listdir(pdf_dir), desc="Loading PDFs"):
    if file.endswith(".pdf"):
        filepath = os.path.join(pdf_dir, file)
        try:
            if is_scanned_pdf(filepath):
                print(f"📷 Using OCR for scanned PDF: {file}")
                loader = UnstructuredPDFLoader(filepath, mode="elements", strategy="ocr_only")
            else:
                print(f"📄 Using text extraction for: {file}")
                loader = PDFPlumberLoader(filepath)

            docs = loader.load()
            chunks = splitter.split_documents(docs)

            # Normalize Thai text
            for chunk in chunks:
                chunk.page_content = unicodedata.normalize("NFC", chunk.page_content)

            # Metadata lookup
            file_clean = file.strip().lower()
            matches = df[df["filename"] == file_clean]
            if matches.empty:
                print(f"⚠️ No metadata found for {file}, skipping metadata assignment.")
                categories, source = [], None
            else:
                row = matches.iloc[0]
                categories = row["category_list"]
                source = row["source"]

            for chunk in chunks:
                chunk.metadata["filename"] = file
                chunk.metadata["category"] = categories
                chunk.metadata["source"] = source

            all_chunks.extend(chunks)

        except Exception as e:
            print(f"Error loading {file}: {e}")

print(f"✅ Total chunks created: {len(all_chunks)}")

# -----------------------------
# Build FAISS index
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)
db = FAISS.from_documents(all_chunks, embeddings)
db.save_local("faiss_index")
print("✅ FAISS index saved to 'faiss_index'.")

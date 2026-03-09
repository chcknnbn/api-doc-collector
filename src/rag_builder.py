import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_rag(docs_dir: str):
    """
    Builds a vector database from the scraped markdown files.
    """
    print(f"[rag_builder] Processing markdown files in {docs_dir} to Vector DB...")
    
    if not os.path.exists(docs_dir):
        print("[rag_builder] Docs directory does not exist.")
        return
        
    try:
        # Load documents
        loader = DirectoryLoader(docs_dir, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()
        if not docs:
            print("[rag_builder] No documents found to index.")
            return
            
        print(f"[rag_builder] Loaded {len(docs)} documents. Splitting text...")
        
        # Split by Markdown Headers to keep API context together
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_splits = []
        for doc in docs:
            splits = markdown_splitter.split_text(doc.page_content)
            # Carry over original metadata (like filename)
            for split in splits:
                split.metadata["source"] = doc.metadata.get("source", "unknown")
            md_splits.extend(splits)
            
        # Further split if chunks are too large
        char_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        final_splits = char_splitter.split_documents(md_splits)
        
        print(f"[rag_builder] Created {len(final_splits)} chunks. Generating embeddings...")
        
        # Free embedded model since we want this to work without paid APIs
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Create Chroma instance
        chroma_dir = "./rag_db"
        Chroma.from_documents(documents=final_splits, embedding=embeddings, persist_directory=chroma_dir)
        
        print(f"[rag_builder] Successfully built Chroma RAG Database at {chroma_dir}!")
        
    except Exception as e:
        print(f"[rag_builder] Failed to build RAG vector store: {e}")


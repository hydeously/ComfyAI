import os
import glob
import logging
from sentence_transformers import SentenceTransformer
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class VectorDBManager:
    def __init__(self, vault_path, exclude_folders=None, auto_index=True):
        self.vault_path = vault_path
        self.exclude_folders = exclude_folders or ["inbox", "diary"]
        self.embedding_model_name = 'all-MiniLM-L6-v2'
        self.embedding_model = None
        self.client = None
        self.collection = None
        self.persist_directory = ".chromadb"
        self._init_embedding_model()
        self._init_chromadb_client()
        if auto_index:
            self.index_vault()

    def _init_embedding_model(self):
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logging.info(f"Loaded embedding model '{self.embedding_model_name}'")
        except Exception as e:
            logging.error(f"Failed to load embedding model '{self.embedding_model_name}': {e}")
            raise

    def _init_chromadb_client(self):
        try:
            if not os.path.exists(self.persist_directory):
                os.makedirs(self.persist_directory)
                logging.debug(f"Created ChromaDB persist directory at {self.persist_directory}")
            self.client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=self.persist_directory))
            self.collection = self.client.get_or_create_collection(
                name="comfyai_knowledge",
                embedding_function=self.embedding_model.encode
            )
            logging.info("Initialized ChromaDB client and collection 'comfyai_knowledge'")
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise

    def _is_excluded(self, filepath):
        for excl in self.exclude_folders:
            if f"/{excl}/" in filepath.replace("\\", "/"):
                return True
        return False

    def _load_md_files(self):
        pattern = os.path.join(self.vault_path, "**/*.md")
        files = glob.glob(pattern, recursive=True)
        files = [f for f in files if not self._is_excluded(f)]
        logging.info(f"Found {len(files)} markdown files (excluding {self.exclude_folders})")
        return files

    def _chunk_text(self, text, max_chunk_size=500):
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) < max_chunk_size:
                current_chunk += p + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = p + "\n\n"
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def index_vault(self):
        logging.info("Starting vault indexing...")
        files = self._load_md_files()
        total_chunks = 0
        errors = 0
        try:
            for filepath in files:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()
                    chunks = self._chunk_text(text)
                    metadata = {"source": os.path.relpath(filepath, self.vault_path)}
                    for i, chunk in enumerate(chunks):
                        doc_id = f"{metadata['source']}_chunk_{i}"
                        self.collection.add(
                            documents=[chunk],
                            metadatas=[metadata],
                            ids=[doc_id]
                        )
                        total_chunks += 1
                except Exception as e:
                    errors += 1
                    logging.error(f"Failed to index {filepath}: {e}")
            self.client.persist()  # save changes to disk
            logging.info(f"Vault indexing completed: {total_chunks} chunks indexed, {errors} errors.")
        except Exception as e:
            logging.error(f"Critical error during vault indexing: {e}")

    def query(self, query_text, top_k=5):
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            return results['documents'][0]  # list of chunks
        except Exception as e:
            logging.error(f"Query failed: {e}")
            return []
import fitz  # PyMuPDF
import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_pdf_paragraph_chunks_with_metadata(pdf_path, max_chunk_size=1000):
    """Extract paragraph-level text chunks from a PDF with metadata."""
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            logger.error("PDF is empty or invalid")
            raise ValueError("PDF is empty or invalid")
        
        chunks = []
        for page_num, page in enumerate(doc, start=1):
            blocks = page.get_text("blocks")  # paragraph-level chunks
            for block in blocks:
                text = block[4].strip()
                if not text:
                    continue
                # Split large blocks into smaller chunks
                while len(text) > max_chunk_size:
                    chunks.append({"text": text[:max_chunk_size], "page": page_num})
                    text = text[max_chunk_size:]
                if text:
                    chunks.append({"text": text, "page": page_num})
        logger.info(f"Extracted {len(chunks)} chunks from {pdf_path}")
        return chunks
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        raise

def build_faiss_index(chunks, embed_model_name="all-MiniLM-L6-v2"):
    """Build and return FAISS index with embedded chunks."""
    try:
        model = SentenceTransformer(embed_model_name)
        texts = [chunk["text"] for chunk in chunks]
        logger.info(f"Embedding {len(texts)} chunks...")
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        logger.info("FAISS index built successfully")
        return index, chunks
    except Exception as e:
        logger.error(f"Error building FAISS index: {e}")
        raise

def main(): 
    parser = argparse.ArgumentParser(description="Build FAISS index from a PDF textbook")
    parser.add_argument("--pdf_path", default="../data/Python_Programming.pdf", help="Path to the PDF file")
    parser.add_argument("--output_index", default="../output/textbook_index.faiss", help="Output path for FAISS index")
    parser.add_argument("--output_chunks", default="../output/text_chunks.pkl", help="Output path for text chunks")
    parser.add_argument("--max_chunk_size", type=int, default=1000, help="Maximum chunk size in characters")
    parser.add_argument("--embed_model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    args = parser.parse_args()

    logger.info("📖 Extracting paragraphs...")
    chunks = extract_pdf_paragraph_chunks_with_metadata(args.pdf_path, args.max_chunk_size)

    logger.info("📐 Embedding & indexing...")
    faiss_index, enriched_chunks = build_faiss_index(chunks, args.embed_model)

    logger.info("💾 Saving index and chunks...")
    try:
        faiss.write_index(faiss_index, args.output_index)
        with open(args.output_chunks, "wb") as f:
            pickle.dump(enriched_chunks, f)
        logger.info(f"✅ Index saved to {args.output_index} and chunks to {args.output_chunks}")
    except Exception as e:
        logger.error(f"Error saving index/chunks: {e}")
        raise

if __name__ == "__main__":
    main()
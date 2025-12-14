from typing import List, Tuple
from pypdf import PdfReader
from chonkie import SlumberChunker, OpenAIGenie
from core.config import OPENAI_API_KEY, OPENAI_MODEL

def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        text_content = []
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_content.append(page_text.strip())
            except Exception as e:
                print(f"⚠️ Cannot extract page {page_num}: {e}")
                continue
        
        if not text_content:
            return "Empty PDF"
        
        return "\n\n".join(text_content)
        
    except Exception as e:
        print(f"❌ PDF Error: {e}")
        raise

def chunk_text(text: str) -> List:
    try:
        genie = OpenAIGenie(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
        
        chunker = SlumberChunker(
            genie=genie,
            tokenizer="gpt2",
            chunk_size=1024,
            candidate_size=128,
            min_characters_per_chunk=100,
            verbose=False
        )
        
        chunks = chunker.chunk(text)
        return chunks
        
    except Exception as e:
        print(f"⚠️ Chonkie chunking failed: {e}")
        chunk_size = 1000
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def load_and_chunk_pdf(file_path: str) -> Tuple[str, List]:
    print(f"Extracting text from {file_path}...")
    text = extract_text_from_pdf(file_path)
    
    print("Chunking with Chonkie...")
    chunks = chunk_text(text)
    
    print(f"✅ Created {len(chunks)} chunks")
    return text, chunks

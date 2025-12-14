from typing import Dict
from core.pdf_processor import load_and_chunk_pdf
from core.agent import create_mcq_agent, generate_mcqs_from_chunk

def generate_mcqs_from_pdf(pdf_path: str, num_questions: int = 10) -> Dict:
    # Step 1: Load PDF and chunk it with Chonkie
    print("\nStep 1: Loading and chunking PDF...")
    full_text, chunks = load_and_chunk_pdf(pdf_path)
    
    # Step 2: Create MCQ agent
    print("\nStep 2: Creating MCQ agent...")
    agent = create_mcq_agent()
    
    # Step 3: Generate MCQs from chunks
    print(f"\nStep 3: Generating {num_questions} MCQs...")
    all_mcqs = []
    
    # Distribute questions across chunks
    questions_per_chunk = max(1, num_questions // len(chunks))
    
    for i, chunk in enumerate(chunks):
        # For last chunk, generate remaining questions
        if i == len(chunks) - 1:
            remaining = num_questions - len(all_mcqs)
            questions_per_chunk = max(1, remaining)
        
        # Extract text from chunk
        chunk_text = chunk.text if hasattr(chunk, 'text') else str(chunk)
        
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        
        # Generate MCQs
        mcqs = generate_mcqs_from_chunk(
            chunk_text,
            min(questions_per_chunk, num_questions - len(all_mcqs)),
            agent
        )
        
        all_mcqs.extend(mcqs)
        
        # Stop if we have enough questions
        if len(all_mcqs) >= num_questions:
            break
    
    # Step 4: Return results
    result = {
        "questions": all_mcqs[:num_questions],
        "metadata": {
            "num_chunks": len(chunks),
            "total_questions": len(all_mcqs[:num_questions]),
            "text_length": len(full_text)
        }
    }
    
    print(f"\n✅ Generated {len(result['questions'])} questions!")
    return result

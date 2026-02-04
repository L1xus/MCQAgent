from typing import Dict
from core.pdf_processor import load_and_chunk_pdf
from core.agent import create_mcq_agent, generate_mcqs_from_chunk
from core.tracker import tracker

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
        
        # Get MCQs and Usage Data
        mcqs, usage = generate_mcqs_from_chunk(
            chunk_text,
            min(questions_per_chunk, num_questions - len(all_mcqs)),
            agent
        )
        
        tracker.log_usage(
            input_tokens=usage.get("input_tokens", 0), 
            output_tokens=usage.get("output_tokens", 0)
        )
        
        all_mcqs.extend(mcqs)
        
        if len(all_mcqs) >= num_questions:
            break
    
    # Log document completion
    tracker.log_usage(0, 0, is_new_document=True)

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

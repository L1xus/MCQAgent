from dotenv import load_dotenv
from services.mcq_service import generate_mcqs_from_pdf

load_dotenv()

def main():
    print("\n" + "="*80)
    print("MCQ Learning Assistant")
    print("="*80 + "\n")
    
    # Configuration
    pdf_path = "docs/bitcoin.pdf" 
    num_questions = 5
    
    print(f"📄 PDF: {pdf_path}")
    print(f"❓ Questions: {num_questions}")
    
    # Generate MCQs using the service
    result = generate_mcqs_from_pdf(
        pdf_path=pdf_path,
        num_questions=num_questions
    )
    
    mcqs = result["questions"]
    
    # Show questions
    for i, mcq in enumerate(mcqs, 1):
        print(f"\n{'='*80}")
        print(f"Question {i} [{mcq['difficulty']}]")
        print('='*80)
        print(f"\n{mcq['question']}\n")
        
        for option in mcq['options']:
            print(f"  {option}")
        
        print(f"\n✓ Answer: {mcq['correct_answer']}")
        print(f"💡 Hint: {mcq['hint']}")
        print(f"📖 Explanation: {mcq['explanation']}")
    
    print("\n" + "="*80)
    print("✨ Done!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

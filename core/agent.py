from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.models import MCQList
from core.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from typing import List

def create_mcq_agent():
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        api_key=OPENAI_API_KEY
    ).with_structured_output(MCQList)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert educator creating multiple-choice questions.
        
        STRICT FORMATTING RULES:
        - Options MUST be formatted as: "A. text", "B. text", "C. text", "D. text"
        - correct_answer MUST be ONLY the letter: "A", "B", "C", or "D" (no periods, no text)
        - difficulty MUST be: "easy", "medium", or "hard" (lowercase)
        
        CONTENT GUIDELINES:
        - Questions must be clear and test understanding
        - Create exactly 4 options (A, B, C, D)
        - Only ONE correct answer
        - Distractors should be plausible but wrong
        - Explanation references the content
        - Hint guides thinking without revealing answer
        - Mix easy, medium, and hard difficulties
        
        EXAMPLE FORMAT:
        {{
            "question": "What is X?",
            "options": ["A. First option", "B. Second option", "C. Third option", "D. Fourth option"],
            "correct_answer": "C",
            "explanation": "The answer is C because...",
            "hint": "Think about...",
            "difficulty": "medium"
        }}
        """),
        ("user", """Create {count} multiple-choice questions from this content:
        {content}
        
        Remember: 
        - Options format: "A. text", "B. text", "C. text", "D. text"
        - correct_answer: Just the letter (A, B, C, or D)
        - difficulty: easy, medium, or hard
        
        Generate {count} questions now.""")
    ])
    
    return prompt | llm

def generate_mcqs_from_chunk(chunk_text: str, count: int, agent) -> List[dict]:
    try:
        response: MCQList = agent.invoke({
            "count": count,
            "content": chunk_text[:4000]
        })
        
        return [q.model_dump() for q in response.questions[:count]]
        
    except Exception as e:
        print(f"⚠️ MCQ generation failed: {e}")
        return []

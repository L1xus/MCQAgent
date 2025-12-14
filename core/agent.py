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
        Guidelines:
        - Questions must be clear and test understanding
        - Create exactly 4 options (A, B, C, D)
        - Only ONE correct answer
        - Distractors should be plausible but wrong
        - Explanation references the content
        - Hint guides thinking without revealing answer
        - Mix easy, medium, and hard difficulties
        Generate questions following the exact structure provided."""),
        ("user", """Create {count} multiple-choice questions from this content:
        {content}
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

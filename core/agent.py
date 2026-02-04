from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.models import MCQList
from core.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from typing import List, Tuple
import tiktoken
import json

def create_mcq_agent():
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        api_key=OPENAI_API_KEY
    )
    
    structured_llm = llm.with_structured_output(MCQList, include_raw=True)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert educator creating multiple-choice questions.
        
        STRICT FORMATTING RULES:
        - Options MUST be formatted as: "A. text", "B. text", "C. text", "D. text"
        - correct_answer MUST be ONLY the letter: "A", "B", "C", or "D"
        - difficulty MUST be: "easy", "medium", or "hard" (lowercase)
        
        LANGUAGE RULES:
        - Detect the language of the provided content.
        - If the content is in French, generate the Question, Options, Explanation, and Hint in French.
        - If the content is in Arabic, generate them in Arabic.
        - Keep the JSON keys (question, options, etc.) in English.
        - Ensure Arabic text is grammatically correct and coherent.
        
        CONTENT GUIDELINES:
        - Create exactly 4 options (A, B, C, D)
        - Only ONE correct answer
        - Distractors should be plausible but wrong
        - Explanation references the content
        - Mix difficulties
        """),
        ("user", """Create {count} multiple-choice questions from this content:
        {content}
        """)
    ])
    
    return prompt | structured_llm

def count_tokens_manually(text: str, model: str = "gpt-4o") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def generate_mcqs_from_chunk(chunk_text: str, count: int, agent) -> Tuple[List[dict], dict]:
    try:
        result = agent.invoke({
            "count": count,
            "content": chunk_text[:4000]
        })
        
        parsed_output: MCQList = result['parsed']
        raw_message = result['raw']
        
        usage_metadata = raw_message.response_metadata.get("token_usage", {})
        
        input_tokens = usage_metadata.get("prompt_tokens", 0)
        output_tokens = usage_metadata.get("completion_tokens", 0)
        
        if input_tokens == 0 and output_tokens == 0:
            print("⚠️ Metadata missing, calculating tokens manually...")
            input_tokens = count_tokens_manually(chunk_text[:4000], OPENAI_MODEL) + 300
            
            json_output = json.dumps([q.model_dump() for q in parsed_output.questions])
            output_tokens = count_tokens_manually(json_output, OPENAI_MODEL)

        usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }

        print(f"💰 Token Usage: {usage}")
        
        return [q.model_dump() for q in parsed_output.questions[:count]], usage
        
    except Exception as e:
        print(f"⚠️ MCQ generation failed: {e}")
        return [], {"input_tokens": 0, "output_tokens": 0}

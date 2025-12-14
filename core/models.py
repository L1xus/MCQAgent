from pydantic import BaseModel, Field, field_validator
from typing import List


class MCQQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="Exactly 4 options formatted as 'A. text', 'B. text', 'C. text', 'D. text'")
    correct_answer: str = Field(description="Single letter only: A, B, C, or D")
    explanation: str = Field(description="Why the answer is correct")
    hint: str = Field(description="Hint without revealing answer")
    difficulty: str = Field(description="easy/medium/hard")
    
    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v: str) -> str:
        """Ensure correct_answer is just a single letter"""
        v = v.strip().upper()
        if '.' in v:
            v = v.split('.')[0].strip()
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError('correct_answer must be A, B, C, or D')
        return v
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        """Ensure options are formatted correctly"""
        if len(v) != 4:
            raise ValueError('Must have exactly 4 options')
        
        formatted = []
        letters = ['A', 'B', 'C', 'D']
        for i, option in enumerate(v):
            option = option.strip()
            # If option doesn't start with letter, add it
            if not option.startswith(f"{letters[i]}."):
                option = f"{letters[i]}. {option}"
            formatted.append(option)
        return formatted
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Ensure difficulty is lowercase"""
        v = v.strip().lower()
        if v not in ['easy', 'medium', 'hard']:
            raise ValueError('difficulty must be easy, medium, or hard')
        return v

class MCQList(BaseModel):
    questions: List[MCQQuestion] = Field(description="Generated questions")


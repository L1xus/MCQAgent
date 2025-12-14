from pydantic import BaseModel, Field
from typing import List


class MCQQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="4 options (A, B, C, D)")
    correct_answer: str = Field(description="Correct answer letter")
    explanation: str = Field(description="Why the answer is correct")
    hint: str = Field(description="Hint without revealing answer")
    difficulty: str = Field(description="easy/medium/hard")


class MCQList(BaseModel):
    questions: List[MCQQuestion] = Field(description="Generated questions")


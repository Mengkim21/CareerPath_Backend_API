import os
import json
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Optional

# Load environment variables from the root .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
  print("Error: GROQ_API_KEY is missing!")
  exit(1)

# Initialize Groq Client
client = Groq(api_key=api_key)

# Define the exact Pydantic Schema 
class ExtractedCandidateProfile(BaseModel):
    full_name: Optional[str] = Field(description="Candidate's full name")
    major: Optional[str] = Field(description="Degree major or field of study")
    gpa: Optional[float] = Field(description="Numeric GPA if found, else null")
    parsed_skills: List[str] = Field(description="Normalized list of technical skills")
    parsed_coursework: List[str] = Field(description="Academic courses/subjects taken")

# Realistic sample raw text (similar to what PyMuPDF will extract from a PDF)
sample_resume_text = """
CURRICULUM VITAE
Sokha Meng
Phnom Penh, Cambodia | sokha.meng@email.com | +855 12 345 678

EDUCATION:
Royal University of Phnom Penh (RUPP)
Bachelor of Science in Computer Science (2021 - 2025)
Cumulative GPA: 3.65 / 4.0

RELEVANT COURSEWORK:
- Data Structures and Algorithms
- Database Management Systems (PostgreSQL)
- Web Development with Python and React
- Computer Networks and Operating Systems

TECHNICAL SKILLS:
Programming Languages: Python, JavaScript, SQL
Frameworks & Tools: FastAPI, Node.js, Git, Docker, Tailwind CSS
Languages: Khmer (Native), English (Professional Working)

PROJECTS:
Cambodia Job Matching Portal:
Built a web application using FastAPI and PostgreSQL with a Next.js frontend.
Integrated RESTful APIs and managed relational database schemas.
"""

print("Sending request to Groq (model: llama-3.1-8b-instant)...")

# Prompt Groq with strict JSON Mode enabled
system_prompt = f"""
You are an expert AI Resume and Transcript Parser for Cambodian university graduates.
Extract candidate details from the provided text and output STRICT JSON matching this schema:
{json.dumps(ExtractedCandidateProfile.model_json_schema(), indent=2)}

Rules:
- Extract all verified technical skills.
- Extract academic subjects under coursework.
- If GPA is not explicitly stated, return null.
- Respond ONLY with the valid raw JSON object. Do not include markdown codeblocks or conversational text.
"""

try: 
  response = client.chat.completions.create(
      model="openai/gpt-oss-20b",
      messages=[
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": sample_resume_text}
      ],
      temperature=0.1,  # Low temperature for deterministic/factual extraction
      response_format={"type": "json_object"}  # Forces Groq to return pure JSON
  )

  # Parse and Validate Output
  raw_json = response.choices[0].message.content
  print("\n Raw JSON Response from Groq:")
  print(raw_json)

  # Validate using Pydantic (ensures data types match before database insertion)

  validated_data = ExtractedCandidateProfile.model_validate_json(raw_json)
  print("\n🎉 Success! Pydantic Validation Passed:")
  print(f"- Name: {validated_data.full_name}")
  print(f"- Major: {validated_data.major}")
  print(f"- GPA: {validated_data.gpa}")
  print(f"- Skills ({len(validated_data.parsed_skills)}): {validated_data.parsed_skills}")
  print(f"- Courses ({len(validated_data.parsed_coursework)}): {validated_data.parsed_coursework}")

except Exception as e:
    print(f"\n Validation Error: {e}")
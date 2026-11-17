import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from groq import Groq
from typing import List

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
  print("Error: GROQ_API_KEY is missing")
  exit(1)

client = Groq(api_key=api_key)
SELECTED_MODEL = "openai/gpt-oss-20b"

# define the structured output schema
class SkillGapAnalysis(BaseModel):
  matched_skills: List[str] = Field(description="Skills the candidate possesses that satisfy job requirements")
  missing_skills: List[str] = Field(description="Crucial required skills that the candidate is lacking")
  course_alignment: List[str] = Field(description="Candidate courses that directly support the job requirements")
  reasoning: str = Field(description="Brief explanation of the semantic matching decisions")

# Sample curated Cambodian benchmark job roles
CAMBODIAN_JOB_DATABASE = {
  "job_backend_01": {
      "title": "Junior Backend Developer",
      "company_type": "Commercial Bank (Phnom Penh)",
      "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "RESTful APIs", "Redis"],
      "preferred_courses": ["Database Systems", "Data Structures", "Computer Networks"]
  },
  "job_marketing_01": {
      "title": "Marketing Specialist",
      "company_type": "Fintech / Digital Payments (Phnom Penh)",
      "required_skills": ["Project Management", "Public Relations", "Digital Advertising", "Brand Consistency", "Market Research", "Google Analytics"],
      "preferred_courses": ["Marketing Strategy", "Business Communications"]
  }
}

# Candidate profile to test
candidate_profile = {
  "name": "Richard Sanchez",
  "degree_major": "Bachelor of Business / Master of Business Management",
  "gpa": 3.8,
  "parsed_skills": [
     "Project Management", 
     "Public Relations", 
     "Teamwork", 
     "Time Management", 
     "Leadership", 
     "Effective Communication",
     "Critical Thinking", 
     "Brand Consistency",
     "Market Research",
     "Budget Management"
  ],
  "parsed_coursework": []
}

# Run matching function
def match_candidate_to_job(candidate: dict, target_job: dict):
  print(f"\nMatching '{candidate['name']}' against '{target_job['title']}'...")
  print(f"Company Sector: {target_job['company_type']}")
  print(f"Required Job Skills ({len(target_job['required_skills'])}): {target_job['required_skills']}")
  print(f"Candidate Skills ({len(candidate['parsed_skills'])}): {candidate['parsed_skills']}\n")

  system_prompt = f"""
You are an expert technical recruiter in Phnom Penh, Cambodia.
Analyze the candidate's skills and coursework against the target job requirements.
Perform semantic matching.

Output STRICT JSON matching this schema:
{json.dumps(SkillGapAnalysis.model_json_schema(), indent=2)}

Rules:
- Be strict about missing technical tools (e.g., if Leadership or Public Relation is missing, list it in missing_skills).
- Only include a skill in 'matched_skills' if the candidate has proven experience or direct equivalence.
- Output ONLY valid raw JSON.
"""

  user_prompt = f"""
Candidate Profile:
- Skills: {candidate['parsed_skills']}
- Coursework: {candidate['parsed_coursework']}

Job Requirements:
- Required Skills: {target_job['required_skills']}
- Preferred Courses: {target_job['preferred_courses']}
"""

  response = client.chat.completions.create(
      model=SELECTED_MODEL,
      messages=[
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": user_prompt}
      ],
      temperature=0.1
  )

  raw_output = response.choices[0].message.content.strip()
  if raw_output.startswith("```"):
      raw_output = raw_output.split("```")[1]
      if raw_output.startswith("json"):
          raw_output = raw_output[4:]
  raw_output = raw_output.strip()

  analysis = SkillGapAnalysis.model_validate_json(raw_output)

  # Deterministic Mathematical Score Calculation
  total_required = len(target_job["required_skills"])
  num_matched = len(analysis.matched_skills)
  
  # 85% based on hard skill coverage
  skill_ratio = (num_matched / total_required) if total_required > 0 else 0
  skill_score = skill_ratio * 85.0
  
  # 15% bonus for relevant academic coursework
  course_bonus = min(len(analysis.course_alignment) * 5.0, 15.0)
  
  final_match_percentage = round(skill_score + course_bonus, 1)

  return analysis, final_match_percentage

# Execute Test
if __name__ == "__main__":
    target_job = CAMBODIAN_JOB_DATABASE["job_marketing_01"]
    result, score = match_candidate_to_job(candidate_profile, target_job)

    print("=" * 60)
    print(f"📊 MATCH RESULTS: {score}% COMPATIBILITY")
    print("=" * 60)
    print(f"✅ Matched Skills   ({len(result.matched_skills)}): {result.matched_skills}")
    print(f"❌ Missing Gaps     ({len(result.missing_skills)}): {result.missing_skills}")
    print(f"📚 Course Alignment ({len(result.course_alignment)}): {result.course_alignment}")
    print(f"💡 AI Recruiter Reasoning: {result.reasoning}")
    print("=" * 60)
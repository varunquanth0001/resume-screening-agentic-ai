import json
import random
from faker import Faker
from pydantic import BaseModel, Field
from typing import List, Optional

class Resume(BaseModel):
    id: int
    name: str
    contact: str
    skills: List[str]
    experience_years: int
    education: str
    summary: str

def generate_resumes(num_resumes: int = 20, seed: int = 42) -> List[Resume]:
    fake = Faker()
    Faker.seed(seed)
    random.seed(seed)

    skill_pool = [
        "Python", "SQL", "React", "Node.js", "Docker", "AWS", "Machine Learning",
        "TensorFlow", "PyTorch", "Java", "C++", "Go", "Kubernetes", "PostgreSQL",
        "NoSQL", "Git", "Agile", "Tableau", "PowerBI", "FastAPI", "Flask",
        "Django", "Spark", "Hadoop", "Excel", "Data Visualization"
    ]

    education_levels = [
        "Bachelor's in Computer Science", "Master's in Data Science",
        "PhD in AI", "B.Tech in Information Technology",
        "M.Sc in Software Engineering", "Bachelor's in Mathematics"
    ]

    resumes = []
    for i in range(1, num_resumes + 1):
        num_skills = random.randint(3, 8)
        skills = random.sample(skill_pool, num_skills)
        
        resume = Resume(
            id=i,
            name=fake.name(),
            contact=fake.email(),
            skills=skills,
            experience_years=random.randint(0, 15),
            education=random.choice(education_levels),
            summary=fake.paragraph(nb_sentences=3)
        )
        resumes.append(resume)
    
    return resumes

def save_resumes(resumes: List[Resume], filename: str = "synthetic_resumes.json"):
    with open(filename, "w") as f:
        json.dump([r.dict() for r in resumes], f, indent=4)

if __name__ == "__main__":
    resumes = generate_resumes(num_resumes=20, seed=42)
    save_resumes(resumes)
    print(f"Generated 20 synthetic resumes in synthetic_resumes.json (Seed: 42)")

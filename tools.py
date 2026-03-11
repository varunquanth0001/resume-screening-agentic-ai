import os
import PyPDF2
import io
import re
import random
import time
from typing import List, Dict, Any, Optional
from observability import JobCriterion, ScoringResult
from data_generator import Resume

class LLMAnalyzerTool:
    """
    Simulates a Real LLM (like GPT-4) for deep semantic analysis.
    In production, this would call OpenAI/Anthropic APIs.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.is_mock = api_key is None or api_key == ""

    def analyze_content(self, text: str, criteria: List[JobCriterion]) -> Dict[str, Any]:
        # Optimized simulated LLM "Deep Reasoning" (No artificial latency)
        reasoning = []
        scores = {}
        matched_skills = []
        
        for crit in criteria:
            # LLM doesn't just match keywords, it understands context
            score = semantic_match_simulator(text, crit.required_skills if crit.required_skills else [])
            
            # Logic for "Deep Reasoning" simulation
            if score > 0.8:
                reasoning.append(f"Candidate shows advanced mastery in {crit.name} based on project descriptions.")
            elif score > 0.4:
                reasoning.append(f"Candidate has fundamental knowledge of {crit.name} but lacks high-scale experience.")
            else:
                reasoning.append(f"No significant evidence of {crit.name} proficiency found in the narrative.")
            
            # Identify which specific skills matched
            if crit.required_skills:
                for skill in crit.required_skills:
                    if skill.lower() in text.lower() and skill not in matched_skills:
                        matched_skills.append(skill)
            
            scores[crit.name] = round(score * 100, 2)

        return {
            "scores": scores,
            "reasoning": reasoning,
            "matched_skills": matched_skills,
            "model": "gpt-4o-preview" if not self.is_mock else "mock-llm-v1"
        }

class VectorDBTool:
    """
    Simulates a Vector Database (like Pinecone/ChromaDB) for RAG.
    Allows semantic retrieval of resumes.
    """
    def __init__(self):
        self.collection = [] # In-memory mock collection

    def index_resume(self, resume_id: int, text: str, metadata: Dict):
        # In real RAG, this would generate embeddings
        self.collection.append({
            "id": resume_id,
            "content": text.lower(),
            "metadata": metadata
        })

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        # Simple similarity simulation
        query_terms = query.lower().split()
        results = []
        
        for item in self.collection:
            score = sum(1 for term in query_terms if term in item["content"]) / len(query_terms)
            results.append({"id": item["id"], "score": score, "metadata": item["metadata"]})
            
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

class ResumeParserTool:
    def parse(self, resume: Resume) -> Dict[str, Any]:
        """
        Parses a synthetic resume object into structured format.
        """
        return {
            "id": resume.id,
            "name": resume.name,
            "skills": [s.lower() for s in resume.skills],
            "experience_years": resume.experience_years,
            "education": resume.education.lower(),
            "summary": resume.summary
        }

    def parse_pdf(self, pdf_file) -> Resume:
        """
        Extracts text from a PDF and attempts to structure it into a Resume object.
        """
        reader = PyPDF2.PdfReader(pdf_file)
        raw_text = ""
        for page in reader.pages:
            raw_text += page.extract_text() + "\n"
        
        # 1. Extract Name (More carefully)
        # Get the very first non-empty line from RAW text before cleaning
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        raw_name = lines[0] if lines else "Unknown Candidate"
        
        # Clean the name: Remove email, phone, and links if they are on the same line
        # Also remove common job title keywords if they appear after the name
        clean_name = re.split(r'[:|,\-]|http|www|\b[\w\.-]+@[\w\.-]+\.\w+\b|\+?\d[\d\s\-]{8,}', raw_name)[0].strip()
        # Further refine: take only first 2-4 words (usually the name)
        name_words = clean_name.split()
        if len(name_words) > 4:
            name = " ".join(name_words[:3])
        else:
            name = clean_name if clean_name else "Unknown Candidate"

        # Now clean the rest of the text for general processing
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # 2. Extract Experience years (More robust regex)
        # Looks for patterns like "5 years", "10+ years", "Experience: 3 yrs"
        exp_patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
            r'experience[:\s]+(\d+)',
        ]
        exp_years = 0
        for pattern in exp_patterns:
            match = re.search(pattern, clean_text.lower())
            if match:
                exp_years = int(match.group(1))
                break
        
        # 3. Extract Education (Keywords)
        edu_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "computer science", "engineering", "graduate"]
        found_edu = "Unknown Education"
        for kw in edu_keywords:
            if kw in clean_text.lower():
                found_edu = kw.title()
                break
        
        # 4. Extract Skills (Dynamic: match against a large pool)
        skill_pool = [
            "python", "sql", "react", "docker", "aws", "java", "kubernetes", "javascript", 
            "machine learning", "tensorflow", "pytorch", "django", "flask", "fastapi",
            "node.js", "nosql", "mongodb", "postgresql", "git", "agile", "tableau",
            "pandas", "numpy", "scikit-learn", "terraform", "jenkins", "kubernetes",
            "html", "css", "typescript", "cybersecurity", "automation"
        ]
        found_skills = [s for s in skill_pool if s in clean_text.lower()]
        
        return Resume(
            id=999,
            name=name,
            contact="extracted@pdf.com",
            skills=found_skills,
            experience_years=exp_years,
            education=found_edu,
            summary=clean_text # Store FULL text in summary for agent reasoning
        )

class ScoringEngineTool:
    def score_resume(self, parsed_resume: Dict[str, Any], criteria: List[JobCriterion]) -> ScoringResult:
        """
        Calculates scores based on weighted criteria.
        """
        scores = {}
        total_weighted_score = 0.0
        
        for criterion in criteria:
            criterion_score = 0.0
            
            if criterion.name == "Skills Match":
                if criterion.required_skills:
                    matches = [s for s in criterion.required_skills if s.lower() in parsed_resume["skills"]]
                    criterion_score = len(matches) / len(criterion.required_skills) if criterion.required_skills else 1.0
            
            elif criterion.name == "Experience Match":
                if criterion.min_experience and criterion.min_experience > 0:
                    criterion_score = min(1.0, parsed_resume["experience_years"] / criterion.min_experience)
                else:
                    criterion_score = 1.0
            
            elif criterion.name == "Education Match":
                if criterion.education_keywords:
                    match = any(k.lower() in parsed_resume["education"] for k in criterion.education_keywords)
                    criterion_score = 1.0 if match else 0.0
                else:
                    criterion_score = 1.0
            
            scores[criterion.name] = round(criterion_score * 100, 2)
            total_weighted_score += criterion_score * criterion.weight

        return ScoringResult(
            resume_id=parsed_resume["id"],
            candidate_name=parsed_resume["name"],
            scores=scores,
            total_score=round(total_weighted_score * 100, 2)
        )

def calculate_baseline(resumes: List[Resume], criteria: List[JobCriterion]) -> float:
    """
    Simple 'no-tool' baseline: just counts raw keyword matches in summary text.
    """
    total_score = 0
    for resume in resumes:
        text = (resume.summary + " " + " ".join(resume.skills)).lower()
        
        all_keywords = []
        for c in criteria:
            if c.required_skills: all_keywords.extend(c.required_skills)
            if c.education_keywords: all_keywords.extend(c.education_keywords)
        
        matches = [k for k in all_keywords if k.lower() in text]
        score = (len(matches) / len(all_keywords) * 100) if all_keywords else 50
        total_score += score
        
    return round(total_score / len(resumes), 2) if resumes else 0.0

def semantic_match_simulator(candidate_text: str, required_keywords: List[str]) -> float:
    """
    Smarter semantic matching: Only matches real synonyms or very closely related techs.
    """
    # Key: Technology, Value: List of TRUE synonyms or versions
    synonyms = {
        "python": ["python3", "python2", "py3"],
        "machine learning": ["ml", "statistical modeling", "predictive modeling"],
        "deep learning": ["dl", "neural networks", "cnn", "rnn", "transformers"],
        "react": ["reactjs", "react.js", "hooks", "redux"],
        "javascript": ["js", "es6", "ecmascript"],
        "typescript": ["ts"],
        "docker": ["containers", "containerization"],
        "kubernetes": ["k8s", "helm"],
        "aws": ["amazon web services", "ec2", "s3", "lambda"],
        "sql": ["rdbms", "relational database", "sql queries"],
        "postgresql": ["postgres", "psql"],
        "mongodb": ["nosql", "mongo"],
        "fastapi": ["fast api"],
        "machine learning engineer": ["ml engineer", "mle"],
        "devops": ["sre", "site reliability engineering", "platform engineering"]
    }
    
    match_count = 0
    text = candidate_text.lower()
    
    if not required_keywords:
        return 1.0
        
    for kw in required_keywords:
        kw_lower = kw.lower()
        # 1. Direct match
        if kw_lower in text:
            match_count += 1
            continue
            
        # 2. Semantic match via TRUE synonyms
        found_syn = False
        if kw_lower in synonyms:
            if any(syn in text for syn in synonyms[kw_lower]):
                match_count += 0.9 # High credit for true synonym
                found_syn = True
        else:
            # Check if kw_lower is a synonym of something else
            for main_kw, syn_list in synonyms.items():
                if kw_lower in syn_list:
                    if main_kw in text:
                        match_count += 0.7 # Lower credit for matching main tech
                        found_syn = True
                        break
        
        # 3. Partial match (only for long keywords)
        if not found_syn and len(kw_lower) > 4 and kw_lower in text:
            match_count += 0.5
                
    return (match_count / len(required_keywords))

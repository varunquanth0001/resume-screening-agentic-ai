import time
import random
import os
from typing import List, Dict, Any, Optional
from observability import Observability, State, JobCriterion, ScoringResult
from tools import ResumeParserTool, ScoringEngineTool, calculate_baseline, semantic_match_simulator, LLMAnalyzerTool, VectorDBTool
from data_generator import Resume

class TechnicalAgent:
    def __init__(self, parser, scorer, obs, llm):
        self.parser = parser
        self.scorer = scorer
        self.obs = obs
        self.llm = llm
        self.name = "TechnicalScorerAgent"

    def process(self, resume: Resume, criteria: List[JobCriterion]) -> Dict[str, Any]:
        thought = f"Analyzing {resume.name}'s resume against criteria: {[c.name for c in criteria]}. Using Deep LLM logic."
        parsed = self.parser.parse(resume)
        # Deep LLM-based analysis
        analysis = self.llm.analyze_content(resume.summary + " " + " ".join(resume.skills), criteria)
        
        self.obs.log_tool_call(self.name, {"id": resume.id}, {"analysis": analysis}, thought=thought)
        return {
            "parsed": parsed, 
            "tech_score": sum(analysis["scores"].values()) / len(analysis["scores"]) / 100, 
            "reasoning": analysis["reasoning"],
            "matched_skills": analysis.get("matched_skills", [])
        }

class SoftSkillsAgent:
    def __init__(self, obs):
        self.obs = obs
        self.name = "SoftSkillsAgent"

    def process(self, resume: Resume, role: str) -> float:
        # Role-specific soft skills keywords
        role_keywords = {
            "DevOps": ["automation", "monitoring", "reliability", "infrastructure", "scaling"],
            "Frontend": ["ui", "ux", "design", "responsive", "accessibility", "animation"],
            "Data Scientist": ["analytical", "research", "statistics", "modeling", "insights"],
            "ML Engineer": ["optimization", "training", "deployment", "pipeline", "accuracy"],
            "Backend": ["api", "scalability", "database", "concurrency", "security"]
        }
        
        text = (resume.summary + " " + " ".join(resume.skills)).lower()
        soft_skills_score = 0.4 # Lower baseline
        
        # 1. Leadership (Generic)
        leadership = ["led", "managed", "coordinated", "mentored", "initiative", "stakeholder"]
        if any(k in text for k in leadership):
            soft_skills_score += 0.2
            
        # 2. Role-specific alignment
        found_role = False
        for r_name, kws in role_keywords.items():
            if r_name.lower() in role.lower():
                matches = [k for k in kws if k in text]
                soft_skills_score += (len(matches) / len(kws)) * 0.3
                found_role = True
                break
        
        if not found_role: # Default for unknown roles
            soft_skills_score += 0.1

        # 3. Content depth
        if len(text.split()) > 30:
            soft_skills_score += 0.1
            
        self.obs.log_tool_call(self.name, {"id": resume.id, "role": role}, {"score": round(soft_skills_score, 2)})
        return min(1.0, soft_skills_score)

class AuditorAgent:
    def __init__(self, obs):
        self.obs = obs
        self.name = "FinalAuditorAgent"

    def finalize(self, tech_data: Dict, soft_score: float, criteria: List[JobCriterion]) -> ScoringResult:
        scores = {}
        total_weighted = 0.0
        
        tech_parsed = tech_data["parsed"]
        for crit in criteria:
            if crit.name == "Skills Match":
                score = tech_data["tech_score"]
            elif crit.name == "Experience Match":
                # More dynamic experience scoring
                if crit.min_experience and crit.min_experience > 0:
                    score = min(1.2, tech_parsed["experience_years"] / crit.min_experience) # Bonus for over-qualified
                    score = min(1.0, score)
                else:
                    score = 1.0
            elif crit.name == "Education Match":
                score = 1.0 if any(k.lower() in tech_parsed["education"].lower() for k in crit.education_keywords) else 0.2
            else:
                score = 0.5
            
            scores[crit.name] = round(score * 100, 2)
            total_weighted += score * crit.weight
            
        # Soft skills contribution
        scores["Soft Skills"] = round(soft_score * 100, 2)
        
        # Auditor weights tech more than soft skills (85/15 split)
        final_score = (total_weighted * 0.85) + (soft_score * 0.15)
        
        return ScoringResult(
            resume_id=tech_parsed["id"],
            candidate_name=tech_parsed["name"],
            scores=scores,
            total_score=round(final_score * 100, 2),
            matched_skills=tech_data.get("matched_skills", [])
        )

class RecruiterAgent:
    def __init__(self, obs):
        self.obs = obs
        self.name = "RecruiterAgent"

    def analyze(self, result: ScoringResult, criteria: List[JobCriterion]) -> Dict[str, Any]:
        """
        Generates tailored summaries and interview questions.
        """
        # Logic to generate summary based on scores
        score = result.total_score
        if score > 85:
            summary = f"Exceptional candidate for {result.candidate_name}. Highly recommended for direct technical interview."
        elif score > 70:
            summary = f"Strong potential in {result.candidate_name}, but needs vetting in specific skill gaps."
        else:
            summary = f"Candidate shows basic knowledge but may not meet the seniority bar."

        # Generate questions based on criteria
        questions = []
        for crit in criteria:
            if crit.name == "Skills Match" and result.scores.get(crit.name, 0) < 100:
                missing = [s for s in crit.required_skills if s.lower() not in summary.lower()] # Simplified
                questions.append(f"Can you explain your experience with {random.choice(crit.required_skills)} in a production environment?")
            elif crit.name == "Experience Match" and result.scores.get(crit.name, 0) < 100:
                questions.append("How do you handle complex tasks that require more years of experience than you currently have?")

        if not questions:
            questions = ["Describe your most challenging project.", "What is your approach to learning new tech stacks?"]

        self.obs.log_tool_call(self.name, {"id": result.resume_id}, {"summary": summary})
        return {"summary": summary, "questions": questions[:3]}

class ScreeningAgent:
    def __init__(self, run_id: str, criteria: List[JobCriterion], scenario_type: str = "Custom", max_steps: int = 20, simulate_failure: bool = False):
        self.obs = Observability(run_id=run_id)
        self.criteria = criteria
        self.scenario_type = scenario_type
        self.max_steps = max_steps
        self.simulate_failure = simulate_failure
        
        # Advanced Infrastructure
        self.llm = LLMAnalyzerTool(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_db = VectorDBTool()
        
        # Initialize specialized agents
        self.tech_agent = TechnicalAgent(ResumeParserTool(), ScoringEngineTool(), self.obs, self.llm)
        self.soft_agent = SoftSkillsAgent(self.obs)
        self.auditor = AuditorAgent(self.obs)
        self.recruiter = RecruiterAgent(self.obs)
        
        self.metrics = {
            "total_processed": 0,
            "avg_score": 0.0,
            "total_time": 0.0,
            "baseline_score": 0.0,
            "agents_active": 4,
            "infrastructure": "Advanced (RAG + LLM Reasoning Engine)"
        }

    def run(self, resumes: List[Resume]) -> List[ScoringResult]:
        start_time = time.time()
        try:
            self.metrics["baseline_score"] = calculate_baseline(resumes, self.criteria)
            
            # Workflow Orchestration
            self.obs.transition(f"Multi-Agent Analysis for {self.scenario_type}", State.PARSING, input_data={"num": len(resumes)})
            
            results = []
            for i, resume in enumerate(resumes[:self.max_steps]):
                if self.simulate_failure and i == 5:
                    raise Exception("Unexpected Orchestration Failure!")

                # 1. Tech Analysis
                tech_data = self.tech_agent.process(resume, self.criteria)
                # 2. Soft Skills Analysis (Now role-aware)
                soft_score = self.soft_agent.process(resume, self.scenario_type)
                # 3. Final audit
                final_res = self.auditor.finalize(tech_data, soft_score, self.criteria)
                results.append(final_res)
                
                self.metrics["total_processed"] += 1

            # 4. Ranking
            self.obs.transition("Ranking Candidates", State.RANKING)
            ranked = sorted(results, key=lambda x: x.total_score, reverse=True)
            for i, r in enumerate(ranked): r.rank = i + 1

            # 5. Reporting Agent (Only for Top 5 to save cost/time)
            self.obs.transition("Generating Detailed Reports", State.REPORTING)
            for r in ranked[:5]:
                report = self.recruiter.analyze(r, self.criteria)
                r.recruiter_summary = report["summary"]
                r.interview_questions = report["questions"]
            
            self.metrics["avg_score"] = round(sum(r.total_score for r in ranked)/len(ranked), 2) if ranked else 0
            self.metrics["total_time"] = round(time.time() - start_time, 2)
            self.obs.transition("Workflow Completed", State.COMPLETED, output_data={"metrics": self.metrics})
            return ranked

        except Exception as e:
            self.obs.transition(f"System Error: {str(e)}", State.ERROR)
            self.metrics["error"] = str(e)
            return []

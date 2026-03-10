import json
import uuid
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class State(Enum):
    IDLE = "IDLE"
    PARSING = "PARSING"
    SCORING = "SCORING"
    RANKING = "RANKING"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class LogEntry(BaseModel):
    timestamp: str
    run_id: str
    agent_name: str
    previous_state: Optional[str] = None
    event: Optional[str] = None
    next_state: Optional[str] = None
    input: Optional[Any] = None
    output: Optional[Any] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Any] = None
    tool_output: Optional[Any] = None
    thought: Optional[str] = None

class Observability:
    def __init__(self, run_id: str = None, log_file: str = "runs.jsonl"):
        self.run_id = run_id or str(uuid.uuid4())
        self.log_file = log_file
        self.current_state = State.IDLE
        self.agent_name = "ScreeningAgent"

    def log(self, entry: LogEntry):
        with open(self.log_file, "a") as f:
            f.write(entry.model_dump_json() + "\n")

    def transition(self, event: str, next_state: State, input_data: Any = None, output_data: Any = None):
        previous_state = self.current_state
        self.current_state = next_state
        
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            run_id=self.run_id,
            agent_name=self.agent_name,
            previous_state=previous_state.value,
            event=event,
            next_state=next_state.value,
            input=input_data,
            output=output_data
        )
        self.log(entry)

    def log_tool_call(self, tool_name: str, input_data: Any, output_data: Any, thought: Optional[str] = None):
        """
        Logs a tool call with an optional 'thought' (Internal Monologue).
        """
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            run_id=self.run_id,
            agent_name=self.agent_name,
            tool_name=tool_name,
            tool_input=input_data,
            tool_output=output_data,
            thought=thought or f"Executing {tool_name} to process data..."
        )
        self.log(entry)

class JobCriterion(BaseModel):
    name: str
    weight: float
    required_skills: Optional[List[str]] = None
    min_experience: Optional[int] = None
    education_keywords: Optional[List[str]] = None

class ScoringResult(BaseModel):
    resume_id: int
    candidate_name: str
    scores: Dict[str, float]
    total_score: float
    rank: Optional[int] = None
    recruiter_summary: Optional[str] = None
    interview_questions: Optional[List[str]] = None

from pydantic import BaseModel, Field

class Job(BaseModel):
    title: str = Field(..., description="The title of the job position.")
    company: str = Field(..., description="The company offering the job.")
    salary: int = Field(..., description="The salary for the job.")
    seniority: str = Field(..., description="The seniority level requested for the job.")
    modality: str = Field(..., description="Presential, hybrid, remote.")
    location: str = Field(..., description="The job's location.")
    description: str = Field(..., description="The job's description.")
    score: float = Field(..., description="Score defines how close to the desire job.")
    criteria_met: int = Field(..., description="Percentage of criteria met (skills, experience).")
    posted_date: str = Field(..., description="The date the job was posted.")

def scrap_job(parameters: dict) -> Job:
    
    pass

'''
Example of a Job object:
# Input JSON/dict
data = {
    "title": "Software Engineer",
    "salary": 120000,
    "location": "Remote",
    "company": "TechCorp",  # Extra field
    "posted_date": "2025-01-01"  # Another extra field
}
# Create a Job instance
job = Job(**data)

In case of not expected fields, these are ignored

'''
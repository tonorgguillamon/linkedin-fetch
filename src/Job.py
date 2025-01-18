from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class Job(BaseModel):
    title: str = Field(..., description="The title of the job position.")
    company: str = Field(..., description="The company offering the job.")
    salary: str = Field("", description="The salary for the job.") # str to keep the currency
    seniority: str = Field("", description="The seniority level requested for the job.")
    modality: str = Field("", description="Presential, hybrid, remote.")
    location: str = Field(..., description="The job's location.")
    description: str = Field(..., description="The job's description.")
    score: float = Field(0.0, description="Score defines how close to the desire job (criteria + modality + salary + seniority).")
    criteria_met: int = Field(0, description="Percentage of criteria met (skills, experience).")
    criteria_array: list = Field([], description="Stores 1 for keyword met and 0 else. Keeps the order.")
    posted_date: str = Field(..., description="The date the job was posted.")
    link_apply: str = Field(..., description="The link to apply for the job.")

    def calculate_criteria_met(self, keywords: list[str]):
        self.criteria_array = [1 if k in self.description.lower() else 0 for k in keywords]
        self.criteria_met = int(sum(self.criteria_array)/len(self.criteria_array)*100)

    def calculate_score(self):
        pass

def scrap_job(data: dict) -> Job:
    # Extract revlevant information from the parameters
    # See example in job_post_data.json
    job_data = {}

    # Company name:
    job_data['company'] = data.get('companyDetails', {}).get(
        'com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}
        ).get('companyResolutionResult', {}).get('name', 'Unknown')
    
    job_data['description'] = data.get('description', {}).get('text', 'Unknown')
    job_data['title'] = data.get('title', 'Unknown')
    job_data['link_apply'] = data.get('applyMethod', {}).get(
        'com.linkedin.voyager.jobs.ComplexOnsiteApply', {}
        ).get('easyApplyUrl', 'Unknown')
    
    modalities = ', '.join([wptype.strip(':')[-1] for wptype in data.get('workplaceTypes', []) if wptype])
    job_data['modality'] = modalities.replace("1", "on-site").replace("2", "remote").replace("3", "hybrid")
    
    listed_at = data.get('listedAt', 0)/1000 # convert from ms to s
    if listed_at != 0:
        posted_date = datetime.fromtimestamp(listed_at)
        job_data['posted_date'] = posted_date.strftime('%Y-%m-%d')
    else:
        job_data['posted_date'] = 'Unknown'
    
    job_data['location'] = data.get('formattedLocation', 'Unknown')

    return job_data

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
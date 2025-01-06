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
    score: float = Field(0.0, description="Score defines how close to the desire job.")
    criteria_met: int = Field(0, description="Percentage of criteria met (skills, experience).")
    posted_date: str = Field(..., description="The date the job was posted.")
    link_apply: str = Field(..., description="The link to apply for the job.")

def scrap_job(data: dict) -> Job:
    # Extract revlevant information from the parameters
    # See example in src/job_post_data.json
    job_data = {}

    # Company name:
    job_data['company'] = data['companyDetails'] \
                              ['com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany'] \
                              ['companyResolutionResult'] \
                              ['name']
    job_data['description'] = data['description']['text']
    job_data['title'] = data['title']
    job_data['link_apply'] = data['applyMethod'] \
                                  ['com.linkedin.voyager.jobs.ComplexOnsiteApply'] \
                                  ['easyApplyUrl']
    modalities = [wptype.strip(':')[-1] for wptype in data['workplaceTypes']]
    job_data['modality'] = ', '.join(modalities)
    
    posted_date = datetime.fromtimestamp(data['listedAt']/1000) # convert from ms to s
    job_data['posted_date'] = posted_date.strftime('%Y-%m-%d')
    
    job_data['location'] = data['formattedLocation']

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
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import re

class Job(BaseModel):
    jobId: str = Field(..., description="Job unique ID.")
    title: str = Field(..., description="The title of the job position.")
    company: str = Field(..., description="The company offering the job.")
    salary: str = Field("No", description="Discloses the salary?")
    seniority: list = Field([], description="The seniority level requested for the job. It can be more than one.")
    modality: set = Field(set(), description="Presential, hybrid, remote. It can be more than one.")
    location: str = Field(..., description="The job's location.")
    description: str = Field(..., description="The job's description.")
    score: float = Field(0.0, description="Score defines how close to the desire job (criteria + modality + salary + seniority).")
    criteria_met: int = Field(0, description="Percentage of criteria met (skills).")
    criteria_array: list = Field([], description="Stores 1 for keyword met and 0 else. Keeps the order.")
    posted_date: str = Field(..., description="The date the job was posted.")
    link_apply: str = Field(..., description="The link to apply for the job.")

    def calculate_criteria_met(self, skills: list[str]):
        self.criteria_array = [1 if k in self.description.lower() else 0 for k in skills]
        self.criteria_met = int(sum(self.criteria_array)/len(self.criteria_array)*100)

    def calculate_score(self):
        pass

    def mentions_salary(self, salary_keywords):
        if any(re.search(salary_kw, self.description.lower()) for salary_kw in salary_keywords):
            self.salary = "Yes"
    
    def get_seniority(self):
        if re.search(r'\bintern\b', self.title.lower()) or re.search(r'\bintern\b', self.description.lower()) \
                or re.search(r'\binternship\b', self.title.lower()) or re.search(r'\binternship\b', self.description.lower()):
            self.seniority.append("Intern")
        if re.search(r'\bjunior\b', self.title.lower()) or re.search(r'\bjunior\b', self.description.lower()):
            self.seniority.append("Junior")
        if re.search(r'\bmid\b', self.title.lower()) or re.search(r'\bmid\b', self.description.lower()) \
                or re.search(r'\bregular\b', self.title.lower()) or re.search(r'\bregular\b', self.description.lower()):
            self.seniority.append("Mid")
        if re.search(r'\bsenior\b', self.title.lower()) or re.search(r'\bsenior\b', self.description.lower()):
            self.seniority.append("Senior")
        if re.search(r'\bmanager\b', self.title.lower()) or re.search(r'\bmanager\b', self.description.lower()) \
                or re.search(r'\blead\b', self.title.lower()) or re.search(r'\blead\b', self.description.lower()):
            self.seniority.append("Manager")
        if re.search(r'\bexecutive\b', self.title.lower()) or re.search(r'\bexecutive\b', self.description.lower()):
            self.seniority.append("Executive")
        if not self.seniority:
            self.seniority.append("Unspecified")

    def get_modality(self):
        if any(re.search(k, self.description.lower()) for k in [r'\bpresential\b', r'\bon-site\b']):
            self.modality.add("Presential")
        if any(re.search(k, self.description.lower()) for k in [r'\bhybrid\b', r'\bin the office\b', r'\bper week\b']): #TODO: test this to also analyze the context
            self.modality.add("Hybrid")
        if any(re.search(k, self.description.lower()) for k in [r'\bremote\b', r'\bfull-remote\b']):
            self.modality.add("Remote")
        if not self.modality:
            self.modality.add("Unspecified")
        

def scrap_job(data: dict, id: str) -> Job:
    # Extract revlevant information from the parameters
    # See example in job_post_data.json
    job_data = {}
    # Job id
    job_data['jobId'] = id
    # Company name:
    job_data['company'] = data.get('companyDetails', {}).get(
        'com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}
        ).get('companyResolutionResult', {}).get('name', 'Unknown')
    
    job_data['description'] = data.get('description', {}).get('text', 'Unknown')
    job_data['title'] = data.get('title', 'Unknown')
    #job_data['link_apply'] = data.get('applyMethod', {}).get(
    #    'com.linkedin.voyager.jobs.ComplexOnsiteApply', {}
    #    ).get('easyApplyUrl', 'Unknown')
    
    job_data['link_apply'] = f'https://www.linkedin.com/jobs/search/?currentJobId={id}'
    
    job_data['modality'] = {wptype.strip(':')[-1].replace("1", "Presential").replace("2", "Remote").replace("3", "Hybrid") for wptype in data.get('workplaceTypes', []) if wptype}
    
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
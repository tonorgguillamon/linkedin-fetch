from src.Job import Job
from collections.abc import Iterable

class RequestPreferences:
    def __init__(self, title, experience, modality, jtype, location, skills):
        self.job_title = title.split(",")
        self.experience_level = experience
        self.modality = modality
        self.job_type = jtype
        self.location = location
        self.skills = skills.split(",")

class JobManager:
    def __init__(self, preferences: RequestPreferences):
        self.jobs = []
        self.preferences = preferences
        self.preferences.experience_level = [experience.replace("1", "Intern").replace("2", "Junior").replace("3", "Mid").replace("4", "Senior").replace("5", "Manager").replace("6", "Executive") for experience in preferences.experience_level if experience]
        self.preferences.modality = [m.strip(':')[-1].replace("1", "Presential").replace("2", "Remote").replace("3", "Hybrid") for m in preferences.modality if m]

    def translate_preferences():
        pass

    def add_job(self, job: Job):
        self.jobs.append(job)

    def get_jobs(self) -> list[Job]:
        return self.jobs
    
    def meet_filter(self, filter, param):
        # filter is what the user requested
        # param is what the job is actually stating
        print("FILTER: ")
        print(filter)
        print("\n PARAMETERS FROM JOB: ")
        print(param)

        if isinstance(filter, Iterable):
            if any(f in param for f in filter):
                return True
            else:
                return False
        else:
            if filter == param: # i.e. the filter is Salary, that can be Yes or No
                return True
            else:
                return False
    
    def get_requested_jobs(self) -> list[Job]:
        # Get only jobs that meet the filters (modality, seniority, etc)
        requested = []
        for job in self.jobs:
            if self.meet_filter(self.preferences.experience_level, job.seniority) and \
                        self.meet_filter(self.preferences.modality, job.modality):
                requested.append(job)
        return requested   
    
    def get_best_jobs(self, min_score) -> list[Job]:
        return [job for job in self.jobs if job.score >= min_score]

    def jobsAmount(self) -> int:
        return len(self.jobs)
    
    def criteriaJobs(self):
        for job in self.jobs:
            job.calculate_criteria_met(self.preferences.skills)

    def modalityJobs(self):
        for job in self.jobs:
            job.get_modality()

    def seniorityJobs(self):
        for job in self.jobs:
            job.get_seniority()
        
    def salaryJobs(self, salary_keywords):
        for job in self.jobs:
            job.mentions_salary(salary_keywords)
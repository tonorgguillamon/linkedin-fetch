from src.Job import Job

class JobManager:
    def __init__(self):
        self.jobs = []

    def add_job(self, job: Job):
        self.jobs.append(job)

    def get_jobs(self) -> list[Job]:
        return self.jobs
    
    def get_best_jobs(self, min_score) -> list[Job]:
        return [job for job in self.jobs if job.score >= min_score]

    def jobsAmount(self) -> int:
        return len(self.jobs)
    
    def set_keywords(self, keywords: str):
        self.keywords = keywords.split(",") # convert the str into a list to iterate over

    def criteriaJobs(self):
        for job in self.jobs:
            job.calculate_criteria_met(self.keywords)
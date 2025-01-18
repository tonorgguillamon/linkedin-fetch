from flask import Flask, render_template, request
from src.Job import Job, scrap_job
from src.JobManager import JobManager
import time

_REGION_ID = {'Europe':91000002,
              'North America':91000022,
              'Schengen':91000024,
              'Asia-Pacific and Japan':91000004,
              'Switzerland':106693272,
              'Nordic Countries':91000009,
              'Poland':105072130}

def get_job_ids(jobs):
    # Extract the job IDs from the jobs
    # i.e. {'trackingUrn': 'urn:li:jobPosting:4081854722',...}
    job_ids = []
    for job in jobs:
        job_ids.append(job['trackingUrn'].split(':')[-1])
    return job_ids

def map_location(region: str) -> int:
    return _REGION_ID.get(region)

def run_app(api):
    app = Flask(__name__, template_folder='../templates')

    @app.route('/')
    def index():
        # Pass the profile and companies data to the template
        return render_template('index.html', companies=None, jobs=None)

    @app.route('/search_companies', methods=['POST'])
    def search_companies():
        keywords = request.form['keywords']
        companies = api.search_companies([keywords])
        return render_template('index.html', companies=companies, jobs=None)

    @app.route('/search_jobs', methods=['POST'])
    def search_jobs():
        job_manager = JobManager()
        # Parameters to filter the search:
        job_title = request.form['job_title']
        experience_level = request.form.getlist('experience_level')
        modality = request.form.getlist('modality')
        job_type = request.form.getlist('job_type')
        location = map_location(request.form['location'])
        job_keywords = request.form['keywords']

        job_manager.set_keywords(job_keywords)

        jobs_fetched = api.search_jobs( keywords = job_title,
                                        experience = experience_level,
                                        job_type = job_type,
                                        remote = modality,
                                        location_geo_id = location,
                                        listed_at=1 * 24 * 60 * 60, limit=10, offset=0)
        job_ids = get_job_ids(jobs_fetched)
        for id in job_ids:
            job_info = api.get_job(id)
            job = Job(**scrap_job(job_info))
            job_manager.add_job(job)
            print(job.title)

        start_time = time.time()
        job_manager.criteriaJobs()
        end_time = time.time()

        print("Elapsed time calculating criteria Jobs: " + str(end_time-start_time))
            
        return render_template('jobs_search.html',
                               companies=None,
                               jobs=job_manager.get_jobs(),
                               jobs_count=job_manager.jobsAmount())

    @app.route('/company/<int:company_id>')
    def company_detail(company_id):
        # Get detailed information for a specific company
        company = api.get_company(company_id)
        return render_template('company_detail.html', company=company)
    
    return app # http://127.0.0.1:5000
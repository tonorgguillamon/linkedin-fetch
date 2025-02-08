from flask import Flask, render_template, request
from src.Job import Job, scrap_job
from src.JobManager import JobManager, RequestPreferences
import time
import concurrent.futures

_REGION_ID = {'Europe':91000002,
              'North America':91000022,
              'Schengen':91000024,
              'Asia-Pacific and Japan':91000004,
              'Switzerland':106693272,
              'Nordic Countries':91000009,
              'Poland':105072130,
              'Spain':105646813}

#TODO: $ is misdetected!
_SALARY_KEYWORDS = [
                    r'\bsalary\b',
                    r'\bcompensation\b',
                    r'\b€\b',
                    r'\beuro\b',
                    #r'\b$\b',
                    r'\bdollars\b',
                    r'\bplm\b',
                    r'\bzl\b',
                    r'\bzlotys\b',
                    r'\b£\b',
                    r'\bpounds\b',
                    r'\bCHF\b'
]

_QUALITY_KEYWORDS = [
                    r'\bflexible\b',
                    r'\btraining\b',
                    r'\bmultisport\b',
                    r'\bhealthcare\b',
                    r'\bpension\b',
                    r'\blife insurance\b',
                    r'\bhealth insurance\b',
                    r'\btax deductible costs\b',
                    r'\btax-deductible costs\b',
                    r'\bmedical insurance\b',
                    r'\brelocation support'
]

def get_job_ids(jobs) -> str:
    # Extract the job IDs from the jobs
    # i.e. {'trackingUrn': 'urn:li:jobPosting:4081854722',...}
    job_ids = set()
    for job in jobs:
        job_ids.add(job['trackingUrn'].split(':')[-1])
    return job_ids

def map_location(region: str) -> int:
    return _REGION_ID.get(region)

def multiple_search_calls(api, filters):
    def search_jobs_call(**kwargs):
        return api.search_jobs(**kwargs)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for job_title in filters.job_title:
            futures.append(executor.submit(search_jobs_call, 
                                           keywords=job_title,
                                           experience=filters.experience_level,
                                           job_type=filters.job_type,
                                           remote=filters.modality,
                                           location_geo_id=filters.location,
                                           listed_at=1 * 24 * 60 * 60, limit=10, offset=0))
            futures.append(executor.submit(search_jobs_call, 
                                           keywords=job_title,
                                           job_type=filters.job_type,
                                           location_geo_id=filters.location,
                                           listed_at=1 * 24 * 60 * 60, limit=10, offset=0))
            futures.append(executor.submit(search_jobs_call, 
                                           keywords=job_title,
                                           location_geo_id=filters.location,
                                           listed_at=1 * 24 * 60 * 60, limit=10, offset=0))

        fetched = []
        for future in concurrent.futures.as_completed(futures):
            fetched.extend(future.result())

    return fetched

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

        requestPreferences = RequestPreferences(
            request.form['job_title'],
            request.form.getlist('experience_level'),
            request.form.getlist('modality'),
            request.form.getlist('job_type'),
            map_location(request.form['location']),
            request.form['keywords']
        )
        jobManager = JobManager(requestPreferences)
        # The LinkedIn search doesn't always stick to the filters set.
        # To cover wider spectrum of jobs, there are multiple calls to it,
        # modifiying few of the parameters:
        jobs_fetched = multiple_search_calls(api, requestPreferences)
        job_ids = get_job_ids(jobs_fetched)

        for id in job_ids:
            job_info = api.get_job(id)
            job = Job(**scrap_job(job_info, id))
            jobManager.add_job(job)
            print(job.title)

        start_time = time.time()
        jobManager.criteriaJobs()
        jobManager.modalityJobs()
        jobManager.seniorityJobs()
        jobManager.salaryJobs(_SALARY_KEYWORDS)
        end_time = time.time()

        print("Elapsed time calculating criteria Jobs: " + str(end_time-start_time))
        # https://www.linkedin.com/job-apply/4115964225
        # https://www.linkedin.com/jobs/search/?currentJobId=4115964225

        
        return render_template('jobs_search.html',
                               companies=None,
                               jobs=jobManager.get_requested_jobs(),
                               jobs_count=jobManager.jobsAmount())

    @app.route('/company/<int:company_id>')
    def company_detail(company_id):
        # Get detailed information for a specific company
        company = api.get_company(company_id)
        return render_template('company_detail.html', company=company)
    
    return app # http://127.0.0.1:5000
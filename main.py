#https://github.com/tomquirk/linkedin-api
#https://www.jcchouinard.com/linkedin-api/
#https://linkedin-api.readthedocs.io/en/latest/api.html
# Jinja2 to embed Python-like expressions in HTML
#https://www.reddit.com/r/linkedin/comments/1avdudu/i_simply_cant_fathom_how_bad_linkedins_job_search/?rdt=62767

from linkedin_api import Linkedin
import json
from flask import Flask, render_template, request, redirect, url_for

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Authenticate using any Linkedin user account credentials
api = Linkedin(config['username'], config['password'])

#print('------------------- JOB -------------------')
#print(json.dumps(api.get_job('4112864647'), indent=4))

app = Flask(__name__)

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
    keywords = request.form['keywords']
    jobs = api.search_jobs(keywords)
    return render_template('index.html', companies=None, jobs=jobs)

@app.route('/company/<int:company_id>')
def company_detail(company_id):
    # Get detailed information for a specific company
    company = api.get_company(company_id)
    return render_template('company_detail.html', company=company)

if __name__ == '__main__':
    app.run(debug=True)
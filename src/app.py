from flask import Flask, render_template, request

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
        keywords = request.form['keywords']
        jobs = api.search_jobs(keywords, listed_at=15 * 24 * 60 * 60, limit=3000, offset=800)
        print("Number of jobs found: " + str(len(jobs)))
        return render_template('index.html', companies=None, jobs=jobs)

    @app.route('/company/<int:company_id>')
    def company_detail(company_id):
        # Get detailed information for a specific company
        company = api.get_company(company_id)
        return render_template('company_detail.html', company=company)
    
    return app # http://127.0.0.1:5000
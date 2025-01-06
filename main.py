#https://github.com/tomquirk/linkedin-api
#https://www.jcchouinard.com/linkedin-api/
#https://linkedin-api.readthedocs.io/en/latest/api.html
# Jinja2 to embed Python-like expressions in HTML
#https://www.reddit.com/r/linkedin/comments/1avdudu/i_simply_cant_fathom_how_bad_linkedins_job_search/?rdt=62767

from linkedin_api import Linkedin
import json
from src.app import run_app
from src.custom_linkedin import CustomLinkedin

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Authenticate using any Linkedin user account credentials
api = Linkedin(config['username'], config['password'])

#print('------------------- JOB -------------------')
#print(json.dumps(api.get_job('4112864647'), indent=4))

app = run_app(api)

if __name__ == '__main__':
    app.run(debug=True)
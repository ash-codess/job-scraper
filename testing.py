import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import plotly.express as px
from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
 
app = Flask(__name__)
 
# Download required NLTK resources
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
 
stop_words = set(stopwords.words('english'))
 
def extract_skills(description):
    skills = []
    tokens = word_tokenize(description.lower())
    tagged_tokens = pos_tag(tokens)
    
    for token, tag in tagged_tokens:
        if tag.startswith('NN') and token not in stop_words:
            skills.append(token)
    
    return skills
 
def extract_jobs_from_linkedin(search_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    job_elems = soup.find_all('div', class_='base-card')
    for job_elem in job_elems:
        title_elem = job_elem.find('h3', class_='base-search-card__title')
        company_elem = job_elem.find('h4', class_='base-search-card__subtitle')
        location_elem = job_elem.find('span', class_='job-search-card__location')
        description_elem = job_elem.find('div', class_='job-card-container__description')
        if None in (title_elem, company_elem, location_elem, description_elem):
            continue
        title = title_elem.text.strip()
        company = company_elem.text.strip()
        location = location_elem.text.strip()
        if 'India' not in location:
            continue
        description = description_elem.text.strip()
        job_url = job_elem.find('a')['href']
        jobs.append({'title': title, 'company': company, 'location': location, 'description': description, 'url': job_url})
    return pd.DataFrame(jobs)
 
@app.route('/visualize')
def visualize_jobs():
    search_url = 'https://www.linkedin.com/jobs/search/?keywords=data%20engineer&location=India'
    jobs_df = extract_jobs_from_linkedin(search_url)
    
    # Save job data to CSV
    jobs_df.to_csv('linkedin_data_engineer_jobs.csv', index=False)
    
    # Extract skills from job descriptions
    jobs_df['skills'] = jobs_df['description'].apply(extract_skills)
    
    # Flatten the list of skills
    skills_list = [skill for skills in jobs_df['skills'] for skill in skills]
    
    # Count the occurrences of each skill
    skill_counts = pd.Series(skills_list).value_counts()
    
    # Create a bar chart
    fig = px.bar(x=skill_counts.index, y=skill_counts.values, title="Demand for Data Engineering Skills on LinkedIn in India")
    
    # Convert the plotly figure to HTML
    graphHTML = fig.to_html(full_html=False)
    
    return render_template('visualize.html', graphHTML=graphHTML)
 
@app.route('/')
def index():
    return render_template('index.html')
 
if __name__ == '__main__':
    app.run(debug=True)

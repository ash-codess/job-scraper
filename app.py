from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import plotly.express as px
import re
 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def extract_skills(title):
    skills = []
    title = title.lower()
    
    if 'python' in title:
        skills.append('python')
    if 'sql' in title:
        skills.append('sql')
    if 'aws' in title:
        skills.append('aws')
    if 'hadoop' in title:
        skills.append('hadoop')
    if 'spark' in title:
        skills.append('spark')
    if 'pysaprk' in title:
        skills.append('pyspark')
    
    # You can add more skills to look for here
    
    return skills
 
# Web Scraping function
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
        
        if None in (title_elem, company_elem, location_elem):
            continue
        
        title = title_elem.text.strip()
        company = company_elem.text.strip()
        location = location_elem.text.strip()
        if 'India' not in location:
            continue
        job_url = job_elem.find('a')['href']
        
        jobs.append({'title': title, 'company': company, 'location': location, 'url': job_url})
        
    return pd.DataFrame(jobs)


@app.route('/scrape')
def scrape_jobs():
    search_url = 'https://www.linkedin.com/jobs/search/?keywords=data%20engineer&location=India'
    jobs_df = extract_jobs_from_linkedin(search_url)
    jobs_df.to_csv('linkedin_data_engineer_jobs.csv', index=False)
    return jsonify(jobs_df.to_dict(orient='records'))


@app.route('/visualize')
def visualize_jobs():
    jobs_df = pd.read_csv('linkedin_data_engineer_jobs.csv')
    top_skills = ['python', 'sql', 'aws', 'hadoop', 'spark']
    for skill in top_skills:
        jobs_df[skill] = jobs_df['title'].apply(lambda x: skill.lower() in x.lower())
    
    skill_counts = jobs_df[top_skills].sum().sort_values(ascending=False)
    fig = px.bar(
        skill_counts,
        x=skill_counts.index,
        y=skill_counts.values,
        title="Demand for Top Data Engineering Skills on LinkedIn",
        labels={"x": "Skills", "y": "Number of Job Listings"},
        template="plotly_dark"
    )
    graphJSON = fig.to_json()
 
    return render_template('visualize.html', graphJSON=graphJSON)

 
if __name__ == '__main__':
    app.run(debug=True)




# jobTitle css-198pbd eu4oa1w0
# jobTitle css-198pbd eu4oa1w0 - title

# css-1qv0295 e37uo190
# css-1qv0295 e37uo190 -  name company

# css-1p0sjhy eu4oa1w0
# css-1p0sjhy eu4oa1w0 - location
import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Set up WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  
#download cromedriver.exe
#hey recruiter to run in your system use your file location
service = Service(r"c:\tools\chromedriver\chromedriver-win32\chromedriver.exe")  
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL List
urls = [
    "https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_TPR=r86400&f_C=1586&position=1&pageNum=0"
]

job_list = []

for url in urls:
    driver.get(url)
    time.sleep(3)  

    
    for _ in range(5): 
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2) 

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_cards = soup.find_all('div', class_='job-search-card')

    for job in job_cards:
        company_name = job.find('h4', class_='base-search-card__subtitle').get_text(strip=True)
        job_title = job.find('h3', class_='base-search-card__title').get_text(strip=True)
        location = job.find('span', class_='job-search-card__location').get_text(strip=True)
        job_url = job.find('a', class_='base-card__full-link')['href']
        linkedin_job_id = job_url.split('/')[-2]

       
        posted_on_element = job.find('time')
        if posted_on_element and 'datetime' in posted_on_element.attrs:
            posted_on = posted_on_element['datetime']
            
            try:
                
                if 'day' in posted_on:
                    days_ago = int(posted_on.split(' ')[1])
                    posted_date = (datetime.today() - timedelta(days=days_ago)).strftime('%d-%m-%Y')
                elif 'hour' in posted_on:
                    posted_date = datetime.today().strftime('%d-%m-%Y')
                else:
                    posted_date = 'unknown'
            except (IndexError, ValueError):
                posted_date = 'unknown'
        else:
            posted_date = 'unknown'

        
        seniority_level = job.find('span', class_='job-search-card__seniority-level').get_text(strip=True) if job.find('span', class_='job-search-card__seniority-level') else 'null'
        employment_type = job.find('span', class_='job-search-card__employment-type').get_text(strip=True) if job.find('span', class_='job-search-card__employment-type') else 'null'

        job_list.append({
            "company_name": company_name,
            "linkedin_job_id": linkedin_job_id,
            "job_title": job_title,
            "location": location,
            "posted_on": posted_on if posted_on else 'null',
            "posted_date": posted_date,
            "seniority_level": seniority_level,
            "employment_type": employment_type
        })

    time.sleep(2)  

driver.quit()

# Save to JSON
with open('job_postings.json', 'w') as f:
    json.dump(job_list, f, indent=4)

# Save to CSV
df = pd.DataFrame(job_list)
df.to_csv('job_postings.csv', index=False)

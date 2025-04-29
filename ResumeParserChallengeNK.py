import pdfplumber
import easyocr
import re
import os
import logging
from collections import defaultdict
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Extract text using pdfplumber
def extract_text_with_pdfplumber(path):
    text = ''
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
    except Exception as e:
        logging.warning(f"PDFPlumber extraction failed: {e}")
    return text.strip()


# Extract text using easyOCR (for image-based PDFs)
def extract_text_with_easyocr(path):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(path, detail=0)
    text = ' '.join(results)
    return text


# Decide whether to use pdfplumber or EasyOCR
def extract_text(path):
    text = extract_text_with_pdfplumber(path)
    if len(text.strip()) < 50:  # If too little text, assume it's image-based
        logging.info("Switching to OCR extraction with EasyOCR.")
        text = extract_text_with_easyocr(path)
    return text


# Normalize date ranges (like "Jan 2020 - Mar 2022")
def normalize_dates(date_text):
    try:
        date_range = re.findall(r'(\w+\s\d{4})\s*-\s*(\w+\s\d{4})', date_text)
        if date_range:
            start_date = datetime.strptime(date_range[0][0], "%b %Y")
            end_date = datetime.strptime(date_range[0][1], "%b %Y")
            return f"{start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}"
    except Exception as e:
        logging.warning(f"Date normalization failed: {e}")
    return date_text


# Smart skill extractor even from sentences
def extract_skills(text, skill_list):
    found_skills = []
    for skill in skill_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.append(skill)
    return list(set(found_skills))


# Extract structured data from text
def extract_resume_data(text):
    fields = {
        "name": (None, 0),
        "email": (None, 0),
        "phone": (None, 0),
        "linkedin": (None, 0),
        "GitHub": (None, 0),
        "skills": ([], 0),
        "education": ([], 0),
        "experience": ([], 0),
        "certifications": ([], 0),
        "projects": ([], 0)
    }

    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    # 1. Extract Name (first non-empty line)
    if lines:
        fields["name"] = (lines[0], 1)

    # 2. Extract Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        fields["email"] = (email_match.group(0), 1)

    # 3. Extract Phone
    phone_match = re.search(r'\b\d{10}\b', text)
    if phone_match:
        fields["phone"] = (phone_match.group(0), 1)

    # 4. Extract LinkedIn
    linkedin_match = re.search(r'https?://www\.linkedin\.com/in/[^\s]+', text)
    if linkedin_match:
        fields["linkedin"] = (linkedin_match.group(0), 1)

    # 5. Extract Github
    GitHub_match = re.search(r'https?://github.com/[^\s]+', text)
    if GitHub_match:
        fields["GitHub"] = (GitHub_match.group(0), 1)

    # 6. Extract Skills
    skills_keywords = [
        'python', 'java', 'c++', 'javascript', 'machine learning', 'data analysis', 'sql',
        'html', 'css', 'excel', 'pandas', 'numpy', 'matplotlib', 'scikit-learn',
        'postgresql', 'mongodb', 'streamlit', 'easyocr', 'nltk', 'llms', 'communication'
    ]
    extracted_skills = extract_skills(text, skills_keywords)
    if extracted_skills:
        fields["skills"] = (extracted_skills, 1)

    # 7. Extract Education
    education_entries = re.findall(r'(.+?),\s*(.+?),\s*(\d{4})\s*[–-]\s*(\d{4})', text)
    if education_entries:
        edu_list = []
        for entry in education_entries:
            degree = entry[0].strip()
            institution = entry[1].strip()
            start_year = entry[2].strip()
            end_year = entry[3].strip()
            edu_list.append({
                "degree": degree,
                "institution": institution,
                "year": f"{start_year} - {end_year}"
            })
        fields["education"] = (edu_list, 1)

    # 8. Extract Certifications
    certifications_section = re.search(r'Certifications\s*(.*?)(Projects|Skills|$)', text, re.S | re.I)
    if certifications_section:
        certs = [line.strip() for line in certifications_section.group(1).split('\n') if line.strip()]
        if certs:
            fields["certifications"] = (certs, 1)

    # 9. Extract Projects
    projects_section = re.search(r'Projects\s*(.*)', text, re.S | re.I)
    if projects_section:
        project_text = projects_section.group(1)
        project_blocks = re.split(r'\n(?=[A-Z][^\n]{3,100}:)', project_text)
        projects = []
        for project in project_blocks:
            project_lines = project.strip().split('\n')
            if project_lines:
                title = project_lines[0].strip(': ')
                description = ' '.join(project_lines[1:]).strip()
                projects.append({
                    "title": title,
                    "description": description
                })
        if projects:
            fields["projects"] = (projects, 1)

    # Log missing fields
    for key, (value, score) in fields.items():
        if not value or (isinstance(value, list) and not value):
            fields[key] = (None, 0)
            logging.warning(f"Missing field detected: {key}")

    return fields


# Master function to parse the resume
def parse_resume(path):
    text = extract_text(path)
    structured_data = extract_resume_data(text)

    # Convert to final format
    final_data = {}
    for key, (value, score) in structured_data.items():
        final_data[key] = {
            "value": value,
            "confidence": score
        }
    return final_data


# Example usage
resume_path = "/content/NitishKumar_A_Resume (1).pdf"  # your uploaded file
parsed_resume = parse_resume(resume_path)

import json
print(json.dumps(parsed_resume, indent=2))
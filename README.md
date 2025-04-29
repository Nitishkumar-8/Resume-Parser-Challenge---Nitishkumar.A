# 📄 Intelligent Resume Parser

This project is a resume parsing system developed for the **Neurabit Take-Home Challenge**. It extracts structured information from resumes (in PDF format) using text extraction and rule-based parsing logic. The system handles both **text-based** and **image-based** resumes (using OCR), providing field-wise **confidence scores**, and logs missing data intelligently.

---

## ✅ Features

- ✔️ Extracts key resume fields:
  - Full Name  
  - Email  
  - Phone Number  
  - LinkedIn URL  
  - Skills (list)  
  - Education (degree, institution, start–end year)  
  - Certifications  
  - Projects (title + description)
- ✔️ Confidence score (0–1) per field
- ✔️ Logs missing fields cleanly
- ✔️ Works for both text and image-based PDFs
- ✔️ Normalizes inconsistent date formats (e.g., `Jan 2020 - Mar 2022`)
- ✔️ Extracts skills intelligently, even from sentences

---

## 🧠 Approach

1. **Text Extraction**  
   - Uses `pdfplumber` for text-based PDFs  
   - Falls back to `easyocr` if text content is too short (indicating image-based PDF)

2. **Information Extraction**  
   - Uses regex and keyword matching for structured field detection
   - Education entries are parsed with proper start–end year range
   - Skills are extracted from both lists and sentences

3. **Confidence Scoring**  
   - A score of `1` is assigned when a field is confidently matched
   - A score of `0.8` is used for heuristic matches (e.g., name from top line)
   - A score of `0` is assigned if a field is missing

4. **Logging**  
   - Missing fields are logged for transparency and debugging

---

## 📦 Requirements


+ pip install pdfplumber
+ pip install easyocr
+ pip install numpy
+ pip install Pillow


---

## 🧪 Example Output

{
  "name": {
    "value": "NitishKumar A",
    "confidence": 1
  },
  
  "email": {
    "value": "nitish1978053@gmail.com",
    "confidence": 1
  },
  
  "phone": {
    "value": "8610673212",
    "confidence": 1
  },
  
  "linkedin": {
    "value": "https://www.linkedin.com/in/nitish-kumar-a-462869145/",
    "confidence": 1
  },
  
  "skills": {
    "value": ["Python", "Pandas", "Machine Learning", "..."],
    "confidence": 1
  },
  
  "education": {
    "value": [
      {
        "degree": "MBA (Finance and Business Analyst)",
        "institution": "Panimalar Engineering College",
        "year": "2021 - 2023"
      }
    ],
    "confidence": 1
  },
  
  "certifications": {
    "value": ["Google's Project Management", "..."],
    "confidence": 1
  },
  
  "projects": {
    "value": [
      {
        "title": "Youtube Data Harvesting Project",
        "description": "Retrieval of channel and video data from YouTube using the YouTube API..."
      }
    ],
    "confidence": 1
  }
}

---

## 🙌 Credits

Created as part of the **Neurabit Intelligent Resume Parsing Challenge**.  
Developed by **NitishKumar.A**.

"""

# Kandidex

Kandidex is an AI-powered candidate evaluation platform developed to streamline and enhance the hiring process by analyzing and summarizing interview documents using NLP techniques. This project consists of a **Python Flask backend** and a **React frontend**.

---

## 🚀 Features

- Upload interview documents (TXT, DOCX, PDF).
- Summarize candidate responses using AI (LLM-based).
- Clean and responsive frontend for document upload.
- Backend API for extracting and processing interview data.

---

## 🛠️ Tech Stack

**Frontend**:  
- React.js  
- HTML, CSS  

**Backend**:  
- Python (Flask)  
- LLM integration for summarization (e.g., LLaMA prompt)  
- Text extraction (PDF, DOCX, TXT)

---

## 📁 Project Structure
kandidex/
├── candidate-evaluation/             # Backend
│   ├── app.py                        # Main Flask app
│   ├── requirements.txt              # Python dependencies
│   └── utils/                        # Text extraction & summarization scripts
├── interview-evaluation-frontend/    # Frontend
│   ├── src/components/UploadForm.js  # Upload component
│   └── public/index.html             # React entry point

---

## ⚙️ How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/YeshwanthMotivity/Kandidex.git
cd Kandidex

### 2. Backend Setup (Python + Flask)
cd candidate-evaluation
python -m venv venv
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
python app.py

### 3. Frontend Setup (React)
cd ../interview-evaluation-frontend
npm install
npm start

---
### 📬 Contact
For questions, reach out at:
📧 yeshwanth.mudimala@motivitylabs.com

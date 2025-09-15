# Kandidex
Kandidex is an AI-powered candidate evaluation platform designed to streamline and enhance the hiring process. It achieves this by automatically analyzing and summarizing interview documents, allowing recruiters and hiring managers to quickly grasp key information and make informed decisions. The project is built with a Python Flask backend and a React frontend, offering a complete, full-stack solution.

---

## 🚀 Features

1. **Document Upload**: Easily upload interview documents in various formats, including .TXT, .DOCX, and .PDF.
2. **AI-Powered Summarization**: Uses a Large Language Model (LLM) to extract and summarize key points from interview transcripts and documents.
3. **Responsive User Interface**: Provides a clean and intuitive frontend for a seamless user experience.
4. **Robust Backend API**: Manages document processing, text extraction, and communication with the LLM for efficient data handling.

---

### 🛠️ Tech Stack

### **Frontend**

|   Component   |   Technology |
| ------------- | ------------ |
| **Framework** | `React.js`   |
| **Styling**   | `HTML`, `CSS`|


### **Backend**

|   Component        |              Technology             |
| ------------------ | ----------------------------------- |
| **Framework**      | `Python (Flask)`                    |
| **AI/NLP**         | `LLM Integration` (e.g., LLaMA)     |
| **Text Extraction**| `PDF`, `DOCX`, `TXT` libraries      |

-----

### 📁 Project Structure

```
kandidex/
├── candidate-evaluation/         # Backend
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   └── utils/                    # Helper scripts for text extraction & summarization
└── interview-evaluation-frontend/    # Frontend
    ├── src/
    │   └── components/UploadForm.js  # React upload component
    └── public/
        └── index.html            # Main React entry point
```
---
## 📸 Architecture Diagram
<img width="2000" height="1125" alt="image" src="https://github.com/user-attachments/assets/acb340b9-94c2-48ac-8ac5-0f9e101a4756" />

---
## ⚙️ How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/YeshwanthMotivity/Kandidex.git
cd Kandidex
```

### 2. Backend Setup (Python + Flask)
```
cd candidate-evaluation
python -m venv venv
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
python app.py

```
### 3. Frontend Setup (React)
```
cd ../interview-evaluation-frontend
npm install
npm start
```
### 4. Ollama Setup
Since Kandidex uses a local LLM, you must have Ollama installed and the LLaMA 3 (8B) model pulled locally.
1. Install Ollama: Follow the instructions at https://ollama.com.
2. Pull the model:
   ```
   ollama pull llama3:8b
   ```
---
### 📈 Future Scope
The project has been planned for several future enhancements to improve its functionality and scalability.
1. **Deployment**: Containerize the application with Docker and deploy it to cloud platforms like Azure or GCP for greater scalability and reliability.
2. **Database Integration**: Implement a database system (e.g., PostgreSQL, MongoDB) for persistent storage of user interactions, logs, and model outputs.
3. **AI Enhancements**: Fine-tune the LLM with domain-specific data, implement a prompt management system, and add a caching layer to reduce latency for repeated queries.
4. **API Enhancements**: Use an async task queue (e.g., Celery) for heavy computations and separate the LLM into a microservice.
   
---

**Author**

Mentor / Manager:
Mr. Venkata Ramana Sudhakar Polavarapu

Team Members:
 Yeshwanth Goud Mudimala, Sai Dinesh Bejjanki, Uma Venkata Karthik Vallabhaneni, Pushpaja Udayagiri, Sai Seetu Reddy Bommareddy

---
### 📬 Contact
For questions or collaboration, you can reach out at:

**Email 📧** : yeshwanth.mudimala@motivitylabs.com

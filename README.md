**AI-Based Plagiarism Detection System**

An NLP-powered plagiarism detection web application built using Flask and Machine Learning techniques. The system analyzes uploaded documents, compares them with stored reference documents, and detects document-level as well as sentence-level similarity.

**🚀 Features**
User Authentication (Login/Register/Logout)
Upload and analyze .txt, .docx, and .pdf files
NLP-based text preprocessing using NLTK
TF-IDF Vectorization for text representation
Cosine Similarity for plagiarism detection
Sentence-level similarity matching
SQLite database integration
Secure password hashing
Responsive Flask web interface
Deployed on Google Cloud Platform (GCP)

**🛠️ Tech Stack**
Backend: Python, Flask
Database: SQLite
Machine Learning: Scikit-learn
NLP: NLTK
File Processing: PyPDF2, python-docx
Deployment: Google Cloud Platform (GCP)

**📂 Supported File Formats**
.txt
.docx
.pdf

**⚙️ Installation**

Clone the repository:

git clone <your-repository-link>
cd plagiarism-detection-system

Install dependencies:

pip install -r requirements.txt

Download NLTK resources:

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

Run the application:

python app.py

**📊 How It Works**
User uploads a document
Text is extracted and preprocessed
TF-IDF converts text into numerical vectors
Cosine similarity calculates similarity score
Matching sentences and plagiarism percentage are displayed

**🔐 Security Features**
Password hashing using Werkzeug
Session-based authentication
Secure database handling
**
🌐 Deployment**

The project is deployed on Google Cloud Platform (GCP) for scalable and reliable access.

**📸 Future Enhancements**
AI-based semantic plagiarism detection
PDF report generation
Multiple document comparison
Improved UI/UX dashboard
Real-time plagiarism highlighting

**👨‍💻 Author**

Developed by Yash Vaswani as an NLP and Machine Learning based project.

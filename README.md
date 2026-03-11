# 📄 Resume Screening Assistant

A high-performance, **Multi-Agent RAG System** designed to automate and intelligently rank candidate resumes using **Deep LLM Reasoning**.

---

## 🚀 Key Features

- **🔐 Secure Authentication**: Persistent Login/Signup with Email support.
- **🤖 Multi-Agent Brain**: 4 specialized agents (Technical, SoftSkills, Auditor, Recruiter) working in a coordinated state machine.
- **📁 PDF Persistence**: Real PDF resumes are uploaded, parsed, and permanently stored on the server.
- **🧠 Semantic Matching (RAG)**: Uses a simulated Vector Database for intelligent skill-matching, moving beyond simple keyword search.
- **📊 Circular Visual Analytics**: Advanced dashboard with Gauge Meters, Radar Charts, and Bubble visualizations.
- **📝 Automated Reporting**: One-click exports to **PDF, Word (DOCX), CSV, and JSON**.
- **🕵️ Full Observability**: Real-time tracking of agent thoughts, tool logs, and state transitions (JSONL compliant).
- **⚡ High Performance**: Optimized execution engine (< 0.15s per run).

---

## 🏗️ Architecture

The system follows a **Decentralized Multi-Agent State Machine**:
1. **Parser**: Extracts structured data from PDF.
2. **Technical Agent**: Evaluates tech stack using semantic synonyms and deep reasoning.
3. **Soft Skills Agent**: Role-aware analysis of leadership and behavioral traits.
4. **Auditor Agent**: Consolidates scores using weighted logic.
5. **Recruiter Agent**: Generates final recommendations and tailored interview questions.

---

## 🛠️ Tech Stack

- **Frontend/Dashboard**: [Streamlit](https://streamlit.io/)
- **Core Language**: Python 3.8+
- **Data Visualization**: Plotly, Pandas, Matplotlib
- **Export Engines**: FPDF2, Python-Docx
- **Infrastructure Simulation**: RAG-lite (Vector Store), Mock LLM (GPT-4 logic)
- **Logging**: JSON Lines (JSONL)

---

## 📥 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd resume
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

---

## 🛡️ Security & Privacy

- **User Data**: Stored locally in `users.json`.
- **Uploaded Resumes**: Stored in `uploaded_resumes/` folder.
- **Privacy**: `.gitignore` ensures your user credentials and resume files are never pushed to GitHub.

---

## 🤝 Contributing

Feel free to open issues or pull requests for any enhancements!

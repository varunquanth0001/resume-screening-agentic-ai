# 📄 Enterprise AI Resume Screening Agent

A high-performance, **Multi-Agent RAG System** designed to automate and intelligently rank candidate resumes using **Deep LLM Reasoning**.

---

## 🚀 Key Features

- **🔐 Enterprise Authentication**: Secure Login/Signup with persistent user storage.
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
4. **Auditor Agent**: Consolidates scores using weighted enterprise logic.
5. **Recruiter Agent**: Generates final recommendations and tailored interview questions.

---

## 🛠️ Tech Stack

- **Frontend/Dashboard**: [Streamlit](https://streamlit.io/)
- **Core Language**: Python 3.8+
- **Data Visualization**: Plotly, Pandas
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

2. **Install Dependencies**:
   ```bash
   pip install streamlit pandas plotly fpdf2 python-docx pydantic faker pycryptodome python-dotenv kaleido PyPDF2
   ```

3. **Configure Environment**:
   Create a `.env` file (optional for mock mode):
   ```env
   OPENAI_API_KEY=your_key_here
   ```

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

---

## 📖 Usage Guide

1. **Register**: Create an account on the Signup page.
2. **Configure**: Select a job scenario (e.g., DevOps, Data Scientist) in the sidebar.
3. **Upload**: Select "Upload PDFs" and add your candidate resumes.
4. **Screen**: Click "Start Screening Run" to trigger the multi-agent workflow.
5. **Review**: Analyze the visual charts and detailed candidate deep-dives.
6. **Export**: Download the final professional report in your preferred format.

---

*Built with ❤️ by Varun & Agent Assistant*

# 📊 Nifty100 Financial Intelligence Platform

A comprehensive financial analytics platform for the Nifty 100 companies, built using Python, SQLite, Streamlit, FastAPI, and Machine Learning.

The platform ingests financial statements, validates data quality, computes 50+ financial KPIs, performs company screening and peer comparison, generates interactive dashboards, exposes REST APIs, and produces automated PDF reports.

---

## 🚀 Project Objectives

- Build a centralized financial intelligence database for Nifty 100 companies.
- Automate ETL and data validation.
- Calculate 50+ financial ratios and KPIs.
- Develop an intelligent stock screener.
- Perform peer comparison and sector analysis.
- Create an interactive Streamlit dashboard.
- Expose financial data through REST APIs.
- Generate professional PDF financial reports.
- Apply Machine Learning for company clustering and statistical analysis.

---

## 🛠 Tech Stack

### Programming
- Python 3.x

### Data Processing
- Pandas
- NumPy
- OpenPyXL

### Database
- SQLite
- SQLAlchemy

### Visualization
- Plotly
- Matplotlib
- Streamlit

### API
- FastAPI
- Uvicorn

### Machine Learning
- Scikit-learn
- SciPy
- NLTK

### Reporting
- ReportLab

### Testing & Quality
- Pytest
- Black
- Ruff
- Pre-Commit

---

## 📁 Project Structure

```
Nifty100_Financial_Intelligence_Platform/
│
├── config/
├── data/
│   ├── raw/
│   ├── processed/
│   └── supporting/
│
├── db/
├── logs/
├── notebooks/
├── output/
├── reports/
├── src/
│   ├── analytics/
│   ├── api/
│   ├── dashboard/
│   ├── etl/
│   └── utils/
│
├── tests/
│   ├── analytics/
│   ├── api/
│   └── etl/
│
├── .env.example
├── Makefile
├── README.md
└── requirements.txt
```

---

## 📅 Development Roadmap

### ✅ Sprint 1 – Data Foundation
- Project setup
- Excel Loader
- Data Normalization
- Data Validation
- SQLite Database
- ETL Pipeline

### ⏳ Sprint 2 – Financial Ratio Engine
- Profitability Ratios
- Leverage Ratios
- Growth Metrics
- Cash Flow Analytics

### ⏳ Sprint 3 – Screener & Peer Comparison
- Stock Screener
- Ranking Engine
- Peer Analytics

### ⏳ Sprint 4 – Dashboard & Valuation
- Streamlit Dashboard
- Company Profile
- Sector Analysis
- Valuation Module

### ⏳ Sprint 5 – Intelligence & Reports
- Cash Flow Intelligence
- NLP Module
- Automated PDF Reports

### ⏳ Sprint 6 – API, ML & Testing
- FastAPI
- K-Means Clustering
- Statistical Analysis
- Automated Testing

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/Nifty100-Financial-Intelligence-Platform.git
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run

Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

---

## 📌 Current Status

- ✅ Project initialized
- ✅ Git repository configured
- ✅ Folder structure created
- ⏳ Sprint 1 in progress

---

Sprint 1
✔ Environment Setup
✔ Excel Loader
✔ Normalizer
✔ Validator
✔ SQLite Schema
✔ ETL Pipeline
✔ Audit Reports
✔ Data Review
✔ SQL Queries


## Known Issue 
Some source Excel workbooks contain inconsistent company identifiers.
These are retained for audit purposes and documented through validation reports instead of being silently modified.


## 👨‍💻 Author

**Amit Singh**

B.Tech (Computer Science – Data Science)  
Python | Data Analytics | SQL | Streamlit | FastAPI | Machine Learning

---

## 📄 License

This project is developed for educational and portfolio purposes.
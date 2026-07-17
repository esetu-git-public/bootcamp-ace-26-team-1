# 🏥 Hospital Readmission Prediction System

An AI-powered Hospital Readmission Prediction System that predicts whether a patient is at risk of being readmitted within 30 days after discharge. The system uses a Random Forest Machine Learning model to analyze patient health records, predict readmission risk, securely store patient data in Supabase, and provide an interactive web dashboard for patient management, prediction history, and reporting.

---

## 🚀 Features

- Secure JWT-based user authentication
- Patient registration and management
- Predicts 30-day hospital readmission risk
- Random Forest Machine Learning model for prediction
- Risk categorization (High Risk / Low Risk)
- Patient prediction history
- Dashboard with patient analytics
- Report generation
- Audit logging for user activities
- REST API with Swagger documentation
- Responsive web interface
- Secure password hashing and Role-Based Access Control (RBAC)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python 3.13, FastAPI |
| AI/ML | Scikit-learn, Random Forest, Pandas, NumPy |
| Database | Supabase (PostgreSQL) |
| Authentication | JWT, OAuth2 |
| Reporting | HTML Reports |
| Version Control | Git, GitHub |

---

## 🏗️ Workflow

User Login → Patient Registration → Patient Data Validation → Feature Preprocessing → Random Forest Prediction → Risk Classification → Store Prediction (Supabase) → Dashboard & Reports

---

## 🎯 Problem & Solution

Hospital readmissions increase healthcare costs and often indicate gaps in post-discharge care. Identifying patients who are likely to be readmitted enables healthcare providers to intervene early and improve patient outcomes.

This system automates readmission prediction using a Random Forest Machine Learning model, helping hospitals identify high-risk patients, improve decision-making, reduce avoidable readmissions, and maintain a complete history of predictions.

---

## ⚙️ Key Requirements

- Prediction response within a few seconds
- Secure JWT authentication
- Responsive dashboard for desktop and mobile
- Secure password hashing
- Patient prediction history
- Audit logging
- Scalable architecture using FastAPI and Supabase

---

## 🚧 Assumptions & Out of Scope

### Assumptions

- Patient data entered is accurate.
- Supabase database is configured.
- Random Forest model is trained before deployment.
- Users have valid login credentials.

### Out of Scope

- Electronic Health Record (EHR) integration
- Live hospital monitoring systems
- Doctor recommendation system
- Medical diagnosis
- Treatment recommendations

---

## 🔮 Future Enhancements

- Add XGBoost, CatBoost, and Neural Network models
- Explainable AI (SHAP/LIME)
- PDF report generation
- Email notifications for high-risk patients
- Cloud deployment
- Multi-hospital support
- Real-time patient monitoring
- Doctor recommendation system

---

# 📁 Project Structure

```text
bootcamp-ace-26-team-1/
│   .env  #place it in .gitignore
│   .gitignore
│   DBstructure.txt
│   local_fallback.db
│   package-lock.json
│   package.json
│   README.md
│   requirements.txt
│   run.sh
│   security.py
│   start.bat
│   test_db_connection.py
│   test_fallback.db
│   train_model.py
│
├── .pytest_cache/
│
├── app/
│   │   config.py
│   │   dependencies.py
│   │   main.py
│   │
│   ├── api/
│   │   ├── audit.py
│   │   ├── auth.py
│   │   ├── patients.py
│   │   ├── prediction.py
│   │   └── reports.py
│   │
│   ├── ml/
│   │   ├── feature_cols.pkl
│   │   ├── feature_engineering.py
│   │   ├── model.pkl
│   │   ├── predictor.py
│   │   ├── preprocess.py
│   │   └── scaler.pkl
│   │
│   ├── services/
│   │   ├── audit_service.py
│   │   ├── auth_service.py
│   │   ├── patient_service.py
│   │   ├── prediction_service.py
│   │   └── report_service.py
│   │
│   └── utils/
│       ├── helpers.py
│       └── logger.py
│
├── data/
│   └── hospital_readmissions_30k.csv
│
├── Docs/
│   ├── Hospital Readmission SDLC.docx
│   ├── MVP Sprint Planning_ProductOwner_Team-1.docx
│   ├── MVP SPRINT PLAN_SCRUM MASTER(TEAM1).docx
│   ├── MVP_Sprint_Planning_Developer.docx
│   ├── MVP_Sprint_Plan_BusinessOwner.doc
│   ├── Product Requirements.docx
│   ├── TDD_Login_Form_Validation_ClientSide.docx
│   └── TEAM LEAD MVP(TEAM-1).docx
│
├── logs/
│   ├── app.log
│   └── audit.log
│
├── reports/
│
├── static/
│   ├── css/
│   │   ├── dashboard.css
│   │   ├── login.css
│   │   ├── patients.css
│   │   └── style.css
│   │
│   ├── images/
│   │   └── logo.png
│   │
│   └── js/
│       ├── audit.js
│       ├── auth-guard.js
│       ├── dashboard.js
│       ├── login.js
│       ├── patients.js
│       ├── prediction.js
│       └── reports.js
│
├── supabase/
│   ├── auth.py
│   ├── client.py
│   ├── database.py
│   ├── policies.md
│   ├── storage.py
│   └── __init__.py
│
├── templates/
│   ├── audit.html
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── patients.html
│   ├── prediction.html
│   └── reports.html
│
├── tests/
│   ├── test_auth.py
│   ├── test_auth_client.py
│   ├── test_patients.py
│   ├── test_prediction.py
│   ├── test_reports.py
│   └── test_security.py
│
└── uploads/
````

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone <repository-url>
cd bootcamp-ace-26-team-1
```

---

## 2. Configure Environment Variables

Create a `.env` file in the project root and add the following variables:

```env
# Supabase Configuration
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=

# Application Settings
ENVIRONMENT=development

# Security
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### How to Get the Required Values

| Variable | How to Obtain |
|----------|---------------|
| **SUPABASE_URL** | Open your Supabase project → **Settings → API** → Copy the **Project URL**. |
| **SUPABASE_KEY** | Go to **Settings → API** → Copy the **anon/public key**. |
| **SUPABASE_SERVICE_ROLE_KEY** | Go to **Settings → API** → Copy the **service_role key**. **Keep this secret and never expose it in frontend code.** |
| **SUPABASE_JWT_SECRET** | Go to **Settings → API** (or **Authentication → JWT**, depending on your Supabase version) → Copy the **JWT Secret**. |
| **SECRET_KEY** | Generate a secure random key (32+ characters). You can generate one using Python or OpenSSL (commands below). |
| **ALGORITHM** | Keep the default value: `HS256`. |
| **ACCESS_TOKEN_EXPIRE_MINUTES** | JWT access token expiry time in minutes. Default: `120`. |
| **ENVIRONMENT** | Use `development` for local development and `production` for deployment. |

### Generate a Secure SECRET_KEY

Using Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Example output:

```text
d4d3d0c5a9f56d4fdab32c8d6d8e4b83d8cf0c0d96e6c2a4fbe2d62d3b4d5f91
```

Or using OpenSSL:

```bash
openssl rand -hex 32
```

Copy the generated value into:

```env
SECRET_KEY=your_generated_secret_key
```

> **Security Note:** Never commit your `.env` file or share your `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, or `SECRET_KEY`. Ensure `.env` is listed in your `.gitignore`.

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Train the Machine Learning Model

```bash
python train_model.py
```

This script trains the **Random Forest** model and generates:

* `model.pkl`
* `scaler.pkl`
* `feature_cols.pkl`

---

## 5. Run the Application

### Linux / macOS

```bash
./run.sh
```

### Windows

```bash
start.bat
```

Or manually:

```bash
uvicorn app.main:app --reload
```

---

## 6. Open the Application

Dashboard:

```
http://localhost:8000
```

Swagger API Documentation:

```
http://localhost:8000/docs
```

ReDoc API Documentation:

```
http://localhost:8000/redoc
```

---
## 🔐 Environment Variables

Create a `.env` file in the project root and configure the following variables:

| Variable | Description | Required |
|---|---|---|
| `SUPABASE_URL` | Supabase Project URL | Yes |
| `SUPABASE_KEY` | Supabase Anon (Public) Key | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key (Backend only) | Yes |
| `SUPABASE_JWT_SECRET` | JWT Secret used by Supabase Authentication | Yes |
| `ENVIRONMENT` | Application environment (`development` or `production`) | No |
| `SECRET_KEY` | Secret key used to sign JWT access tokens | Yes |
| `ALGORITHM` | JWT signing algorithm (Default: `HS256`) | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiration time in minutes | No |

---

# 🗄️ Database Schema

The database contains the following primary tables:

* **users** — Stores user authentication and profile information.
* **patients** — Stores patient demographic and clinical information.
* **predictions** — Stores readmission prediction results and risk levels.
* **audit_logs** — Maintains user activity logs for auditing.
* **reports** — Stores generated report information.

---

# 🤖 Machine Learning

The system uses a **Random Forest Classifier** trained on the hospital readmission dataset.

Input features include:

* Age
* Gender
* Blood Pressure
* Cholesterol
* BMI
* Diabetes
* Hypertension
* Medication Count
* Length of Stay
* Discharge Destination

The trained model predicts whether a patient is likely to be readmitted within 30 days after discharge.

---

# 🔒 Security

* JWT Authentication
* OAuth2 Password Flow
* Password Hashing
* Protected API Routes
* Role-Based Access Control (RBAC)
* Environment Variable Protection

---

# 📄 License

This project is developed for educational purposes as part of the Bootcamp AI Project.

---

# 👨‍💻 Team

**Bootcamp ACE 2026 – Team 1**

Hospital Readmission Prediction System

```


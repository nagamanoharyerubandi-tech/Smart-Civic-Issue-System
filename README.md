# SMART CIVIC ISSUE REPORTING & RESOLUTION MANAGEMENT SYSTEM

> **"Report Problems. Track Progress. Build Better Communities."**

A modern, responsive, full-stack civic governance web application developed with **Python**, **Django Framework**, and **MySQL**, designed to streamline public infrastructure defect reporting and municipal resolution tracking.

---

## 1. Project Overview

Municipal infrastructure challenges directly affect the quality of life, commuter safety, and public health. Citizens often struggle with cumbersome paperwork and lack of transparency when reporting problems such as:

- **Road damage and dangerous potholes**
- **Overflowing garbage and municipal dumping**
- **Treated water pipeline leaks and bursts**
- **Drainage and sewage line blockages**
- **Streetlight failures and blackout corridors**
- **Public sanitation and community restroom defects**
- **Drinking water shortages and pressure failures**

The **Smart Civic Issue Reporting & Resolution Management System** replaces outdated paper grievances with an automated, photo-verified, geotagged digital platform. It establishes clear accountability with time-bound SLAs, duplicate complaint detection, live tracking timelines, and citizen feedback ratings.

---

## 2. Technology Stack

- **Backend:** Python 3.10+ / Python 3.15, Django Framework 6.0
- **Database:** MySQL 8.0 with `mysqlclient` and `PyMySQL`
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Analytics & Visualizations:** Chart.js 4.4
- **Image Processing & Validation:** Pillow (PIL)
- **Authentication & Security:** Django Auth, Password Hashing (PBKDF2-SHA256), CSRF Tokens, Role-Based Access Controls

---

## 3. User Roles & Capabilities

### A. Citizen
- **Registration & Authentication:** Sign up with contact details, address, and city.
- **Citizen Dashboard:** Live KPI counters (Total, Under Review, In Progress, Resolved) and active issue cards with progress bars.
- **Report Civic Issues:** Select from 7 pre-configured categories, upload photos with live preview, input city/ward/address/landmark, and auto-capture GPS coordinates.
- **My Complaints Registry:** Filterable list with status pills, search query, and pagination.
- **Complaint Detail Inspector:** High-resolution photo zoom, assigned department details, status change history.
- **Visual Progress Tracking:** Real-time horizontal stepper milestone view.
- **Complaint Cancellation:** Cancel submitted complaints if still in the initial `Submitted` status.
- **Feedback & Rating System:** Submit a 1-to-5 star rating and review after resolution.
- **In-App & Email Notifications:** Real-time alerts on triage, assignment, and status updates.
- **Personal Profile Management:** Update personal contact info and change passwords.

### B. Administrator
- **Secure Admin Portal:** Dedicated administrative command center.
- **Admin Dashboard:** High-level metrics, urgent high-priority alerts, and 4 interactive Chart.js graphs:
  1. *Status Distribution Donut Chart*
  2. *Category Volume Bar Chart*
  3. *Monthly Intake vs Resolution Trend Line Chart*
  4. *Department Workload & Resolution Bar Chart*
- **Manage All Complaints:** Search by reference ID, title, citizen, or ward; filter by status, priority, category, or department.
- **Audit & Status Update:** Update status (`Submitted` &rarr; `Under Review` &rarr; `Assigned` &rarr; `In Progress` &rarr; `Resolved` &rarr; `Rejected`) with mandatory remarks logged in history.
- **Department Dispatch:** Assign issues to engineering departments with instructions and target SLA completion dates.
- **Priority Management:** Elevate or de-escalate issue priority (`Low`, `Medium`, `High`).
- **Duplicate Detection Console:** Review automated duplicate flags, verify duplicates with one click, or dismiss false alarms.
- **Master Records Management:** Full CRUD for Issue Categories and Municipal Departments.
- **Citizen Directory:** Inspect all registered citizens, contact information, and grievance counts.
- **Complaint Analytics:** Review resolution rates, average turnaround durations, and department performance.
- **Feedback Review Center:** Monitor citizen reviews, star distribution scorecards, and testimonials.

---

## 4. Complaint Lifecycle & Status Flow

```
[ Citizen Files Issue ]
          │
          ▼
    1. SUBMITTED  ──────────► [ Citizen Can Cancel If In Initial State ]
          │
          ▼
   2. UNDER REVIEW (Central Control Room Triage & Duplicate Check)
          │
          ▼
     3. ASSIGNED   (Dispatched to Department e.g. PWD, Water Board)
          │
          ▼
   4. IN PROGRESS  (Field Maintenance Team On-Site with Machinery)
          │
    ┌─────┴────────────────┐
    ▼                      ▼
5. RESOLVED            6. REJECTED
 (With Official Notes)  (With Rejection Reason / Duplicate Consolidation)
    │
    ▼
[ Citizen Feedback & 5-Star Rating ]
```

Every transition is recorded in `ComplaintStatusHistory` with the acting officer, remarks, and timestamp.

---

## 5. Normalized Database Design

The relational schema is configured in MySQL (`civic_issue_db`):

| Model Name | Description | Key Relationships |
|---|---|---|
| **User** | Django built-in auth user | Core identity record |
| **Profile** | User role, phone, address, city, avatar | `OneToOneField(User)` |
| **Category** | Problem classifications (Roads, Waste, Water, etc.) | Referenced by `Complaint` |
| **Department** | Municipal dispatch wings (PWD, SWM, Water Board) | Referenced by `Complaint`, `ComplaintAssignment` |
| **Complaint** | Central grievance record (Reference ID, location, photo, priority, status) | `ForeignKey(User)`, `ForeignKey(Category)`, `ForeignKey(Department)` |
| **ComplaintAssignment** | Department work order, target date, dispatch notes | `ForeignKey(Complaint)`, `ForeignKey(Department)` |
| **ComplaintStatusHistory**| Complete unalterable audit trail of status changes | `ForeignKey(Complaint)`, `ForeignKey(User)` |
| **Notification** | In-app notification center | `ForeignKey(User)`, `ForeignKey(Complaint)` |
| **Feedback** | Post-resolution 1-5 star rating and review | `OneToOneField(Complaint)`, `ForeignKey(User)` |

---

## 6. Project Folder Structure

```
Smart_Civic_Issue_System/
│
├── manage.py                          # Django management CLI
├── requirements.txt                   # Production dependencies
├── pyrun.bat                          # Executable helper
├── test_all_endpoints.py              # Automated test runner for 28 endpoints
├── README.md                          # Comprehensive documentation
│
├── civic_management/                  # Project configuration
│   ├── __init__.py
│   ├── settings.py                   # MySQL, Apps, Auth, Static/Media config
│   ├── urls.py                       # Main routing registry
│   └── wsgi.py
│
├── accounts/                          # Authentication & User Profiles
│   ├── models.py                     # Profile model & signals
│   ├── views.py                      # Login, register, profile, password change
│   ├── forms.py                      # Citizen registration & profile forms
│   ├── decorators.py                 # @citizen_required, @admin_required
│   └── urls.py
│
├── complaints/                        # Core Complaint System
│   ├── models.py                     # Category, Department, Complaint, Assignment, History
│   ├── views.py                      # Citizen & Admin complaint workflows, CRUD
│   ├── forms.py                      # Complaint submission, triage, category, dept forms
│   ├── utils.py                      # Intelligent duplicate detection engine
│   ├── urls.py
│   ├── tests.py                      # 7 automated unit tests
│   └── management/commands/
│       └── seed_civic_data.py        # Realistic demo data seeder
│
├── dashboard/                         # Public, Citizen & Admin Dashboards
│   ├── views.py                      # Landing, about, how-it-works, contact, analytics, Chart.js API
│   └── urls.py
│
├── notifications/                     # In-App & Email Notification System
│   ├── models.py                     # Notification model
│   ├── utils.py                      # send_civic_notification helper
│   ├── context_processors.py         # Global unread count in navbar
│   ├── views.py                      # Notification list & mark as read
│   └── urls.py
│
├── feedback/                          # Citizen Rating & Review System
│   ├── models.py                     # Feedback model (1-5 stars)
│   ├── forms.py                      # 5-star rating form
│   ├── views.py                      # Feedback submission & admin review
│   └── urls.py
│
├── templates/                         # Reusable Django Templates
│   ├── base.html                     # Global base layout (Navbar, Footer, Messages)
│   ├── public/                       # Public pages (Home, About, Track, Login, Register)
│   ├── citizen/                      # Citizen portal (Dashboard, Report, My Complaints, Detail)
│   └── admin_portal/                 # Admin portal (Dashboard, Complaints, Categories, Depts, Analytics)
│
├── static/                            # Static Assets
│   ├── css/styles.css                # Professional Light & Dark theme stylesheet
│   └── js/
│       ├── main.js                   # Theme toggle, GPS capture, image preview
│       └── charts.js                 # Chart.js initialization & responsive updates
│
└── media/                             # Uploaded Media Storage
    ├── complaints/                   # Uploaded complaint photographs
    └── profiles/                     # User profile avatars
```

---

## 7. Installation & Execution Guide

### Prerequisites
1. Python 3.10 or higher installed.
2. MySQL Server 8.0 running locally on port 3306.

### Step 1: Clone or Navigate to Project Directory
```powershell
cd c:\Users\krish\OneDrive\Desktop\Smart_Civic_Issue_System
```

### Step 2: Configure MySQL Database
Open your MySQL client or workbench and create the database:
```sql
CREATE DATABASE IF NOT EXISTS civic_issue_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Update your database credentials in `civic_management/settings.py` (or set environment variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'civic_issue_db',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Seed Demonstration Data
Populate realistic categories, departments, demo users, complaints, and citizen feedbacks:
```powershell
python manage.py seed_civic_data
```

### Step 6: Start the Development Server
```powershell
python manage.py runserver
```
Open your browser and navigate to: `http://127.0.0.1:8000/`

---

## 8. Demonstration Login Credentials

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Super Administrator** | `admin` | `adminpassword123` | Full access to Municipal Admin Portal, analytics, categories, departments, and complaint management |
| **Citizen (Rahul Sharma)** | `citizen_rahul` | `citizen123` | Standard citizen dashboard, filed complaints, history, ratings |
| **Citizen (Priya Patel)** | `citizen_priya` | `citizen123` | Standard citizen dashboard, active in-progress issues |
| **Citizen (Amit Verma)** | `citizen_amit` | `citizen123` | Standard citizen dashboard, assigned water leak report |
| **Citizen (Sneha Iyer)** | `citizen_sneha` | `citizen123` | Standard citizen dashboard, duplicate road report demo |

*Tip: The Sign In page features quick 1-click credential fill buttons for fast demonstration!*

---

## 9. Automated Testing & Verification

Run the Django unit test suite:
```powershell
python manage.py test complaints
```
*(Result: 7 tests passing covering complaint generation, duplicate detection, department assignments, audit trail, feedback calculations, and security isolation).*

Run the full end-to-end endpoint verification script:
```powershell
python test_all_endpoints.py
```
*(Result: All 28 endpoints tested with HTTP 200/302 responses and security boundaries verified).*

---

## 10. Key Features for Technical Interviews

When demonstrating this project in fresher / junior IT interviews, highlight:
1. **Model Normalization:** Clean relational modeling with ForeignKeys, OneToOneField, timestamps, custom choices, and properties.
2. **Security & Role-Based Access Control:** Custom decorators (`@citizen_required`, `@admin_required`) ensuring citizens cannot view other citizens' complaints and cannot access the admin portal.
3. **Audit History Trail:** Automated capture of status transitions in `ComplaintStatusHistory`.
4. **Duplicate Detection:** Heuristic matching of incoming complaints against active neighborhood issues.
5. **Modern Responsive UI:** Bootstrap 5.3, custom CSS tokens, instant Light & Dark theme toggle using `localStorage`, and interactive Chart.js visualizations.
6. **Robust Error Handling:** File upload validation with Pillow, graceful fail-silent email dispatch, and clean Django message alerts.

# Tifinify: AI-Powered Tiffin & Mess Service Discovery and Review Trust Analysis System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask_3.x-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/Academic-MCA_Minor_Project-orange.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-22%2F22%20Passing-brightgreen.svg)](#)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/pranab1411/tifinify)

> **"Find food nearby. Understand the reviews. Choose with confidence."**

---

## 1. Project Overview

**Tifinify** is a location-based web application and review intelligence platform specifically engineered to help students, interns, and young professionals discover dependable daily tiffin and mess services.

While traditional platforms rely solely on aggregate star ratings (which are vulnerable to promotional spam, copy-paste reviews, and bias), Tifinify’s central innovation is its **Review Intelligence & Trust Analysis Engine**. Using text normalization, TF-IDF vectorization, pairwise Cosine Similarity, behavioral heuristics, aspect-based sentiment extraction, and grounded Gemini AI synthesis, Tifinify calculates a transparent, explainable **Review Trust Score (0–100)** for every provider.

---

## 2. Key MVP Features

1. **Modern Food-Tech Landing Page**:
   - Hero section with area-based discovery search.
   - Quick GPS location detection ("Use Current Location").
   - 4-step "How It Works" overview.
   - Explainable AI trust badging preview and featured nearby listings.

2. **Location-Based Discovery Engine**:
   - Customizable search radius: **1 km, 3 km, 5 km, 10 km**.
   - Bounding-box spatial pre-filtering and Haversine distance calculations.
   - Multi-parameter filtering: Service category (Tiffin / Mess), Dietary preference (Pure Veg / Jain / Non-Veg), Minimum rating, Review Trust Score threshold, and Maximum budget.
   - Interactive map with custom provider pins and popups.

3. **Provider Details & Transparent Trust Audit**:
   - **Clear Separation of Ratings**: External source star rating (e.g. ⭐ 4.5/5) is cleanly distinguished from Tifinify's AI Review Trust Score (e.g. 🛡 94/100).
   - **Explainable Behavioral Checklist**: Transparent positive signals (e.g. *"Diverse review wording"*, *"Normal rating consistency"*) and warning signals (e.g. *"Near-duplicate phrasing detected"*, *"Temporal burst"*).
   - **Food & Service Aspects**: Satisfaction breakdown across **Taste, Hygiene, Food Quality, Quantity, Delivery, and Value for Money**.
   - **Interactive Sentiment Chart**: Chart.js doughnut visualization of positive, neutral, and negative customer sentiment.
   - **Grounded AI Review Summary**: Objective 2-3 sentence overview synthesized strictly from customer experiences.

4. **Side-by-Side Provider Comparison Tool**:
   - Objective comparison of two providers across star rating, review count, trust score, monthly subscription price, distance, and aspect ratings.
   - Adheres to responsible consumer empowerment without declaring an arbitrary "winner."

5. **User Reviews & Authentication**:
   - User registration and login with secure **Werkzeug** password hashing.
   - Review submission form that instantly runs the review through the trust analysis engine.
   - User bookmarks and "My Favorites" list.

6. **Admin Dashboard**:
   - System-wide telemetry: total providers, reviews analyzed, suspicious reviews detected, and registered users.

---

## 3. Technology Stack

- **Backend**: Python 3.11+, Flask 3.x, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: SQLite (SQLAlchemy 2.0 ORM; fully portable to PostgreSQL/MySQL)
- **AI & NLP Engine**:
  - `scikit-learn` (Word n-gram TF-IDF vectorizer & pairwise Cosine Similarity)
  - `numpy` (Statistical matrices & score aggregation)
  - `google-genai` (Gemini 2.5 generative synthesis with deterministic rule-based fallback)
- **Frontend**: HTML5, CSS3 (Custom Food-Tech Theme), Bootstrap 5.3, Bootstrap Icons, Leaflet.js (Map), Chart.js (Visualizations)
- **Testing**: Pytest 8.x (14 passing unit and integration tests)

---

## 4. Review Trust Score Methodology

The Review Trust Score is formulated as:

$$\text{Trust Score} = 100 - \min(100, (\text{DuplicatePenalty} \times 0.35 + \text{InconsistencyPenalty} \times 0.30 + \text{BurstPenalty} \times 0.20 + \text{PolarizationPenalty} \times 0.15))$$

### Trust Badges
- **🟢 Likely Authentic (80 – 100)**: Natural linguistic diversity, consistent sentiment, and organic timing.
- **🟡 Potentially Suspicious (50 – 79)**: Minor repeated phrases or rating-content contradictions.
- **🔴 Highly Suspicious (0 – 49)**: Severe near-duplicate clusters, advertising jargon, or artificial review bursts.

> **Responsible AI Principle:**  
> The system evaluates detectable linguistic and statistical patterns. It does **not** claim to prove real-world reviewer identity or fraud.

---

## 5. Quick Start (Running Locally)

### Prerequisites
- Python 3.11 or higher installed on your machine.

### 1. Set Up Virtual Environment & Install Dependencies
```bash
# Navigate to the project directory
cd "D:\shreya minor project\tifinify"

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install minimal dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
A pre-configured `.env.example` is provided:
```bash
copy .env.example .env
```
*(Note: Tifinify works 100% out-of-the-box in Demo Mode without requiring any external paid API keys.)*

### 3. Seed Realistic Demo Data
Populate the database with realistic student tiffin providers and controlled review patterns:
```bash
python scripts/seed_db.py
```

### 4. Run the Application
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 6. Faculty Demonstration Walkthrough (5-Minute Sequence)

1. **Landing Page (`http://127.0.0.1:5000/`)**:
   - Showcase the food-tech UI, project tagline, and search card.
   - Click **"Find Tiffin & Mess Services"**.
2. **Provider Discovery (`/providers/discovery`)**:
   - Demonstrate the interactive map with colored provider pins.
   - Filter by **Radius (3 km)**, **Food Type (Pure Veg)**, or **Trust Score (80+)**.
3. **Provider Details (`/providers/1`) - Authentic Example**:
   - Open **"Annapurna Homely Tiffin Service"**.
   - Note the distinction between **Source Rating (4.6/5)** and **AI Review Trust Score (94/100, Likely Authentic)**.
   - Review the aspect bars (Taste: 92%, Hygiene: 88%) and sentiment chart.
4. **Provider Details (`/providers/2`) - Suspicious Anomaly Example**:
   - Open **"Royal Star Mess & Catering"**.
   - Note that despite having a 3.4-star rating, the system detected near-duplicate promotional reviews:
     `"Best tiffin service in Pune call now for guaranteed discounts..."`
   - Observe the yellow warning badge, similarity indicators, and burst warnings.
5. **Side-by-Side Comparison (`/providers/compare?p1=1&p2=2`)**:
   - Compare Annapurna Homely Tiffin vs. Royal Star Mess.
6. **Submit a Review (`/reviews/1/new`)**:
   - Submit a review and observe instant re-evaluation by the AI engine.
7. **Admin Dashboard (`/admin/dashboard`)**:
   - Log in as `admin@tifinify.com` / `Admin@123` to view system telemetry.

---

## 7. Running Automated Tests

Run the complete 14-test verification suite:
```bash
pytest -v
```
All unit tests for text cleaning, TF-IDF cosine similarity, heuristic inconsistency detection, aspect extraction, route endpoints, and comparison matrices will execute.

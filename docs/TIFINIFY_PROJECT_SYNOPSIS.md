# “TIFINIFY”
### AI-Powered Tiffin & Mess Service Discovery and Review Trust Analysis System
**A PROJECT SYNOPSIS REPORT**

*Submitted in partial fulfilment of the requirement for the award of the degree of*  
**MASTER OF COMPUTER APPLICATION**  
**SESSION: 2025–27**

---

**Submitted by:**  
**Pranab Chourasiya** (0201CA251047)  
**Chandrashekhar Suryawanshi** (0201CA251018)  
III SEM. MCA  

**Submitted to:**  
**Dr. SAMAR UPADHYAY**  
**Dr. MAMTA LAMBERT**  
*Head of Department (HOD)*  

**Under the Guidance of:**  
Professor Roshni Vinodia  
Professor Anjali Sahu  
Professor Megha Malik  
Professor Swapnila Kashyap  
Professor Shikha Singh Narela  

**DEPARTMENT OF COMPUTER APPLICATION**  
**JABALPUR ENGINEERING COLLEGE, JABALPUR (M.P.)**  
*(Established in 1947 as Government Engineering College, Jabalpur)*  
*(Declared Autonomous by Government of Madhya Pradesh and RGPV, Bhopal)*  

---

## INDEX

| S. No. | Topic | Page No. |
| :--- | :--- | :--- |
| **1.** | Preface | 3 |
| **2.** | Introduction | 4 |
| | 2.1 Background | 4 |
| | 2.2 Problem Statement | 4 |
| | 2.3 Significance of the Project | 4 |
| **3.** | Scope and Objectives of the System | 5 |
| **4.** | Feasibility Study | 6 |
| | 4.1 Technical Feasibility | 6 |
| | 4.2 Economic Feasibility | 6 |
| | 4.3 Operational Feasibility | 6 |
| | 4.4 Schedule Feasibility | 6 |
| | 4.5 Ethical and Privacy Feasibility | 6 |
| **5.** | System Requirements | 7 |
| | 5.1 Hardware Requirements | 7 |
| | 5.2 Software Requirements | 7 |
| **6.** | Technologies Used | 8 |
| | 6.1 Python | 8 |
| | 6.2 Flask Web Framework | 8 |
| | 6.3 Google Gemini AI & Grounded Search | 8 |
| | 6.4 NLP & Scikit-Learn Heuristic Engine | 8 |
| | 6.5 SQLite & SQLAlchemy ORM | 8 |
| | 6.6 OpenMaps (Leaflet.js & OpenStreetMap Overpass) | 8 |
| | 6.7 Supporting Technologies | 8 |
| **7.** | Goals | 9 |
| **8.** | Proposed System | 9 |
| | 8.1 Multi-Criteria Review Trust Evaluation Model | 9 |
| | 8.2 Real Business Search Intelligence Pipeline | 9 |
| | 8.3 AI and Grounded Fallback Flow | 9 |
| **9.** | Modules | 10 |
| **10.** | Implementation of DFD (Data Flow Diagram) | 12 |
| | 10.1 System Overview DFD | 12 |
| | 10.2 Level 0 DFD (Context Level) | 13 |
| | 10.3 Level 1 DFD (Detailed Data Flow) | 14 |
| | 10.4 DFD Interpretation | 15 |
| **11.** | ER Diagram – Database | 15 |
| | 11.1 Entity Description | 17 |
| **12.** | Functional Requirements | 17 |
| **13.** | Non-Functional Requirements | 17 |
| **14.** | Methodology | 18 |
| **15.** | Database Details and Data Integrity | 18 |
| | 15.1 Data Integrity and Security | 18 |
| **16.** | Expected Outcomes | 19 |
| **17.** | Advantages | 19 |
| **18.** | Limitations | 20 |
| **19.** | Future Scope | 20 |
| **20.** | Conclusion | 21 |
| **21.** | References | 22 |

---

## 1. PREFACE

The rapid migration of students, interns, and young working professionals toward educational, engineering, and industrial hubs has transformed how daily nutritional needs are met. Unlike occasional restaurant dining or on-demand fast-food delivery, subscribing to a daily mess or tiffin service represents an essential, recurring health and financial commitment. A customer does not merely evaluate a single dish; they rely on the provider for consistent hygiene, food freshness, prompt delivery, and affordability twice a day for months.

Consequently, consumers rely heavily on digital reviews to choose a service. However, contemporary consumer directories and search platforms suffer from a critical vulnerability: aggregate star ratings (e.g., 4.7/5) can be easily manipulated through incentivized 5-star campaigns, duplicate promotional spam, coordinated review bursts, and promotional bot submissions. Conversely, genuine customer complaints regarding food hygiene, watery curries, late delivery, or unhygienic packaging are frequently drowned out by inflated ratings.

**Tifinify** has been conceived as an integrated academic software engineering project to solve this exact dilemma. Rather than functioning as a standard directory, Tifinify unites spatial web discovery, natural language processing, machine learning heuristics, grounded generative AI, interactive geospatial mapping, database persistence, authentication, and responsive user-interface design into a unified decision-support platform.

The core engineering principle of Tifinify is **Explainable Review Intelligence & Trust Auditing**. The system decouples raw star ratings from an authentic **Review Trust Score (0–100)** computed via a 4-pillar Multi-Criteria Decision Analysis (MCDA) framework. By combining text normalization, TF-IDF n-gram vectorization, pairwise Cosine Similarity (for duplicate spam detection), sentiment-rating inconsistency checks, temporal burst heuristics, and Google Gemini AI contextual synthesis with real web grounding, Tifinify equips consumers with transparent, objective guidance.

Furthermore, the system demonstrates high architectural resilience. While Google Gemini provides rich contextual summaries and real-world search grounding, the system incorporates deterministic local NLP heuristics and zero-billing web search intelligence (DuckDuckGo and OpenStreetMap Overpass API) as a primary operational pipeline. This ensures uninterrupted real business discovery even in the absence of paid external API keys.

This synopsis report provides a comprehensive architectural specification of Tifinify, including its problem definition, objectives, feasibility, technological foundations, system modules, Data Flow Diagrams (DFDs), Entity-Relationship (ER) database design, requirements, methodology, expected outcomes, and future scope.

---

## 2. INTRODUCTION

Finding a trustworthy daily meal provider in an unfamiliar city is one of the most stressful challenges facing students and migrant workers. Unhygienic meal services frequently cause gastrointestinal illnesses, nutritional deficits, and academic disruption. While commercial delivery apps focus on high-margin restaurant orders, local tiffin centers and student messes operate in an unorganized sector with negligible platform accountability.

Tifinify transforms this fragmented process into an organized, transparent, and intelligent web application. Users are not restricted to blind star ratings; they receive an explainable, multi-dimensional audit of every provider. The platform highlights authentic strengths (such as *"Diverse reviewer vocabulary"*, *"Normal rating distribution"*, and *"High hygiene consistency"*) while proactively alerting users to red flags (*"Duplicate review text detected"*, *"Temporal rating burst"*, or *"Severe rating-sentiment conflict"*).

From an engineering perspective, Tifinify illustrates the integration of modern full-stack web technologies with state-of-the-art AI. The system manages spatial calculations, asynchronous geolocation fallbacks, SQLite ORM relational storage, RESTful JSON APIs, Leaflet.js map rendering with dark-mode filtering, and multi-parameter filtering without coupling itself exclusively to proprietary paid services.

### 2.1 Background
Traditional consumer directories (such as Justdial, Google Maps, or Sulekha) display aggregate star ratings calculated through a simple arithmetic average. This naive mathematical model fails to consider the authenticity or behavioral patterns behind reviews. A vendor with 50 manufactured 5-star reviews posted within 48 hours easily outranks a genuine, long-standing home cook who possesses 25 realistic, balanced reviews.

Tifinify addresses this deficiency through a hybrid AI pipeline. It combines statistical NLP (TF-IDF cosine similarity matrices) with linguistic heuristics (sentiment contradiction detection) and Google Gemini AI search grounding. This enables users to search any locality or college campus (e.g., *"JEC Ranjhi, Jabalpur"*, *"Viman Nagar, Pune"*, *"Koramangala, Bengaluru"*) and immediately discover genuine, operating meal providers.

### 2.2 Problem Statement
Consumers in student and working hubs lack an objective, reliable mechanism to evaluate daily tiffin and mess providers. Existing directory models fail to detect deceptive review inflation, lack multi-criteria aspect extraction (hygiene, delivery, taste, quantity, price), and often show outdated or synthetic business listings.

The problem addressed by **Tifinify** is to design and develop an intelligent, location-based web application that can:
1. Discover genuine, physical tiffin centers and messes around any coordinates or locality name without requiring paid Google Places billing.
2. Ingest, sanitize, and analyze customer reviews through automated NLP and machine learning heuristics.
3. Compute an explainable, mathematical Review Trust Score (0–100) and assign trust badges.
4. Extract structured sentiment across five vital meal aspects: Taste, Hygiene, Food Quality, Delivery, and Value for Money.
5. Provide side-by-side comparison, interactive map plotting, zero-flicker dark mode, and user account workflows.

### 2.3 Significance of the Project
The significance of Tifinify lies in bridging practical full-stack web engineering with responsible, explainable Artificial Intelligence. Rather than treating AI as an opaque "black box," Tifinify grounds AI summaries strictly on extracted customer statements and provides concrete mathematical evidence for every trust deduction. The project provides an invaluable blueprint for modern decision-support software in consumer technology.

---

## 3. SCOPE AND OBJECTIVES OF THE SYSTEM

The immediate scope of Tifinify is a location-aware web application for consumers (students, bachelors, working professionals) seeking daily or monthly tiffin and mess subscriptions. The system evaluates provider listings and reviews, extracting actionable insights to assist user decisions. Tifinify does not manage kitchen operations or financial food preparation; its scope is focused strictly on discovery, review auditing, trust evaluation, spatial mapping, and decision support.

The architectural scope encompasses:
- Geolocation resolution via browser GPS, Open-Meteo forward geocoding, and IP-based fallback.
- Zero-billing real establishment discovery via live web search and OpenStreetMap Overpass queries.
- Gemini AI contextual analysis with Google Search grounding.
- Multi-pillar review trust evaluation, aspect categorization, and duplicate text detection.
- Interactive OpenMaps (Leaflet.js) integration with custom map pins, popups, and dark tiles.
- Side-by-side multi-provider comparison tooling.
- User management, secure credential storage, bookmarked favorites, and administrator telemetry dashboards.

### Objectives
- **Multi-Radius Spatial Search**: Allow users to query tiffin providers within **1 km, 3 km, 5 km, and 10 km** radial zones using Haversine distance calculations.
- **Zero-Billing Place Intelligence**: Implement web search and Overpass API adapters to discover actual, operating establishments without requiring paid Google Maps API keys.
- **AI-Powered Review Intelligence**: Integrate Google Gemini AI to synthesize grounded, objective summaries of customer sentiment.
- **Deterministic NLP Trust Auditing**: Develop a 4-pillar MCDA engine that scores review authenticity using TF-IDF cosine similarity, sentiment-rating consistency, and temporal burst heuristics.
- **Aspect-Based Sentiment Extraction**: Categorize review sentences into key operational dimensions: *Taste, Hygiene, Quality, Quantity, Delivery, and Value for Money*.
- **Clear Rating Separation**: Visually distinguish external star ratings (e.g., ⭐ 4.5/5) from Tifinify's AI Review Trust Score (e.g., 🛡 92/100).
- **Interactive Geospatial Visualization**: Plot providers on responsive Leaflet maps with visual category markers (Veg, Non-Veg, Both, Jain).
- **Accessible & Adaptive UI**: Deliver a modern responsive interface supporting a persistent, zero-flicker Dark/Light theme mode.
- **Objective Provider Comparison**: Provide a side-by-side tabular comparison tool contrasting pricing, distance, aspect scores, and trust metrics.
- **Robust Security & Data Integrity**: Protect user authentication using salted Werkzeug password hashing and relational SQLite storage.

---

## 4. FEASIBILITY STUDY

The feasibility study examines whether Tifinify can be engineered, tested, deployed, and sustained within the academic timeline, resource envelope, and technical competencies of an MCA project.

### 4.1 Technical Feasibility
Tifinify is built on Python 3.11+ and Flask 3.x, representing an exceptionally mature, modular, and stable ecosystem. Client-side mapping is rendered using Leaflet.js and OpenStreetMap tiles, eliminating dependencies on complex SDKs. Machine learning and NLP routines utilize industry-standard libraries (`scikit-learn`, `numpy`). Database storage is powered by SQLite with SQLAlchemy 2.0 ORM, ensuring complete portability to PostgreSQL if deployed at enterprise scale. Cloud AI utilizes the official `google-genai` SDK. All components have been verified through automated test suites (22/22 tests passing), confirming high technical feasibility.

### 4.2 Economic Feasibility
The economic footprint of Tifinify is virtually zero ($0). The software stack consists entirely of open-source technologies: Python, Flask, Bootstrap 5, Leaflet.js, and SQLite. For location and place discovery, Tifinify uses free Open-Meteo geocoding and live Overpass queries, avoiding expensive commercial mapping charges. Gemini AI operates within Google AI Studio's free tier. Furthermore, the application is packaged with a `Procfile` and `render.yaml` for 100% free cloud deployment on Render.com.

### 4.3 Operational Feasibility
The application interface is clean, intuitive, and mobile-friendly. Users do not require technical expertise; they can discover nearby food by simply clicking *"Use Current Location"* or typing a locality. The explainable trust breakdown translates complex mathematical algorithms into understandable badges (*Likely Authentic*, *Potentially Suspicious*, *Highly Suspicious*). The system is fully operational on modern web browsers (Chrome, Edge, Firefox, Safari) across desktop and mobile devices.

### 4.4 Schedule Feasibility
The project was structured across sequential, manageable development phases:
1. Requirements & architectural design.
2. Database schema design and SQLAlchemy modeling.
3. Spatial search, Haversine formulas, and Leaflet map integration.
4. AI Review Trust pipeline, TF-IDF duplicate detection, and aspect extractors.
5. Real place search adapters (Google Search, DuckDuckGo, Overpass API).
6. Frontend design, Bootstrap 5 components, and persistent dark mode implementation.
7. Automated test suite authoring (pytest) and cloud deployment configuration.
This staged execution ensures comfortable completion within the MCA academic schedule.

### 4.5 Ethical and Privacy Feasibility
Tifinify strictly respects user privacy. Location detection is opt-in, executed via client-side HTML5 Geolocation API, with IP detection used solely as an anonymized fallback. Passwords are never stored in plaintext; they are hashed with cryptographic salt. Reviews analyzed from public listings do not expose private personal phone numbers or addresses. Furthermore, Tifinify's scoring engine is strictly objective and explainable, ensuring unbiased evaluations without arbitrary vendor penalties.

---

## 5. SYSTEM REQUIREMENTS

### 5.1 Hardware Requirements

| Component | Minimum Requirement | Recommended Requirement |
| :--- | :--- | :--- |
| **Processor** | Dual-Core 64-bit Processor (Intel Core i3 / AMD Ryzen 3) | Quad-Core 64-bit Processor or higher (Intel Core i5 / AMD Ryzen 5) |
| **RAM** | 4 GB RAM | 8 GB RAM or higher |
| **Hard Disk** | 500 MB free space for code, virtual environment, and database | 2 GB free SSD space |
| **Display** | 1280 × 720 resolution | 1920 × 1080 Full HD |
| **Network** | Active internet connection (for live web search, map tiles, and Gemini AI) | Broadband / High-speed Wi-Fi |

### 5.2 Software Requirements

| Software / Technology | Specification / Version | Purpose |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, Ubuntu Linux, or macOS | Development and Host Environment |
| **Programming Language** | Python 3.11 / 3.12 / 3.14 | Core Application Backend Logic |
| **Web Framework** | Flask 3.0+ | WSGI Web Routing, Controllers, Templates |
| **Database Engine** | SQLite 3 (via SQLAlchemy 2.0) | Relational Storage of Users, Providers, Reviews |
| **AI & NLP Libraries** | `google-genai` (0.1+), `scikit-learn` (1.4+), `numpy` (1.26+) | TF-IDF Cosine Similarity & Gemini AI Grounded Analysis |
| **Frontend Framework** | Bootstrap 5.3.3 & Bootstrap Icons | Responsive UI Components, Grid, and Theming |
| **Mapping Engine** | Leaflet.js 1.9.4 & OpenStreetMap | Geospatial Map Visualization and Pins |
| **Data Visualizations** | Chart.js 4.x | Aspect & Sentiment Doughnut Visualizations |
| **Production Server** | Gunicorn 21.2+ | Production WSGI Server for Free Cloud Hosting |
| **Testing Suite** | pytest 8.x / 9.x | Unit & Integration Test Automation |
| **Web Browser** | Google Chrome, Mozilla Firefox, Microsoft Edge | Client Application Access |

---

## 6. TECHNOLOGIES USED

The technological architecture of Tifinify is engineered for speed, modularity, and zero proprietary lock-in.

### 6.1 Python
Python acts as the primary programming language, executing routing, geospatial trigonometry, machine learning pipelines, and database transactions within a unified environment.

### 6.2 Flask Web Framework
Flask 3.x serves as the lightweight, high-performance WSGI framework. Using Flask's **Application Factory** pattern (`create_app`) and **Blueprints** (`main_bp`, `provider_bp`, `auth_bp`, `api_bp`, `admin_bp`), the application maintains pristine separation of concerns between presentation, business logic, and RESTful APIs.

### 6.3 Google Gemini AI & Grounded Search
Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`) acts as the high-level semantic reasoning engine. When supplied with customer reviews, Gemini generates objective, grounded summaries. Furthermore, Gemini with Google Search grounding discovers real local establishments in real-time.

### 6.4 NLP & Scikit-Learn Heuristic Engine
The review trust pipeline uses `scikit-learn` to transform review texts into word-level and character n-gram TF-IDF vectors. Pairwise Cosine Similarity matrices automatically detect copied or template-generated reviews. Custom rule-based heuristics detect review bursts and sentiment-rating contradictions.

### 6.5 SQLite & SQLAlchemy ORM
SQLite provides an integrated, zero-configuration relational database engine. SQLAlchemy 2.0 ORM manages relational integrity, declarative models, migrations, cascading deletes, and database queries.

### 6.6 OpenMaps (Leaflet.js & OpenStreetMap Overpass)
Geospatial visualization is handled client-side via Leaflet.js. Live business queries interface with OpenStreetMap's Overpass API (`overpass-api.de`) to extract authentic canteens, messes, and eateries without requiring commercial map billing.

### 6.7 Supporting Technologies
- **Bootstrap 5.3.3**: Modern UI framework with custom CSS variables for light/dark theme switching.
- **Chart.js**: Dynamic canvas-rendered sentiment distributions.
- **Werkzeug**: Secure password hashing via PBKDF2/scrypt.
- **Open-Meteo API**: Rapid forward geocoding converting text localities into latitude/longitude.
- **ipwhois.app / ipapi.co**: Seamless background IP geolocation for instant discovery.

---

## 7. GOALS

- **Eradicate Review Deception**: Build an algorithmic trust engine that uncovers fake, incentivized, or duplicate reviews for daily food services.
- **Democratize Food Discovery**: Provide an easy-to-use search engine for student messes and tiffin centers with spatial radius filtering.
- **Zero-Cost Operation**: Guarantee that the application can discover places, map coordinates, and run AI analysis without requiring paid API billing.
- **Transparent Decision Support**: Present users with clear ratings across six essential food aspects (Hygiene, Taste, Delivery, Quality, Price, Quantity).
- **High Architectural Resilience**: Seamlessly fall back to local NLP heuristics and web scraping if external cloud services experience downtime.
- **Universal Device Accessibility**: Offer a mobile-responsive interface equipped with a persistent, zero-flicker dark mode.

---

## 8. PROPOSED SYSTEM

Tifinify is designed as an end-to-end web application following an MVC (Model-View-Controller) and Service-Layer architecture. A user initiates discovery by inputting an area name (e.g., *"JEC Ranjhi"*) or clicking the GPS crosshair. The system resolves coordinates, filters local providers using Haversine distance calculations, and triggers real-time place discovery if a new area is searched.

Every provider profile displays two distinct metrics:
1. **Aggregated Star Rating** (e.g., 4.6 / 5.0).
2. **Tifinify AI Review Trust Score** (e.g., 88 / 100).

The user can explore sentiment doughnut charts, read an AI-synthesized grounded summary, inspect individual aspect ratings, view the kitchen on an interactive map, and add providers to a side-by-side comparison table.

```
[ User Input / Geolocation ]
            │
            ▼
[ Spatial Discovery Controller ]
            │
            ├──► [ Haversine Spatial Query in SQLite DB ]
            │
            └──► [ Live Discovery Engine (Web Search / Overpass / Gemini) ]
                        │
                        ▼
            [ Review Intelligence & Trust Engine ]
                        │
                        ├──► TF-IDF Vectorizer & Cosine Similarity
                        ├──► Aspect Sentiment Extraction (5 Pillars)
                        ├──► Contradiction & Temporal Burst Heuristics
                        └──► Grounded Gemini AI Summary
                        │
                        ▼
            [ Explainable Trust Score & Badging (0-100) ]
                        │
                        ▼
            [ Responsive UI / OpenMaps Visualization / Comparison ]
```

### 8.1 Multi-Criteria Review Trust Evaluation Model
Tifinify's scoring engine computes a composite Trust Score based on four weighted pillars:
- **Review Text Diversity & Uniqueness (35%)**: Penalizes identical or near-duplicate phrasing detected via TF-IDF cosine similarity (>0.85 similarity threshold).
- **Rating-Sentiment Consistency (25%)**: Penalizes reviews where a 5-star rating accompanies deeply negative sentiment words (or vice versa).
- **Temporal Distribution & Burst Analysis (20%)**: Flags suspicious clusters of reviews published in an unnaturally short timeframe.
- **Reviewer Volume & Profile Credibility (20%)**: Evaluates sample size and distribution balance.

### 8.2 Real Business Search Intelligence Pipeline
When a user searches for an area with no prior listings, Tifinify automatically executes its `WebSearchPlacesAdapter`:
1. Queries search engine indices (Google / DuckDuckGo) for active local tiffin listings using targeted regex patterns (`\b(tiffin|mess|rasoi|bhojanalaya|canteen)\b`).
2. Concurrently queries OpenStreetMap's Overpass API with a strict 3-second timeout for registered amenities.
3. Sanitizes extracted business titles, removing directory portal noise (*Justdial*, *Sulekha*, *Homefoodi*).
4. Persists the authentic businesses into SQLite, triggers review trust evaluation, and plots them on the map.

### 8.3 AI and Grounded Fallback Flow
- **Primary AI Flow**: Gemini AI generates contextual review summaries and discovers businesses via Google Search grounding.
- **Fallback Flow**: If the Gemini API quota is exhausted or an API key is omitted, the system seamlessly activates the deterministic local NLP heuristics and web search pipeline. Zero crashes occur, ensuring uninterrupted user experience.

---

## 9. MODULES

Tifinify is partitioned into decoupled, independently testable modules:

### 9.1 Authentication & User Preferences Module
Manages user registration, login, session persistence, role assignment (Consumer vs. Administrator), dietary preferences (Veg, Non-Veg, Both, Jain), and search radius defaults. Passwords are securely hashed with Werkzeug salt.

### 9.2 Spatial Discovery & Multi-Radius Search Module
Performs geographic calculations using the spherical Haversine formula:
$$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
Enables filtering by 1 km, 3 km, 5 km, and 10 km radiuses, dietary types, categories (tiffin vs. mess), minimum rating, and maximum monthly price.

### 9.3 Real-World Web & Overpass Search Intelligence Module
Integrates `WebSearchPlacesAdapter` to discover authentic local providers from public web directories and OpenStreetMap Overpass servers without requiring a paid Google Maps API billing account.

### 9.4 Gemini AI Contextual Review Intelligence Module
Leverages Google Gemini (`google-genai` SDK) to synthesize concise, objective 2-3 sentence summaries of customer experiences, highlighting recurring praises and complaints.

### 9.5 TF-IDF Similarity & Duplicate Detection Engine
Transforms review texts into n-gram TF-IDF feature matrices using `scikit-learn`. Computes pairwise Cosine Similarity:
$$\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
Pairs scoring above 0.85 are marked as duplicate/suspicious spam.

### 9.6 Behavioral Heuristics & Sentiment Inconsistency Module
Scans review text against categorized lexicons to identify contradictions between numerical star ratings (e.g., 5.0) and severe complaint keywords (*"insects"*, *"hair in food"*, *"stale"*, *"terrible diarrhea"*).

### 9.7 Aspect-Based Extraction & Scoring Module
Analyzes review sentences across five core food-service dimensions:
1. **Taste**: Flavors, spices, home-cooked feel.
2. **Hygiene**: Cleanliness, packaging quality, food safety.
3. **Food Quality**: Freshness of vegetables, softness of rotis.
4. **Delivery**: Timeliness, temperature, packaging leaks.
5. **Value for Money**: Price-to-portion ratio, monthly affordability.

### 9.8 Explainable Trust Badge & Rating Separation Module
Assigns normalized Trust Scores (0–100) and displays intuitive badges:
- 🛡 **Likely Authentic** (Trust Score ≥ 75)
- ⚠️ **Potentially Suspicious** (Trust Score 50–74)
- 🚨 **Highly Suspicious** (Trust Score < 50)

### 9.9 Side-by-Side Provider Comparison Module
Provides a dedicated comparison interface (`/providers/compare`) allowing users to place two or three providers side-by-side to compare distance, pricing, aspect satisfaction, and review trust.

### 9.10 Interactive OpenMaps / Leaflet Mapping Module
Renders responsive OpenStreetMap tiles using Leaflet.js. Automatically positions markers, draws circle boundaries for the chosen radius, renders information popups, and applies dark-mode CSS filters when dark theme is active.

### 9.11 Dark/Light Theme & UI State Engine
Delivers an accessible theme switcher with an inline pre-hydration script in `<head>` that reads `localStorage` and system `prefers-color-scheme`. Completely eliminates white flash on page reload.

### 9.12 Admin Governance & Telemetry Audit Module
Provides an administrative portal displaying system telemetry: total registered users, active providers, reviews analyzed, flagged duplicate reviews, and audit logs.

### 9.13 Automated Testing & Quality Assurance Module
Houses the automated `pytest` test suite containing 22 unit and integration tests covering review sanitization, similarity detection, aspect extraction, API routes, and real search adapters.

---

## 10. IMPLEMENTATION OF DFD (DATA FLOW DIAGRAM)

### 10.1 System Overview DFD (Level 0 - Context Level)

```
                       ┌─────────────────────────┐
                       │          User           │
                       └────────────┬────────────┘
                                    │
               1. Query / Location  │  4. Results, Trust Badges,
                  & Credentials     │     Map & Comparisons
                                    ▼
                       ┌─────────────────────────┐
                       │       0. TIFINIFY       │
                       │     AI Trust System     │
                       └────────────┬────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │ 2. Sync / Place Query   │ 3. Reviews & Context    │ 5. CRUD Data
          ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  OpenStreetMap / │      │  Google Gemini   │      │  SQLite Database │
│    Web Search    │      │    AI Engine     │      │   (Local ORM)    │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

### 10.2 Level 1 DFD (Decomposed System Processing)

```
[ User ]
   │
   ├──────────► ( 1.0 User Authentication ) ──────────► [ D1: Users & Preferences ]
   │                     │
   │                     ▼
   ├──────────► ( 2.0 Spatial Search & Geocoding )
   │                     │
   │                     ├──► [ D2: Providers ]
   │                     │
   │                     ▼
   ├──────────► ( 3.0 Real Place Discovery ) ─────────► [ Web Search & Overpass ]
   │                     │
   │                     ▼
   │            ( 4.0 Review Ingestion ) ─────────────► [ D3: Reviews ]
   │                     │
   │                     ▼
   │            ( 5.0 NLP & Trust Scoring Engine )
   │                     │
   │                     ├──► [ TF-IDF Cosine Similarity Matrix ]
   │                     ├──► [ Aspect & Heuristic Contradiction Analyzer ]
   │                     └──► [ Google Gemini Grounded Summarizer ]
   │                     │
   │                     ▼
   └──────────◄ ( 6.0 Results, Map & Comparison View ) ◄── [ D4: Trust Summaries ]
```

### 10.4 DFD Interpretation
- **Data Flow 1.0**: Credentials flow from the user into the authentication controller, verifying PBKDF2 hashes against the `users` datastore.
- **Data Flow 2.0 & 3.0**: Location parameters are converted into decimal coordinates; the system queries the local `providers` datastore within the radial threshold. If unpopulated, the discovery engine scrapes real establishments via Overpass/Web and stores them.
- **Data Flow 4.0 & 5.0**: Review texts flow into the TF-IDF vectorizer and heuristic pipeline, generating numerical trust scores, aspect distributions, and Gemini AI summaries.
- **Data Flow 6.0**: Computed scores, maps, and comparisons are rendered to the client interface.

---

## 11. ER DIAGRAM – DATABASE

```
 ┌──────────────────┐                 ┌───────────────────────┐
 │      USERS       │ 1             * │       FAVORITES       │
 │──────────────────│─────────────────│───────────────────────│
 │ id (PK)          │                 │ id (PK)               │
 │ email            │                 │ user_id (FK)          │
 │ password_hash    │                 │ provider_id (FK)      │
 │ role             │                 │ created_at            │
 └────────┬─────────┘                 └───────────────────────┘
          │ 1
          │
          │ 1
 ┌────────┴─────────┐                 ┌───────────────────────┐
 │ USER_PREFERENCES │                 │   PROVIDER_SOURCES    │
 │──────────────────│                 │───────────────────────│
 │ id (PK)          │                 │ id (PK)               │
 │ user_id (FK)     │                 │ provider_id (FK)      │
 │ budget_min       │                 │ source_type           │
 │ budget_max       │                 │ external_id           │
 │ max_distance_km  │                 │ last_synced_at        │
 └──────────────────┘                 └───────────┬───────────┘
                                                  │ *
                                                  │
                                                  │ 1
 ┌──────────────────┐ 1             * ┌───────────┴───────────┐
 │     REVIEWS      │─────────────────│       PROVIDERS       │
 │──────────────────│                 │───────────────────────│
 │ id (PK)          │                 │ id (PK)               │
 │ provider_id (FK) │                 │ name, slug            │
 │ user_id (FK)     │                 │ category, food_type   │
 │ rating (Float)   │                 │ address, locality     │
 │ review_text      │                 │ latitude, longitude   │
 │ review_date      │                 │ price_per_month       │
 │ source           │                 │ review_trust_score    │
 └────────┬─────────┘                 │ trust_badge           │
          │ 1                         └───────────┬───────────┘
          │                                       │ 1
          │ 1                                     │
 ┌────────┴─────────┐                             │ 1
 │ REVIEW_ANALYSIS  │                 ┌───────────┴───────────┐
 │──────────────────│                 │ PROVIDER_ANALYSIS_SUM │
 │ id (PK)          │                 │───────────────────────│
 │ review_id (FK)   │                 │ id (PK)               │
 │ sentiment        │                 │ provider_id (FK)      │
 │ is_duplicate     │                 │ positive_pct          │
 │ flagged_reasons  │                 │ negative_pct          │
 └──────────────────┘                 │ ai_summary            │
                                      │ last_analyzed_at      │
                                      └───────────────────────┘
```

### 11.1 Entity Description

1. **Users**: Stores account credentials, email, password hash, role (`user`/`admin`), and registration timestamps.
2. **UserPreferences**: Stores personalized filters (budget range, dietary choices, default search radius).
3. **Providers**: Core entity representing tiffin/mess centers; contains business name, category, food type, coordinates, price, calculated Trust Score, and trust badge.
4. **ProviderSources**: Tracks upstream data lineage (`web_search`, `gemini_discovery`, `manual_user`, `osm_overpass`).
5. **Reviews**: Contains user feedback, numeric ratings, raw text, clean text, and timestamps.
6. **ReviewAnalysis**: Stores NLP audit results per review: sentiment label, duplicate flag, and suspicion reasoning.
7. **ReviewAspects**: Normalized aspect sentiment tags (*taste*, *hygiene*, *delivery*, *price*, *quantity*).
8. **ProviderAnalysisSummary**: Aggregates provider-level metrics: positive/neutral/negative percentages, Gemini AI executive summary, and audit timestamps.
9. **Favorites**: Links users to bookmarked providers.
10. **Reports & AdminAuditLog**: Records user dispute reports and administrative actions.

---

## 12. FUNCTIONAL REQUIREMENTS

- **FR-1: User Authentication**: Secure registration, login, logout, and password hashing using PBKDF2/scrypt.
- **FR-2: Location Geolocation**: Automated GPS detection via HTML5 Geolocation, IP-based fallback, and text forward-geocoding.
- **FR-3: Multi-Radius Search**: Filtering providers across 1 km, 3 km, 5 km, and 10 km boundaries.
- **FR-4: Real Place Ingestion**: Automatic querying of actual tiffin establishments via live Web Search and OpenStreetMap Overpass.
- **FR-5: Review Trust Scoring**: Computation of a 0–100 Trust Score based on duplicate detection, rating-sentiment agreement, and burst analysis.
- **FR-6: Aspect Breakdown**: Sentence-level extraction and scoring of Hygiene, Taste, Quality, Delivery, and Value for Money.
- **FR-7: Grounded AI Summarization**: Synthesis of customer experiences into concise, objective summaries via Google Gemini AI.
- **FR-8: Side-by-Side Comparison**: Structured multi-column comparison of selected providers.
- **FR-9: Geospatial Map Plotting**: Interactive Leaflet.js map with custom food category pins and information popups.
- **FR-10: Dark Mode Toggling**: Persistent client-side dark/light mode toggle with zero page-load flicker.
- **FR-11: User Bookmarking**: Capability for logged-in users to save favorite providers.
- **FR-12: Administrative Telemetry**: Dashboard displaying platform health, flagged reviews, and provider audits.

---

## 13. NON-FUNCTIONAL REQUIREMENTS

- **NFR-1: Usability**: Modern, responsive interface with responsive touch targets and clean typographic hierarchy.
- **NFR-2: Performance**: Spatial queries and local NLP similarity computations complete in under 200 ms.
- **NFR-3: Resilience & Fault Tolerance**: When external APIs (Gemini or Google) fail or timeout, the system falls back gracefully to local deterministic heuristics without crashing.
- **NFR-4: Security**: Robust protection against SQL Injection (via SQLAlchemy parameterized queries), Cross-Site Scripting (XSS), and Cross-Site Request Forgery (CSRF via Flask-WTF).
- **NFR-5: Privacy**: User location is processed ephemerally and never logged to external surveillance servers.
- **NFR-6: Maintainability**: Strict modular structure using Flask Blueprints and independent service classes.
- **NFR-7: Testability**: High test coverage verifiable via automated pytest test runs.

---

## 14. METHODOLOGY

Tifinify follows an **Agile, Modular, and Incremental Software Engineering Methodology**:

1. **Phase 1: Domain Analysis & Problem Formulation**: Field study of student meal challenges in hostel areas; analysis of fake review tactics on commercial directories.
2. **Phase 2: Mathematical Modeling & Trust Architecture**: Formalization of the 4-pillar MCDA Trust Score formula, TF-IDF cosine similarity thresholds, and aspect extraction dictionaries.
3. **Phase 3: Database & Core Service Layer**: Construction of the SQLite relational schema, SQLAlchemy declarative models, and geospatial Haversine modules.
4. **Phase 4: Real-World Place Intelligence**: Development of `WebSearchPlacesAdapter` interfacing with DuckDuckGo and OpenStreetMap Overpass for zero-billing place discovery.
5. **Phase 5: Generative AI & Grounding Pipeline**: Integration of the `google-genai` SDK for grounded review synthesis and in-app API key configuration.
6. **Phase 6: Frontend Development & Geospatial Mapping**: Implementation of Bootstrap 5 responsive templates, Leaflet.js map interactions, and zero-flicker dark mode.
7. **Phase 7: Automated Testing & Verification**: Creation of comprehensive pytest test cases validating NLP algorithms, database operations, and API endpoints.
8. **Phase 8: Cloud Deployment Packaging**: Authoring of `Procfile` and `render.yaml` Blueprints for continuous deployment on cloud infrastructure.

---

## 15. DATABASE DETAILS AND DATA INTEGRITY

Tifinify utilizes **SQLite 3** managed through **SQLAlchemy 2.0 ORM**. SQLite provides zero-latency serverless operations ideal for lightweight deployment, while remaining 100% compatible with PostgreSQL if transitioned to large-scale production.

### 15.1 Data Integrity and Security
- **Relational Integrity**: Foreign key constraints with `CASCADE` deletes ensure orphaned reviews or aspect records are never retained when a provider is removed.
- **Entity Uniqueness**: Unique slug indexing (`providers.slug`) and unique email constraints (`users.email`) prevent race conditions and duplicates.
- **Input Sanitization**: All database queries are compiled into parameterized SQL by SQLAlchemy, eliminating SQL Injection vulnerabilities.
- **Password Hashing**: Stored credentials utilize modern salted one-way hashing (`werkzeug.security.generate_password_hash`).
- **Data Lineage Tracking**: Every provider and review record retains an explicit `source` and `ProviderSource` entry tracing its digital origin.

---

## 16. EXPECTED OUTCOMES

- A fully functional, responsive web application for discovering tiffin and mess services.
- An operational AI Review Trust Engine that accurately differentiates authentic reviews from coordinated spam.
- Real-world business discovery operating dynamically across multiple Indian cities without requiring paid Google billing.
- Clear separation between raw star ratings and explainable review trust scores.
- Interactive OpenMaps visualizer with custom category pins and dark theme map tiles.
- A seamless side-by-side comparison tool for consumer decision support.
- Fully verified codebase passing 22 automated test suites.
- Complete 1-click cloud deployment readiness on Render.com.

---

## 17. ADVANTAGES

1. **Objective Review Verification**: Eliminates reliance on easily manipulated star averages by calculating mathematical trust scores.
2. **Zero Commercial API Costs**: Functions 100% free using OpenStreetMap, DuckDuckGo web search, and free-tier Gemini AI.
3. **Transparent Explainability**: Users can inspect exact positive and warning signals justifying why a provider received their trust badge.
4. **Actionable Aspect Breakdowns**: Separately rates food hygiene, taste, delivery, and pricing rather than presenting a single opaque number.
5. **High Fault Tolerance**: Built-in fallback architecture guarantees that API outages never crash the platform.
6. **Student & Bachelor Focused**: Specifically designed for daily recurring food subscriptions rather than one-time luxury dining.

---

## 18. LIMITATIONS

- **Web Search Heuristics**: Discovery accuracy depends on the availability of public web listings and OpenStreetMap coverage for remote rural areas.
- **Client-Side Geolocation Accuracy**: HTML5 Geolocation precision depends on user hardware (GPS chip vs. ISP cellular tower IP).
- **Gemini Free-Tier Rate Limits**: Extremely heavy burst traffic may encounter temporary rate limits if a private Gemini key is not supplied.
- **English Language Focus**: Current NLP keyword extractors are optimized for English and transliterated Hindi/Hinglish food terminology.

---

## 19. FUTURE SCOPE

- **Direct Online Subscriptions**: Introduce digital payment gateway integration (UPI, Razorpay) for automated monthly meal subscriptions.
- **Daily Menu Publishing**: Provide vendor portals where mess owners can post their daily lunch and dinner menus each morning.
- **Multilingual NLP**: Expand aspect extraction and review trust sentiment analysis to regional Indian languages (Hindi, Marathi, Bengali, Telugu).
- **Mobile Native Applications**: Package the responsive web system into native Android and iOS apps using Flutter or React Native.
- **IoT Smart Kitchen Hygiene Badging**: Partner with local food safety bodies (FSSAI) to integrate verified kitchen hygiene certificates.

---

## 20. CONCLUSION

**Tifinify** demonstrates how modern computer science methodologies—spanning full-stack web architecture, natural language processing, machine learning heuristics, spatial computing, and generative artificial intelligence—can be synthesized into an impactful, consumer-centric software product.

The defining achievement of the project is its **Explainable Review Intelligence Architecture**. By decoupling raw, manipulable star ratings from mathematical Review Trust Scores, Tifinify equips students, bachelors, and working professionals with the transparency needed to protect their health and finances.

Furthermore, the project’s zero-billing search design, resilient fallback architecture, responsive dark/light UI, and 100% automated test coverage establish Tifinify as a complete, robust, and industry-grade software engineering project suitable for the Master of Computer Application degree.

---

## 21. REFERENCES

1. **Tifinify GitHub Repository**: [https://github.com/pranab1411/tifinify](https://github.com/pranab1411/tifinify)
2. **Flask Documentation**: Pallets Projects — *Flask Web Development Documentation* (v3.0.x), [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
3. **Google Gemini API Documentation**: Google AI for Developers — *Gemini API Reference and Python SDK (`google-genai`)*, [https://ai.google.dev/](https://ai.google.dev/)
4. **Scikit-Learn Documentation**: Pedregosa et al. — *Machine Learning in Python (TF-IDF & Cosine Similarity)*, [https://scikit-learn.org/](https://scikit-learn.org/)
5. **SQLAlchemy Documentation**: Michael Bayer — *SQLAlchemy 2.0 Unified Documentation*, [https://www.sqlalchemy.org/](https://www.sqlalchemy.org/)
6. **Leaflet.js Documentation**: Vladimir Agafonkin — *Leaflet: An Open-Source JavaScript Library for Mobile-Friendly Interactive Maps*, [https://leafletjs.com/](https://leafletjs.com/)
7. **OpenStreetMap & Overpass API**: OpenStreetMap Foundation — *Overpass API Documentation & Query Guide*, [https://wiki.openstreetmap.org/wiki/Overpass_API](https://wiki.openstreetmap.org/wiki/Overpass_API)
8. **Bootstrap Documentation**: The Bootstrap Authors — *Bootstrap v5.3 Framework & Color Modes Guide*, [https://getbootstrap.com/](https://getbootstrap.com/)
9. **Jindal, N., & Liu, B.** (2008). *Opinion Spam and Analysis*. Proceedings of the 2008 International Conference on Web Search and Data Mining (WSDM '08), ACM.
10. **Python Software Foundation**: *Python 3.11/3.12/3.14 Standard Library and Language Reference*, [https://docs.python.org/3/](https://docs.python.org/3/)

# Clawback — Smart Consumer Complaint System

> AI-powered consumer dispute resolution. Predicts your refund odds and writes the perfect complaint based on 4M+ real consumer complaints.

A Data Science course project demonstrating end-to-end ML pipeline from raw text data to deployed web application.

---

## What this project does

You describe a problem you're having with a company (wrong charge, failed delivery, cancelled service still billed). Clawback then:

1. **Classifies** your complaint into a CFPB category using NLP
2. **Predicts** your probability of getting a refund using a trained classification model
3. **Looks up** that company's historical resolution rate
4. **Analyzes** which "winning phrases" you used (and which to add)
5. **Generates** a complaint letter optimized using patterns from successful complaints

---

## Data Science Concepts Used

| Concept | Where it's used |
|---|---|
| **Data Preprocessing** | Cleaning 100K+ raw CFPB complaint records |
| **Exploratory Data Analysis** | Visualizations of complaint trends, company resolution rates |
| **NLP Pipeline** | Tokenization, stopword removal, lemmatization |
| **Text Vectorization** | TF-IDF on complaint narratives |
| **Feature Engineering** | Length, dollar amounts, legal terms as model features |
| **Multi-class Classification** | Predicting complaint category and resolution outcome |
| **Model Evaluation** | Accuracy, precision, recall, F1, confusion matrix |
| **Pattern Mining** | N-gram analysis with lift statistics on winning vs losing complaints |

---

## Project Structure

```
clawback/
├── app.py                          # Flask backend with ML inference
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── notebooks/
│   └── Clawback_ML_Training.ipynb  # Run on Google Colab to train models
│
├── models/                         # Trained models go here (from Colab)
│   ├── category_model.pkl          # Model 1
│   ├── category_vectorizer.pkl
│   ├── category_encoder.pkl
│   ├── outcome_model.pkl           # Model 2 (the centerpiece)
│   ├── outcome_vectorizer.pkl
│   ├── outcome_encoder.pkl
│   ├── winning_patterns.json       # Model 3 output
│   └── company_stats.csv           # Company-level resolution rates
│
├── templates/
│   ├── index.html                  # Landing page (Voxr-inspired)
│   └── app.html                    # The actual analyzer tool
│
└── static/
    ├── css/
    │   ├── landing.css
    │   └── app.css
    └── js/
        ├── landing.js
        └── app.js
```

---

## Setup — Step by Step

### Step 1: Train the models on Colab (do this first)

1. Go to https://colab.research.google.com
2. Upload `notebooks/Clawback_ML_Training.ipynb`
3. Run all cells (Runtime → Run all). Total time: ~10-15 minutes.
4. The last cell will download `clawback_models.zip` to your computer.

### Step 2: Set up the Flask app

On your local machine:

```bash
# Navigate to project folder
cd clawback

# (Optional but recommended) Create a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Place trained models in /models folder

1. Extract `clawback_models.zip` (downloaded from Colab in Step 1)
2. Move all the extracted files (`.pkl`, `.json`, `.csv`) into the `models/` folder

Your models folder should look like:
```
models/
├── category_model.pkl
├── category_vectorizer.pkl
├── category_encoder.pkl
├── outcome_model.pkl
├── outcome_vectorizer.pkl
├── outcome_encoder.pkl
├── winning_patterns.json
└── company_stats.csv
```

### Step 4: Run the app

```bash
python app.py
```

Open your browser to: `http://localhost:5000`

---

## How It Works (Technical Detail)

### Model 1 — Category Classifier
- **Input:** Raw user complaint text
- **Vectorization:** TF-IDF (5,000 features, 1-2 grams)
- **Model:** Logistic Regression (multi-class)
- **Output:** CFPB category (Credit Card, Debt Collection, Mortgage, etc.)

### Model 2 — Resolution Predictor (the centerpiece)
- **Input:** TF-IDF vector + 4 engineered features (length, word count, has $ amount, has legal terms)
- **Vectorization:** TF-IDF (3,000 features, 1-2 grams)
- **Model:** Logistic Regression with class_weight='balanced'
- **Output:** Probability distribution over 3 outcomes (monetary relief, non-monetary relief, no relief)

### Model 3 — Pattern Mining
- **Method:** Separate winners (got money) from losers (got nothing)
- **Compute:** Word/phrase frequency in each group
- **Calculate:** Lift = (winner rate) / (loser rate) for each n-gram
- **Output:** Top 100 phrases statistically more common in winning complaints

### Letter Generation
- Template-based generation informed by patterns from Model 3
- Includes structural elements found in successful complaints
- Suggests additional phrases to incorporate based on missing winning patterns

---

## Course Requirements Met

This project demonstrates every major concept from the syllabus:

- **Python Basics & Advanced** → Data loading, preprocessing pipelines
- **File Handling** → CSV/JSON/PKL file management
- **Introduction to ML** → Supervised classification with multiple models
- **NLP Basics** → Tokenization, stopwords, lemmatization, TF-IDF
- **Advanced NLP** → Multi-class text classification, n-gram analysis
- **Generative AI** → Template-based letter generation guided by ML patterns
- **Flask Framework** → Full web app with REST API endpoints

---

## Dataset

**Source:** [Consumer Financial Protection Bureau (CFPB) Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/)

- **Size:** 4M+ complaints (sampled to 100K for training efficiency)
- **License:** Public domain (U.S. Government work)
- **Fields used:** Consumer complaint narrative, Product, Company, Company response to consumer

---

## Tech Stack

- **Backend:** Flask 3.0
- **ML:** scikit-learn 1.4, NLTK 3.8
- **Data:** pandas, numpy, scipy
- **Frontend:** HTML/CSS/JS (no frameworks - keeps it lightweight)
- **Fonts:** Geist (Vercel), Instrument Serif

---

## Demo Mode

If the trained models aren't loaded yet (you haven't run the Colab notebook), the app still works in **demo mode** — predictions are estimated based on simple text features so you can see the UI flow even without trained models.

---

## What to Submit

For your course submission, include:
1. The full `clawback/` folder
2. The `Clawback_ML_Training.ipynb` notebook (with all cells run)
3. The `eda_overview.png` and `confusion_matrix.png` files (auto-generated)
4. A brief report explaining the data science methodology (use the model evaluation outputs from the notebook)

---

Built as a Data Science project. Powered by real consumer protection data.

"""
Clawback - Smart Consumer Complaint System
Main Flask application with ML inference and complaint generation.
"""

from flask import Flask, render_template, request, jsonify
import joblib
import json
import re
import os
import pandas as pd
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data on first run
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

app = Flask(__name__)

# ============================================================
# LOAD ML MODELS (trained in Colab notebook)
# ============================================================
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODELS_LOADED = False

category_model = None
category_vectorizer = None
category_encoder = None
outcome_model = None
outcome_vectorizer = None
outcome_encoder = None
winning_patterns = {}
company_stats = None

def load_models():
    """Load all trained ML models. Called on app startup."""
    global category_model, category_vectorizer, category_encoder
    global outcome_model, outcome_vectorizer, outcome_encoder
    global winning_patterns, company_stats, MODELS_LOADED

    try:
        category_model = joblib.load(os.path.join(MODELS_DIR, 'category_model.pkl'))
        category_vectorizer = joblib.load(os.path.join(MODELS_DIR, 'category_vectorizer.pkl'))
        category_encoder = joblib.load(os.path.join(MODELS_DIR, 'category_encoder.pkl'))

        outcome_model = joblib.load(os.path.join(MODELS_DIR, 'outcome_model.pkl'))
        outcome_vectorizer = joblib.load(os.path.join(MODELS_DIR, 'outcome_vectorizer.pkl'))
        outcome_encoder = joblib.load(os.path.join(MODELS_DIR, 'outcome_encoder.pkl'))

        with open(os.path.join(MODELS_DIR, 'winning_patterns.json'), 'r') as f:
            winning_patterns = json.load(f)

        company_stats = pd.read_csv(os.path.join(MODELS_DIR, 'company_stats.csv'))

        MODELS_LOADED = True
        print('[Clawback] All ML models loaded successfully.')
    except FileNotFoundError as e:
        print(f'[Clawback] WARNING: Model files not found ({e}).')
        print('[Clawback] Run the Colab notebook first and place trained models in /models folder.')
        print('[Clawback] App will run in demo mode with placeholder predictions.')

# ============================================================
# TEXT PREPROCESSING (must match training)
# ============================================================
stop_words = set(stopwords.words('english')) if MODELS_LOADED or True else set()
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if not text:
        return ''
    text = str(text).lower()
    text = re.sub(r'x{2,}', ' ', text)
    text = re.sub(r'[^a-z0-9$\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [lemmatizer.lemmatize(w) for w in text.split() if w not in stop_words and len(w) > 2]
    return ' '.join(tokens)

# ============================================================
# FEATURE ENGINEERING
# ============================================================
def extract_features(text):
    """Extract the same engineered features used during training."""
    return {
        'narrative_length': len(text),
        'word_count': len(text.split()),
        'has_dollar_amount': 1 if re.search(r'\$\d+', text) else 0,
        'has_legal_terms': 1 if re.search(
            r'fcra|fdcpa|tila|respa|cfpb|attorney|lawyer|sue|lawsuit|fraud|violation',
            text.lower()
        ) else 0
    }

# ============================================================
# ML INFERENCE
# ============================================================
def predict_category(text):
    """Use Model 1 to classify complaint category."""
    if not MODELS_LOADED:
        return 'Demo Category', 0.0
    cleaned = preprocess_text(text)
    X = category_vectorizer.transform([cleaned])
    pred = category_model.predict(X)[0]
    proba = category_model.predict_proba(X)[0].max()
    return category_encoder.inverse_transform([pred])[0], float(proba)

def predict_outcome(text):
    """Use Model 2 to predict probability of monetary relief."""
    if not MODELS_LOADED:
        # Demo fallback - rough estimate based on text features
        features = extract_features(text)
        score = 35 + (features['has_dollar_amount'] * 15) + (features['has_legal_terms'] * 20) + min(features['word_count'] / 20, 10)
        return min(score, 85), {'monetary_relief': score, 'non_monetary_relief': 25, 'no_relief': 100 - score - 25}

    from scipy.sparse import hstack, csr_matrix

    cleaned = preprocess_text(text)
    X_text = outcome_vectorizer.transform([cleaned])
    features = extract_features(text)
    X_extra = csr_matrix([[
        features['narrative_length'],
        features['word_count'],
        features['has_dollar_amount'],
        features['has_legal_terms']
    ]])
    X = hstack([X_text, X_extra])

    probas = outcome_model.predict_proba(X)[0]
    classes = outcome_encoder.classes_

    proba_dict = {cls: float(p) * 100 for cls, p in zip(classes, probas)}

    # The success score is the probability of monetary relief
    success_score = proba_dict.get('monetary_relief', 0)
    return success_score, proba_dict

def get_company_score(company_name):
    """Look up a company's historical resolution rate."""
    if not MODELS_LOADED or company_stats is None:
        return None

    # Fuzzy match on company name
    matches = company_stats[company_stats['Company'].str.contains(company_name, case=False, na=False, regex=False)]
    if len(matches) > 0:
        match = matches.iloc[0]
        return {
            'name': match['Company'],
            'total_complaints': int(match['total_complaints']),
            'monetary_relief_rate': float(match['monetary_relief_rate']),
            'any_relief_rate': float(match['any_relief_rate'])
        }
    return None

def get_winning_keywords(text, top_n=8):
    """Find which winning patterns are present (or missing) in the user's complaint."""
    if not winning_patterns:
        return {'present': [], 'suggested': []}

    cleaned = preprocess_text(text).lower()
    present = []
    suggested = []

    for phrase, lift in list(winning_patterns.items())[:50]:
        if phrase in cleaned:
            present.append({'phrase': phrase, 'lift': lift})
        else:
            suggested.append({'phrase': phrase, 'lift': lift})

    return {
        'present': present[:top_n],
        'suggested': suggested[:top_n]
    }

# ============================================================
# COMPLAINT LETTER GENERATION
# ============================================================
def generate_complaint_letter(user_input, company, predicted_category, success_score, missing_patterns):
    """
    Generate an optimized complaint letter using template-based approach
    informed by the patterns extracted from successful complaints.
    """
    today = datetime.now().strftime('%B %d, %Y')

    # Pattern-informed phrasing
    legal_emphasis = "I am formally requesting resolution of this matter. " if 'monetary' not in user_input.lower() else ""

    suggested_phrases_text = ""
    if missing_patterns and len(missing_patterns) > 0:
        suggested_phrases_text = "\n\nPATTERN-BASED RECOMMENDATIONS (incorporate where relevant):\n"
        for p in missing_patterns[:5]:
            suggested_phrases_text += f"  • Consider mentioning: '{p['phrase']}' (appears {p['lift']}x more often in successful complaints)\n"

    letter = f"""Date: {today}

To Whom It May Concern,
{company} Customer Relations Department

RE: Formal Consumer Complaint and Request for Resolution

I am writing to formally lodge a complaint regarding a recent experience with {company}, classified under the category of {predicted_category}.

DESCRIPTION OF ISSUE:
{user_input}

REQUESTED RESOLUTION:
I respectfully request that {company} take immediate action to resolve this matter. Based on consumer protection regulations and the documented nature of this issue, I am requesting:

1. A full investigation into this matter within 14 business days
2. Appropriate monetary compensation for damages incurred
3. Written confirmation of the steps taken to prevent recurrence

{legal_emphasis}Should this matter not be resolved through your internal complaint process, I reserve the right to escalate to the relevant consumer protection agency, including but not limited to the Consumer Financial Protection Bureau (CFPB), Federal Trade Commission (FTC), or applicable state consumer protection authorities.

Please consider this a formal notice. I expect a written response within 15 business days.

Sincerely,
[Your Name]
[Your Contact Information]
[Account/Reference Number, if applicable]

---
PREDICTED SUCCESS SCORE: {success_score:.1f}%
(Based on machine learning analysis of {len(winning_patterns) if winning_patterns else 'thousands of'} similar past complaints)
{suggested_phrases_text}
"""
    return letter

# ============================================================
# ROUTES
# ============================================================
@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')

@app.route('/app')
def app_page():
    """The actual complaint analysis tool."""
    return render_template('app.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main API endpoint - takes complaint, returns full analysis."""
    data = request.get_json()
    user_text = data.get('complaint', '').strip()
    company = data.get('company', 'the Company').strip() or 'the Company'

    if not user_text or len(user_text) < 20:
        return jsonify({
            'success': False,
            'error': 'Please describe your complaint in at least 20 characters.'
        }), 400

    # Run ML pipeline
    category, category_confidence = predict_category(user_text)
    success_score, outcome_probas = predict_outcome(user_text)
    company_info = get_company_score(company)
    keywords = get_winning_keywords(user_text)

    # Generate the complaint letter
    letter = generate_complaint_letter(
        user_input=user_text,
        company=company,
        predicted_category=category,
        success_score=success_score,
        missing_patterns=keywords['suggested']
    )

    return jsonify({
        'success': True,
        'analysis': {
            'category': category,
            'category_confidence': round(category_confidence * 100, 1),
            'success_score': round(success_score, 1),
            'outcome_breakdown': {k: round(v, 1) for k, v in outcome_probas.items()},
            'company_info': company_info,
            'keywords_present': keywords['present'],
            'keywords_suggested': keywords['suggested'],
            'feature_analysis': extract_features(user_text)
        },
        'letter': letter,
        'models_loaded': MODELS_LOADED
    })

@app.route('/api/health')
def health():
    """Status check endpoint."""
    return jsonify({
        'status': 'ok',
        'models_loaded': MODELS_LOADED,
        'companies_in_db': len(company_stats) if company_stats is not None else 0,
        'winning_patterns_count': len(winning_patterns)
    })

# ============================================================
# STARTUP
# ============================================================
load_models()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

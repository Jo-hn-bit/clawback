# Clawback Setup Guide — From Zero to Running

This guide walks you through getting Clawback running locally. Total time: ~20 minutes (most of it is Colab training).

---

## Prerequisites

- Python 3.10 or 3.11 installed (NOT 3.12 — some ML packages have issues)
- A Google account (for Colab)
- A web browser

---

## PART 1: Train the Models on Google Colab

This generates the trained ML models that power the app.

### 1.1 Open Colab
Go to https://colab.research.google.com and sign in with your Google account.

### 1.2 Upload the Training Notebook
- Click **File → Upload notebook**
- Upload `notebooks/Clawback_ML_Training.ipynb` from this project

### 1.3 Run All Cells
- Click **Runtime → Run all** (or press Ctrl+F9)
- The notebook will:
  1. Install dependencies (1 min)
  2. Download the CFPB dataset (~2-3 min, 250MB)
  3. Preprocess 100K complaints (1-2 min)
  4. Generate EDA visualizations (1 min)
  5. Train 3 ML models (3-5 min)
  6. Save everything as `clawback_models.zip`

### 1.4 Download the Files
The last cell auto-downloads:
- `clawback_models.zip` ← Drop this into your project's `/models` folder
- `eda_overview.png` ← Use in your project report
- `confusion_matrix.png` ← Use in your project report

If the download doesn't auto-trigger, find the files in Colab's file panel (left sidebar) and right-click → Download.

---

## PART 2: Set Up the Flask App Locally

### 2.1 Verify Python Version

Open Command Prompt (Windows) or Terminal (Mac/Linux):

```bash
python --version
```

You should see `Python 3.10.x` or `Python 3.11.x`. If you have 3.12+, install 3.11 from python.org first.

### 2.2 Navigate to the Project Folder

```bash
cd path/to/clawback
```

### 2.3 Create a Virtual Environment (Recommended)

This keeps your Python packages isolated.

```bash
python -m venv venv
```

**Activate it:**

Windows:
```cmd
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal prompt.

### 2.4 Install Dependencies

```bash
pip install -r requirements.txt
```

This takes 2-3 minutes the first time.

---

## PART 3: Place the Trained Models

### 3.1 Extract the Models Zip

Find `clawback_models.zip` (downloaded from Colab in Part 1) and extract it.

### 3.2 Move Files into /models Folder

Copy ALL extracted files into the `clawback/models/` folder:

```
clawback/
└── models/
    ├── category_model.pkl          ← put these here
    ├── category_vectorizer.pkl
    ├── category_encoder.pkl
    ├── outcome_model.pkl
    ├── outcome_vectorizer.pkl
    ├── outcome_encoder.pkl
    ├── winning_patterns.json
    └── company_stats.csv
```

---

## PART 4: Run the App

### 4.1 Start the Server

Make sure your virtual environment is still active, then:

```bash
python app.py
```

You should see:
```
[Clawback] All ML models loaded successfully.
 * Running on http://0.0.0.0:5000
```

### 4.2 Open in Browser

Visit: **http://localhost:5000**

You'll see the landing page. Click "Get my money back" to access the analyzer.

---

## Testing It Works

Try this complaint to verify everything is wired up:

**Company:** Capital One

**Complaint:**
> I was charged a $35 overdraft fee even though I had funds available in my account. I have been a customer for 8 years and called to dispute the charge but was told there's nothing they can do. The transaction history clearly shows my balance was positive when the charge occurred. I am requesting a refund of the $35 fee and an explanation for why this was charged.

You should see:
- A predicted success score (probably 40-70%)
- Company information about Capital One (if they're in the dataset)
- Pattern analysis showing winning phrases used
- A complete complaint letter ready to copy

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
Your virtual environment isn't activated. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux), then try again.

### "[Clawback] WARNING: Model files not found"
You haven't placed the trained models in the `/models` folder yet. The app will run in demo mode but predictions will be approximations. Complete Part 3.

### Port 5000 already in use
Either kill whatever is using port 5000, or change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### "ImportError" on scikit-learn or numpy
Your Python version is likely too new (3.12+). Install Python 3.11 and try again.

### Colab cell fails on download
Try this cell instead to download manually:
```python
from google.colab import files
files.download('/content/clawback_models.zip')
```

### Models load but predictions seem wrong
The CFPB dataset is biased toward financial complaints (banking, credit cards, debt). For non-financial complaints (food delivery, e-commerce), predictions will be less accurate. This is a known limitation we'll mention in the project report.

---

## What to Show Your Professor

1. **Live demo** of the app at localhost:5000
2. **The Colab notebook** with all cells run (shows EDA, training, evaluation)
3. **The two PNG files** (`eda_overview.png`, `confusion_matrix.png`)
4. **The README.md** explaining the architecture
5. **The model evaluation metrics** printed in the notebook (accuracy, classification report)

---

You're done. Time to fight some companies.

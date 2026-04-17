// ============================================
// CLAWBACK - APP PAGE LOGIC
// ============================================

const els = {
  company: document.getElementById('company-input'),
  complaint: document.getElementById('complaint-input'),
  charCount: document.getElementById('char-count'),
  analyzeBtn: document.getElementById('analyze-btn'),
  results: document.getElementById('results'),
  category: document.getElementById('result-category'),
  scoreValue: document.getElementById('score-value'),
  scoreFill: document.getElementById('score-fill'),
  scorePill: document.getElementById('score-pill'),
  probMonetary: document.getElementById('prob-monetary'),
  probNonMonetary: document.getElementById('prob-non-monetary'),
  probNoRelief: document.getElementById('prob-no-relief'),
  companyContent: document.getElementById('company-content'),
  featuresGrid: document.getElementById('features-grid'),
  patternsPresent: document.getElementById('patterns-present'),
  patternsSuggested: document.getElementById('patterns-suggested'),
  letterOutput: document.getElementById('letter-output'),
  copyBtn: document.getElementById('copy-btn'),
  restartBtn: document.getElementById('restart-btn'),
};

// Update character count live
els.complaint.addEventListener('input', () => {
  els.charCount.textContent = els.complaint.value.length;
});

// Analyze button click
els.analyzeBtn.addEventListener('click', async () => {
  const complaint = els.complaint.value.trim();
  const company = els.company.value.trim();

  if (complaint.length < 20) {
    alert('Please describe your complaint in at least 20 characters.');
    return;
  }

  els.analyzeBtn.classList.add('loading');
  els.analyzeBtn.disabled = true;

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ complaint, company }),
    });

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Analysis failed');
    }

    renderResults(data, company);

  } catch (err) {
    alert('Something went wrong: ' + err.message);
    console.error(err);
  } finally {
    els.analyzeBtn.classList.remove('loading');
    els.analyzeBtn.disabled = false;
  }
});

// Render the results
function renderResults(data, company) {
  const a = data.analysis;

  // Score
  els.category.textContent = a.category;
  animateNumber(els.scoreValue, 0, Math.round(a.success_score), 1200);
  setTimeout(() => {
    els.scoreFill.style.width = a.success_score + '%';
  }, 100);

  // Pill color based on score
  if (a.success_score >= 60) {
    els.scorePill.textContent = 'Strong case';
    els.scorePill.className = 'gauge-pill gauge-pill-success';
  } else if (a.success_score >= 35) {
    els.scorePill.textContent = 'Moderate odds';
    els.scorePill.className = 'gauge-pill';
    els.scorePill.style.background = 'rgba(245,158,11,0.15)';
    els.scorePill.style.color = '#f59e0b';
    els.scorePill.style.border = '1px solid rgba(245,158,11,0.3)';
  } else {
    els.scorePill.textContent = 'Tough case';
    els.scorePill.className = 'gauge-pill';
    els.scorePill.style.background = 'rgba(239,68,68,0.15)';
    els.scorePill.style.color = '#ef4444';
    els.scorePill.style.border = '1px solid rgba(239,68,68,0.3)';
  }

  // Outcome breakdown
  const ob = a.outcome_breakdown;
  els.probMonetary.textContent = (ob.monetary_relief || 0).toFixed(1) + '%';
  els.probNonMonetary.textContent = (ob.non_monetary_relief || 0).toFixed(1) + '%';
  els.probNoRelief.textContent = (ob.no_relief || 0).toFixed(1) + '%';

  // Company info
  if (a.company_info) {
    const ci = a.company_info;
    const reliefRate = ci.monetary_relief_rate;
    const reliefColor = reliefRate >= 30 ? '#10b981' : reliefRate >= 15 ? '#f59e0b' : '#ef4444';

    els.companyContent.innerHTML = `
      <div class="company-name">${escapeHtml(ci.name)}</div>
      <div class="company-meta">${ci.total_complaints.toLocaleString()} historical complaints in our database</div>
      <div class="company-stat-grid">
        <div class="company-stat">
          <div class="company-stat-value">${reliefRate}%</div>
          <div class="company-stat-label">Monetary relief rate</div>
        </div>
        <div class="company-stat">
          <div class="company-stat-value">${ci.any_relief_rate}%</div>
          <div class="company-stat-label">Any relief rate</div>
        </div>
      </div>
    `;
  } else {
    els.companyContent.innerHTML = `
      <p class="empty-text">No historical data available for "${escapeHtml(company || 'this company')}". Predictions are based on the complaint text alone.</p>
    `;
  }

  // Feature analysis
  const fa = a.feature_analysis;
  els.featuresGrid.innerHTML = `
    <div class="feature-item ${fa.word_count >= 50 ? 'feature-good' : ''}">
      <div class="feature-label">Word count</div>
      <div class="feature-value">${fa.word_count}</div>
    </div>
    <div class="feature-item ${fa.has_dollar_amount ? 'feature-good' : ''}">
      <div class="feature-label">Mentions $ amount</div>
      <div class="feature-value">${fa.has_dollar_amount ? 'Yes ✓' : 'No'}</div>
    </div>
    <div class="feature-item ${fa.has_legal_terms ? 'feature-good' : ''}">
      <div class="feature-label">Legal language</div>
      <div class="feature-value">${fa.has_legal_terms ? 'Yes ✓' : 'No'}</div>
    </div>
    <div class="feature-item">
      <div class="feature-label">Character count</div>
      <div class="feature-value">${fa.narrative_length}</div>
    </div>
  `;

  // Patterns
  els.patternsPresent.innerHTML = a.keywords_present.length
    ? a.keywords_present.map(k => `
        <div class="pattern-item">
          <span class="pattern-phrase">${escapeHtml(k.phrase)}</span>
          <span class="pattern-lift">${k.lift}x lift</span>
        </div>
      `).join('')
    : '<p class="empty-text">None of the historical winning phrases detected. See suggestions →</p>';

  els.patternsSuggested.innerHTML = a.keywords_suggested.length
    ? a.keywords_suggested.slice(0, 6).map(k => `
        <div class="pattern-item">
          <span class="pattern-phrase">${escapeHtml(k.phrase)}</span>
          <span class="pattern-lift">${k.lift}x lift</span>
        </div>
      `).join('')
    : '<p class="empty-text">Your complaint already contains the strongest patterns.</p>';

  // Letter
  els.letterOutput.textContent = data.letter;

  // Show results and scroll
  els.results.style.display = 'block';
  setTimeout(() => {
    els.results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 50);
}

// Copy letter button
els.copyBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(els.letterOutput.textContent).then(() => {
    const orig = els.copyBtn.innerHTML;
    els.copyBtn.innerHTML = '<span>✓</span> Copied!';
    setTimeout(() => {
      els.copyBtn.innerHTML = orig;
    }, 2000);
  });
});

// Restart
els.restartBtn.addEventListener('click', () => {
  els.results.style.display = 'none';
  els.complaint.value = '';
  els.company.value = '';
  els.charCount.textContent = '0';
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Helpers
function animateNumber(el, from, to, duration) {
  const start = performance.now();
  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

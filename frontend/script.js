// ===== STATE =====
let resumeText = '', fullResumeText = '', analysisData = null, careerData = null;
let isAuthenticated = false, userEmail = '', isLoginMode = true;
let mockMode = false, chartInstance = null;
let interviewQuestions = [], currentQIndex = 0, scores = [];
let allJobs = [];

// ===== DOM =====
const $ = id => document.getElementById(id);
const mockToggle = $('mock-mode-toggle');
const modeLabel = $('mode-label');

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    mockToggle.addEventListener('change', () => {
        mockMode = mockToggle.checked;
        modeLabel.textContent = mockMode ? 'Mock' : 'Live';
    });
    // DEFAULT: Live mode (unchecked)
    mockToggle.checked = false;
    mockMode = false;
    modeLabel.textContent = 'Live';

    setupUpload();
    setupAuth();
    setupTabs();
    setupInterview();
    setupSkillGap();
    $('hamburger-btn').addEventListener('click', () => $('nav-links').classList.toggle('open'));
    $('analyze-career-btn').addEventListener('click', analyzeCareer);
});

// ===== NAVIGATION =====
function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active-page'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    const el = $('page-' + page);
    if (el) { el.classList.add('active-page'); }
    const link = document.querySelector(`.nav-link[data-page="${page}"]`);
    if (link) link.classList.add('active');
    $('nav-links').classList.remove('open');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    // Trigger renders for data-dependent pages
    if (page === 'jobs') renderJobs();
    if (page === 'roadmap') renderRoadmap();
}

// ===== UPLOAD =====
function setupUpload() {
    const dz = $('hero-drop-zone'), fi = $('resume-upload');
    if (!dz || !fi) return;
    ['dragenter','dragover'].forEach(e => dz.addEventListener(e, ev => { ev.preventDefault(); dz.classList.add('drag-over'); }));
    ['dragleave','drop'].forEach(e => dz.addEventListener(e, () => dz.classList.remove('drag-over')));
    dz.addEventListener('dragover', e => e.preventDefault());
    dz.addEventListener('drop', e => { e.preventDefault(); handleFiles(e.dataTransfer.files); });
    fi.addEventListener('change', e => handleFiles(e.target.files));
}

async function handleFiles(files) {
    if (!files.length) return;
    if (files[0].type !== 'application/pdf') return showToast('Please upload a PDF file.', 'error');
    const fd = new FormData();
    fd.append('resume', files[0]);
    fd.append('mock_mode', mockMode);
    $('upload-loading').classList.remove('hidden');
    $('hero-drop-zone').style.display = 'none';
    try {
        const res = await fetch('/api/upload_resume', { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Upload failed');
        resumeText = data.text_preview;
        fullResumeText = data.full_text || resumeText;
        analysisData = data.analysis;
        populateAnalysis(analysisData);
        showToast('Resume analyzed successfully!', 'success');
        navigateTo('dashboard');
    } catch (e) { 
        showToast(e.message, 'error'); 
        $('hero-drop-zone').style.display = ''; 
    }
    finally { $('upload-loading').classList.add('hidden'); }
}

// ===== CAREER ANALYSIS =====
async function analyzeCareer() {
    const role = $('target-role-input').value.trim();
    if (!role) return showToast('Please enter a target role.', 'error');
    if (!resumeText) return showToast('Please upload a resume first.', 'error');
    $('career-loading').classList.remove('hidden');
    $('analyze-career-btn').disabled = true;
    $('analyze-career-btn').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
    try {
        const res = await fetch('/api/analyze_career', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ resume_text: fullResumeText || resumeText, target_role: role, mock_mode: mockMode })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        careerData = data;
        populateCareerResults(data);
        allJobs = data.jobs || [];
        showToast('Career analysis complete!', 'success');
    } catch (e) { showToast(e.message, 'error'); }
    finally { 
        $('career-loading').classList.add('hidden'); 
        $('analyze-career-btn').disabled = false;
        $('analyze-career-btn').innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze';
    }
}

// ===== POPULATE FUNCTIONS =====
function populateAnalysis(d) {
    if (!d) return;
    animateScore('ats-circle', d.ats_score || 0, 100);
    animateCount('ats-score-val', d.ats_score || 0);
    $('career-level-chip').textContent = d.career_level || '—';
    fillList('strengths-list', d.strengths);
    fillList('weaknesses-list', d.weaknesses);
    fillList('improvements-list', d.improvements);
    $('skills-tags').innerHTML = (d.skills||[]).map(s => `<span class="tag">${s}</span>`).join('');
    $('missing-skills-tags').innerHTML = (d.missing_skills||[]).map(s => `<span class="tag">${s}</span>`).join('');
    $('score-cards').style.display = 'flex';
}

function populateCareerResults(d) {
    const m = d.role_match || {};
    animateScore('match-circle', m.match_percentage || 0, 100);
    animateCount('match-percent-val', m.match_percentage || 0);
    $('readiness-chip').textContent = m.readiness_level || '—';
    const level = m.readiness_level || '';
    $('readiness-chip').className = 'chip ' + (level.includes('Ready') ? 'chip-green' : level.includes('Over') ? 'chip-yellow' : 'chip-red');
    
    // LinkedIn data
    const li = d.linkedin_optimization || {};
    $('li-about').textContent = li.about_section || 'Run career analysis to generate LinkedIn suggestions.';
    fillList('li-posts', li.post_ideas);
    
    // Skill gap from career analysis
    const gaps = m.skill_gap_analysis || [];
    if (gaps.length > 0) {
        const gapHtml = gaps.map(g => `
            <li><strong>${g.skill}</strong> <span class="chip ${g.gap_level === 'High' ? 'chip-red' : g.gap_level === 'Medium' ? 'chip-yellow' : 'chip-green'}">${g.gap_level}</span><br><small style="color:var(--text3)">${g.how_to_bridge}</small></li>
        `).join('');
        const weakList = $('weaknesses-list');
        if (weakList) weakList.innerHTML += gapHtml;
    }
}

function fillList(id, items) {
    const el = $(id);
    if (!el || !items) return;
    el.innerHTML = items.map(i => `<li>${i}</li>`).join('');
}

function animateScore(circleId, value, max) {
    const circle = $(circleId);
    if (!circle) return;
    const circumference = 2 * Math.PI * 52;
    const offset = circumference - (value / max) * circumference;
    circle.style.strokeDasharray = circumference;
    setTimeout(() => { circle.style.strokeDashoffset = offset; }, 100);
}

function animateCount(id, target) {
    const el = $(id);
    if (!el) return;
    let current = 0;
    target = parseInt(target) || 0;
    const step = Math.max(1, Math.floor(target / 30));
    const timer = setInterval(() => {
        current += step;
        if (current >= target) { current = target; clearInterval(timer); }
        el.textContent = current;
    }, 30);
}

// ===== JOBS =====
function renderJobs() {
    const container = $('jobs-container');
    const empty = $('no-jobs-msg');
    if (!allJobs.length) { container.innerHTML = ''; empty.classList.remove('hidden'); return; }
    empty.classList.add('hidden');
    renderJobCards(allJobs);
}

function renderJobCards(jobs) {
    $('jobs-container').innerHTML = jobs.map((j, i) => `
        <div class="job-card ${i === 0 ? 'best-match' : ''}">
            <h3>${escHtml(j.title)}</h3>
            <div class="job-meta">
                <span><i class="fa-solid fa-building"></i> ${escHtml(j.company)}</span>
                <span><i class="fa-solid fa-location-dot"></i> ${escHtml(j.location)}</span>
                <span class="chip">${j.match_percentage}%</span>
            </div>
            <p class="job-desc">${escHtml(j.description || '')}</p>
            <div class="job-skills">${(j.key_skills||[]).map(s=>`<span class="tag">${escHtml(s)}</span>`).join('')}</div>
            <a href="${escHtml(j.apply_link)}" target="_blank" rel="noopener" class="job-apply"><i class="fa-solid fa-arrow-up-right-from-square"></i> Apply Now</a>
        </div>
    `).join('');
}

window.filterJobs = function() {
    const role = $('job-filter-role').value.toLowerCase();
    const loc = $('job-filter-location').value.toLowerCase();
    const filtered = allJobs.filter(j => {
        const matchRole = !role || j.title.toLowerCase().includes(role);
        const matchLoc = !loc || j.location.toLowerCase().includes(loc);
        return matchRole && matchLoc;
    });
    if (filtered.length === 0) {
        $('jobs-container').innerHTML = '<div class="empty-state"><i class="fa-solid fa-search"></i><h3>No Matches</h3><p>Try adjusting your filters.</p></div>';
    } else {
        renderJobCards(filtered);
    }
};

// ===== ROADMAP =====
function renderRoadmap() {
    const empty = $('roadmap-empty'), content = $('roadmap-content');
    if (!careerData || !careerData.roadmap) { empty.classList.remove('hidden'); content.style.display = 'none'; return; }
    empty.classList.add('hidden'); content.style.display = 'block';
    const rm = careerData.roadmap;
    $('roadmap-timeline').innerHTML = (rm.roadmap||[]).map((w, i) => `
        <div class="timeline-item">
            <h4>${escHtml(w.week)}: ${escHtml(w.focus)}</h4>
            <ul>${(w.tasks||[]).map(t=>`<li>${escHtml(t)}</li>`).join('')}</ul>
        </div>
    `).join('');
    fillList('projects-list', rm.projects_to_build);
    fillList('courses-list', rm.courses_to_take);
}

// ===== SKILL GAP =====
function setupSkillGap() {
    $('sg-analyze-btn').addEventListener('click', analyzeSkillGap);
}

async function analyzeSkillGap() {
    const role = $('sg-target-role').value.trim();
    if (!role) return showToast('Enter a target role to analyze.', 'error');
    $('sg-loading').classList.remove('hidden');
    $('sg-results').classList.add('hidden');
    $('sg-empty').classList.add('hidden');
    $('sg-analyze-btn').disabled = true;
    $('sg-analyze-btn').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
    try {
        const skills = analysisData ? analysisData.skills : [];
        const res = await fetch('/api/skill_gap', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ target_role: role, current_skills: skills, resume_text: fullResumeText || resumeText, mock_mode: mockMode })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        renderSkillGap(data);
        showToast('Skill gap analysis complete!', 'success');
    } catch(e) { showToast(e.message, 'error'); $('sg-empty').classList.remove('hidden'); }
    finally { 
        $('sg-loading').classList.add('hidden'); 
        $('sg-analyze-btn').disabled = false;
        $('sg-analyze-btn').innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Analyze Gap';
    }
}

function renderSkillGap(d) {
    $('sg-results').classList.remove('hidden');
    $('sg-role-title').textContent = (d.target_role || 'Role') + ' Match';
    animateScore('sg-circle', d.match_percentage || 0, 100);
    animateCount('sg-match-val', d.match_percentage || 0);
    $('sg-matched').innerHTML = (d.matched_skills||[]).map(s=>`<span class="tag">${escHtml(s)}</span>`).join('') || '<span class="text-block muted">None detected — upload a resume first</span>';
    $('sg-missing').innerHTML = (d.missing_skills||[]).map(s=>`<span class="tag">${escHtml(s)}</span>`).join('') || '<span class="text-block muted">Great — no gaps found!</span>';
    $('sg-recommendations').innerHTML = (d.recommendations||[]).map(r => `
        <div class="reco-item">
            <span class="reco-skill">${escHtml(r.skill)}</span>
            <span class="chip ${r.priority==='High'?'chip-red':r.priority==='Medium'?'chip-yellow':'chip-green'}">${r.priority}</span>
            <span class="reco-resource">${escHtml(r.resource)}</span>
        </div>
    `).join('');
}

// ===== MOCK INTERVIEW =====
function setupInterview() {
    $('start-interview-btn').addEventListener('click', startInterview);
    $('submit-answer-btn').addEventListener('click', submitAnswer);
    $('skip-btn').addEventListener('click', nextQuestion);
    $('next-q-btn').addEventListener('click', () => { $('feedback-card').classList.add('hidden'); nextQuestion(); });
}

async function startInterview() {
    const role = $('interview-role').value;
    $('interview-loading').classList.remove('hidden');
    $('interview-setup').classList.add('hidden');
    try {
        const res = await fetch('/api/interview/questions', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ role, mock_mode: mockMode })
        });
        const data = await res.json();
        interviewQuestions = data.questions || [];
        currentQIndex = 0; scores = [];
        if (!interviewQuestions.length) throw new Error('No questions generated. Try again.');
        $('interview-session').classList.remove('hidden');
        showQuestion();
        showToast(`Interview started for ${role}!`, 'success');
    } catch(e) { showToast(e.message, 'error'); $('interview-setup').classList.remove('hidden'); }
    finally { $('interview-loading').classList.add('hidden'); }
}

function showQuestion() {
    if (currentQIndex >= interviewQuestions.length) { finishInterview(); return; }
    const q = interviewQuestions[currentQIndex];
    $('q-counter').textContent = `Question ${currentQIndex+1} of ${interviewQuestions.length}`;
    $('interview-progress-fill').style.width = ((currentQIndex+1)/interviewQuestions.length*100)+'%';
    $('q-text').textContent = q.question;
    $('q-category').textContent = q.category || 'General';
    $('q-difficulty').textContent = q.difficulty || 'Medium';
    $('q-difficulty').className = 'chip ' + (q.difficulty==='Hard'?'chip-red':q.difficulty==='Easy'?'chip-green':'chip-yellow');
    $('answer-input').value = '';
    $('answer-input').focus();
    $('feedback-card').classList.add('hidden');
    $('interview-complete').classList.add('hidden');
    $('submit-answer-btn').disabled = false;
    $('submit-answer-btn').innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Answer';
}

async function submitAnswer() {
    const answer = $('answer-input').value.trim();
    if (!answer) return showToast('Please type your answer before submitting.', 'error');
    $('answer-loading').classList.remove('hidden');
    $('submit-answer-btn').disabled = true;
    $('submit-answer-btn').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evaluating...';
    try {
        const q = interviewQuestions[currentQIndex];
        const res = await fetch('/api/interview/evaluate', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ question: q.question, answer, role: $('interview-role').value, mock_mode: mockMode })
        });
        const fb = await res.json();
        if (!res.ok) throw new Error(fb.error || 'Evaluation failed');
        scores.push(fb.score || 0);
        renderFeedback(fb);
    } catch(e) { showToast(e.message, 'error'); }
    finally { 
        $('answer-loading').classList.add('hidden'); 
        $('submit-answer-btn').disabled = false;
        $('submit-answer-btn').innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Answer';
    }
}

function renderFeedback(fb) {
    $('feedback-card').classList.remove('hidden');
    animateScore('fb-circle', fb.score || 0, 10);
    animateCount('fb-score', fb.score || 0);
    $('fb-text').textContent = fb.feedback || '';
    fillList('fb-strengths', fb.strengths);
    fillList('fb-improvements', fb.improvements);
    $('fb-sample').textContent = fb.sample_answer || '';
    $('feedback-card').scrollIntoView({behavior:'smooth'});
}

function nextQuestion() {
    currentQIndex++;
    if (currentQIndex >= interviewQuestions.length) { finishInterview(); return; }
    showQuestion();
    window.scrollTo({ top: $('interview-session').offsetTop - 80, behavior: 'smooth' });
}

function finishInterview() {
    $('interview-session').classList.add('hidden');
    $('interview-complete').classList.remove('hidden');
    const avg = scores.length ? (scores.reduce((a,b)=>a+b,0)/scores.length).toFixed(1) : 0;
    $('avg-score').textContent = avg;
    showToast(`Interview complete! Average score: ${avg}/10`, 'success');
}

window.resetInterview = function() {
    $('interview-complete').classList.add('hidden');
    $('interview-session').classList.add('hidden');
    $('interview-setup').classList.remove('hidden');
    interviewQuestions = []; currentQIndex = 0; scores = [];
};

// ===== TABS =====
function setupTabs() {
    document.querySelectorAll('.tab').forEach(btn => {
        btn.addEventListener('click', () => {
            const bar = btn.closest('.tab-bar');
            const panels = bar.nextElementSibling;
            bar.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            panels.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            const panel = $(btn.dataset.tab);
            if (panel) panel.classList.add('active');
        });
    });
}

// ===== AUTH =====
function setupAuth() {
    $('auth-btn').addEventListener('click', () => $('auth-modal').classList.remove('hidden'));
    $('close-auth').addEventListener('click', () => $('auth-modal').classList.add('hidden'));
    // Close modal on overlay click
    $('auth-modal').addEventListener('click', (e) => {
        if (e.target === $('auth-modal')) $('auth-modal').classList.add('hidden');
    });
    $('auth-toggle-link').addEventListener('click', e => {
        e.preventDefault();
        isLoginMode = !isLoginMode;
        $('auth-title').textContent = isLoginMode ? 'Welcome Back' : 'Create Account';
        $('auth-subtitle').textContent = isLoginMode ? 'Sign in to save your progress' : 'Join to track your career growth';
        $('auth-submit-btn').textContent = isLoginMode ? 'Sign In' : 'Create Account';
        $('auth-toggle-msg').textContent = isLoginMode ? "Don't have an account?" : 'Already have an account?';
        $('auth-toggle-link').textContent = isLoginMode ? 'Create one' : 'Sign in';
    });
    $('auth-submit-btn').addEventListener('click', handleAuth);
    $('logout-btn').addEventListener('click', handleLogout);
    // Enter key support
    $('auth-password').addEventListener('keydown', e => { if (e.key === 'Enter') handleAuth(); });
}

async function handleAuth() {
    const email = $('auth-email').value, password = $('auth-password').value;
    if (!email || !password) return showToast('Please fill in all fields.', 'error');
    $('auth-submit-btn').disabled = true;
    $('auth-submit-btn').textContent = 'Please wait...';
    try {
        const res = await fetch(isLoginMode ? '/api/login' : '/api/signup', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({email, password})
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        $('auth-modal').classList.add('hidden');
        $('auth-email').value = '';
        $('auth-password').value = '';
        await checkAuthStatus();
        showToast(isLoginMode ? 'Signed in successfully!' : 'Account created!', 'success');
    } catch(e) { showToast(e.message, 'error'); }
    finally {
        $('auth-submit-btn').disabled = false;
        $('auth-submit-btn').textContent = isLoginMode ? 'Sign In' : 'Create Account';
    }
}

async function handleLogout() {
    try { await fetch('/api/logout', {method:'POST'}); } catch(e) {}
    isAuthenticated = false;
    updateAuthUI();
    showToast('Logged out successfully.', 'success');
}

async function checkAuthStatus() {
    try {
        const res = await fetch('/api/user');
        const data = await res.json();
        isAuthenticated = data.authenticated;
        userEmail = data.email || '';
    } catch(e) { isAuthenticated = false; }
    updateAuthUI();
}

function updateAuthUI() {
    if (isAuthenticated) {
        $('auth-btn').classList.add('hidden');
        $('logout-btn').classList.remove('hidden');
        $('user-email-display').textContent = userEmail;
        $('user-email-display').classList.remove('hidden');
    } else {
        $('auth-btn').classList.remove('hidden');
        $('logout-btn').classList.add('hidden');
        $('user-email-display').classList.add('hidden');
    }
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'info') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 4000);
}

// ===== UTILS =====
function escHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

window.copyText = function(id) {
    const text = $(id).innerText;
    navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard!', 'success'));
};

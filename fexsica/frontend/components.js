/**
 * UI Components Module
 */

/**
 * Show loading overlay
 */
function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.textContent = text;
    overlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'none';
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    const icon = document.createElement('i');
    icon.className = iconMap[type] || iconMap.info;
    
    const text = document.createElement('span');
    text.textContent = message;
    
    toast.appendChild(icon);
    toast.appendChild(text);
    container.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard', 'success');
    }).catch(err => {
        showToast('Failed to copy', 'error');
    });
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format confidence percentage
 */
function formatConfidence(confidence) {
    return `${Math.round(confidence * 100)}%`;
}

/**
 * Create verdict badge HTML
 */
function createVerdictBadge(verdict) {
    const badges = {
        authentic: '<span class="verdict-badge authentic">✓ Authentic</span>',
        manipulated: '<span class="verdict-badge manipulated">✗ Manipulated</span>',
        inconclusive: '<span class="verdict-badge inconclusive">? Inconclusive</span>',
        error: '<span class="verdict-badge error">✗ Error</span>'
    };
    return badges[verdict] || badges.inconclusive;
}

/**
 * Create verdict icon
 */
function getVerdictIcon(verdict) {
    const icons = {
        authentic: 'fas fa-check-circle',
        manipulated: 'fas fa-times-circle',
        inconclusive: 'fas fa-question-circle',
        error: 'fas fa-exclamation-circle'
    };
    return icons[verdict] || icons.inconclusive;
}

/**
 * Render engine progress
 */
function renderEngineProgress(engines) {
    const engineList = document.getElementById('engineList');
    engineList.innerHTML = '';
    
    const engineNames = [
        'ELA', 'Metadata', 'Noise', 'Illumination',
        'Geometry', 'Deepfake', 'AI-Gen'
    ];
    
    engineNames.forEach((name, index) => {
        const engine = engines[name] || { status: 'pending' };
        
        const item = document.createElement('div');
        item.className = 'engine-item';
        item.id = `engine-${name}`;
        
        const status = document.createElement('div');
        status.className = `engine-status ${engine.status}`;
        
        const nameElem = document.createElement('div');
        nameElem.className = 'engine-name';
        nameElem.textContent = name;
        
        const result = document.createElement('div');
        result.className = 'engine-result';
        result.textContent = engine.status === 'complete' ? engine.verdict : 'Analyzing...';
        
        item.appendChild(status);
        item.appendChild(nameElem);
        item.appendChild(result);
        engineList.appendChild(item);
    });
}

/**
 * Update engine status
 */
function updateEngineStatus(engineName, status, result = null) {
    const engineItem = document.getElementById(`engine-${engineName}`);
    if (!engineItem) return;
    
    const statusElem = engineItem.querySelector('.engine-status');
    const resultElem = engineItem.querySelector('.engine-result');
    
    statusElem.className = `engine-status ${status}`;
    if (result) {
        resultElem.textContent = result;
    }
}

/**
 * Render analysis results
 */
function renderResults(data) {
    // Render verdict
    renderVerdict(data);
    
    // Render summary
    renderSummary(data);
    
    // Render Bayesian analysis
    renderBayesianAnalysis(data);
    
    // Render engine results table
    renderEnginesTable(data.engine_results);
    
    // Render chain of custody
    renderChainOfCustody(data);
    
    // Enable report download if available
    if (data.report_path) {
        const btn = document.getElementById('downloadReportBtn');
        btn.style.display = 'inline-flex';
        btn.onclick = () => {
            showLoading('Downloading report...');
            api.downloadReport(data.analysis_id)
                .then(() => {
                    hideLoading();
                    showToast('Report downloaded successfully', 'success');
                })
                .catch(error => {
                    hideLoading();
                    showToast(error.message, 'error');
                });
        };
    }
}

/**
 * Render verdict box
 */
function renderVerdict(data) {
    const container = document.getElementById('verdictContainer');
    const verdict = data.verdict;
    const confidence = data.confidence;
    
    const icon = getVerdictIcon(verdict);
    const title = verdict.charAt(0).toUpperCase() + verdict.slice(1);
    
    let verdictClass = `verdict-${verdict}`;
    
    container.innerHTML = `
        <div class="verdict-box ${verdictClass}">
            <div class="verdict-icon">
                <i class="${icon}"></i>
            </div>
            <h2 class="verdict-title">${title}</h2>
            <div class="confidence-meter">
                <p><strong>Confidence: ${formatConfidence(confidence)}</strong></p>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidence * 100}%"></div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render summary
 */
function renderSummary(data) {
    const container = document.getElementById('summaryBox');
    const summary = data.summary || 'No summary available.';
    
    container.innerHTML = `
        <div class="summary-box">
            <h3><i class="fas fa-file-alt"></i> Summary</h3>
            <p class="summary-text">${summary}</p>
        </div>
    `;
}

/**
 * Render Bayesian analysis
 */
function renderBayesianAnalysis(data) {
    const container = document.getElementById('bayesianContent');
    const bayesian = data.bayesian_data;
    
    const manipProb = Math.round(bayesian.posterior_manipulated * 100);
    const authProb = Math.round(bayesian.posterior_authentic * 100);
    
    container.innerHTML = `
        <div class="bayesian-content">
            <div class="bayes-item">
                <div class="bayes-label">Probability of Manipulation</div>
                <div class="bayes-value">${manipProb}%</div>
            </div>
            <div class="bayes-item">
                <div class="bayes-label">Probability of Authenticity</div>
                <div class="bayes-value">${authProb}%</div>
            </div>
        </div>
    `;
}

/**
 * Render engines results table
 */
function renderEnginesTable(engines) {
    const tbody = document.getElementById('enginesTableBody');
    tbody.innerHTML = '';
    
    engines.forEach(engine => {
        if (engine.engine === 'Bayesian Fusion') return; // Skip fusion in table
        
        const row = document.createElement('tr');
        
        const engineCell = document.createElement('td');
        engineCell.textContent = engine.engine;
        
        const verdictCell = document.createElement('td');
        verdictCell.innerHTML = createVerdictBadge(engine.verdict);
        
        const confidenceCell = document.createElement('td');
        confidenceCell.innerHTML = `<span class="confidence-text">${formatConfidence(engine.confidence)}</span>`;
        
        const findingCell = document.createElement('td');
        const finding = engine.findings && engine.findings[0] ? engine.findings[0] : 'No findings';
        findingCell.textContent = finding.length > 50 ? finding.substring(0, 47) + '...' : finding;
        findingCell.title = finding;
        
        row.appendChild(engineCell);
        row.appendChild(verdictCell);
        row.appendChild(confidenceCell);
        row.appendChild(findingCell);
        tbody.appendChild(row);
    });
}

/**
 * Render chain of custody
 */
function renderChainOfCustody(data) {
    document.getElementById('analysisId').textContent = data.analysis_id;
    document.getElementById('imageHash').textContent = data.image_hash;
    
    if (data.report_hash) {
        document.getElementById('reportHashItem').style.display = 'block';
        document.getElementById('reportHash').textContent = data.report_hash;
    }
}

/**
 * Render history
 */
function renderHistory(analyses) {
    const container = document.getElementById('historyList');
    
    if (analyses.length === 0) {
        container.innerHTML = '<p class="empty-state">No analyses yet. Start by uploading an image.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    analyses.forEach(analysis => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.onclick = () => navigateTo('upload');
        
        const info = document.createElement('div');
        info.className = 'history-info';
        
        const caseElem = document.createElement('div');
        caseElem.className = 'history-case';
        caseElem.textContent = analysis.case_number;
        
        const timeElem = document.createElement('div');
        timeElem.className = 'history-time';
        const date = new Date(analysis.timestamp).toLocaleString();
        timeElem.textContent = date;
        
        info.appendChild(caseElem);
        info.appendChild(timeElem);
        
        const result = document.createElement('div');
        result.className = 'history-result';
        result.innerHTML = createVerdictBadge(analysis.verdict);
        
        item.appendChild(info);
        item.appendChild(result);
        container.appendChild(item);
    });
}

/**
 * Format truncated hash for display
 */
function truncateHash(hash, chars = 16) {
    if (hash.length <= chars) return hash;
    return hash.substring(0, chars) + '...' + hash.substring(hash.length - 8);
}

/**
 * Create engine mock data for testing
 */
function createMockAnalysisData() {
    return {
        status: 'success',
        case_number: '2024-001234',
        analysis_id: 'FX-2024-0001',
        image_hash: 'abc123def456789abc123def456789abc123def456789abc123def456789abc123',
        report_hash: 'xyz789abc123def456xyz789abc123def456xyz789abc123def456xyz789abc123',
        timestamp: new Date().toISOString(),
        verdict: 'manipulated',
        confidence: 0.82,
        summary: 'Forensic analysis indicates 82% probability of manipulation. Multiple forensic engines detected compression inconsistencies and metadata anomalies.',
        engine_results: [
            {
                engine: 'ELA',
                verdict: 'manipulated',
                confidence: 0.85,
                findings: ['Detected 15.2% anomalous JPEG blocks', 'Compression history inconsistency detected']
            },
            {
                engine: 'Metadata',
                verdict: 'inconclusive',
                confidence: 0.60,
                findings: ['32 EXIF fields detected', 'Timestamp consistent']
            },
            {
                engine: 'Noise',
                verdict: 'authentic',
                confidence: 0.70,
                findings: ['Uniform noise distribution', 'PRNU signature consistent']
            },
            {
                engine: 'Illumination',
                verdict: 'manipulated',
                confidence: 0.80,
                findings: ['Multiple light sources detected', 'Shadow angle inconsistency']
            },
            {
                engine: 'Geometry',
                verdict: 'authentic',
                confidence: 0.75,
                findings: ['Perspective consistent', 'Single vanishing point']
            },
            {
                engine: 'Deepfake',
                verdict: 'authentic',
                confidence: 0.95,
                findings: ['No deepfake artifacts detected']
            },
            {
                engine: 'AI-Gen',
                verdict: 'authentic',
                confidence: 0.70,
                findings: ['Frequency spectrum consistent with natural image']
            }
        ],
        bayesian_data: {
            posterior_manipulated: 0.82,
            posterior_authentic: 0.18
        },
        report_path: '/tmp/fexsics/evidence/report_FX-2024-0001.pdf'
    };
}

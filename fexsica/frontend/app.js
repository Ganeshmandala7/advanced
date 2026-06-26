/**
 * FEXsics Frontend Application
 * Main application logic and event handling
 */

let currentFile = null;
let currentAnalysis = null;
let analysisHistory = JSON.parse(localStorage.getItem('fexsicsHistory')) || [];

// ========================================
// Initialization
// ========================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('FEXsics Frontend initialized');
    
    // Check backend health
    const isHealthy = await api.checkHealth();
    if (!isHealthy) {
        showToast('Warning: Backend server may be unavailable. Using demo mode.', 'warning');
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial section
    navigateTo('upload');
});

// ========================================
// Event Listeners Setup
// ========================================

function setupEventListeners() {
    // Upload area
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    
    uploadArea.addEventListener('click', () => imageInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    imageInput.addEventListener('change', handleImageSelect);
    
    // Clear image button
    document.getElementById('clearImageBtn').addEventListener('click', clearImage);
    
    // Case form
    document.getElementById('caseForm').addEventListener('submit', handleFormSubmit);
}

// ========================================
// File Upload Handling
// ========================================

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageSelect({ target: { files: files } });
    }
}

function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file
    const validFormats = ['image/jpeg', 'image/png', 'image/tiff', 'image/webp', 'image/bmp'];
    if (!validFormats.includes(file.type)) {
        showToast('Invalid image format. Please use JPEG, PNG, TIFF, WebP, or BMP.', 'error');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        showToast('File size exceeds 50MB limit.', 'error');
        return;
    }
    
    currentFile = file;
    displayImagePreview(file);
}

function displayImagePreview(file) {
    const previewSection = document.getElementById('previewSection');
    const previewImg = document.getElementById('previewImg');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    document.getElementById('uploadArea').style.display = 'none';
    previewSection.style.display = 'flex';
}

function clearImage() {
    currentFile = null;
    document.getElementById('imageInput').value = '';
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
}

// ========================================
// Form Submission
// ========================================

async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (!currentFile) {
        showToast('Please select an image first.', 'error');
        return;
    }
    
    const caseNumber = document.getElementById('caseNumber').value;
    const caseName = document.getElementById('caseName').value;
    const investigator = document.getElementById('investigator').value;
    const includeReport = document.getElementById('includeReport').checked;
    
    if (!caseNumber || !caseName) {
        showToast('Please fill in all required fields.', 'error');
        return;
    }
    
    // Show progress
    navigateTo('progress');
    
    // Update progress display
    document.getElementById('progressCaseNumber').textContent = caseNumber;
    document.getElementById('progressCaseName').textContent = caseName;
    
    // Initialize engine progress
    renderEngineProgress({});
    
    // Start analysis
    try {
        showLoading('Validating image...');
        
        // Validate image
        const validation = await api.validateImage(currentFile);
        if (!validation.ok) {
            hideLoading();
            showToast(validation.message, 'error');
            navigateTo('upload');
            return;
        }
        
        showLoading('Starting forensic analysis...');
        
        // Submit for analysis
        const result = await api.analyzeImage(currentFile, {
            caseNumber,
            caseName,
            investigator,
            includeReport
        });
        
        hideLoading();
        
        // Store in history
        analysisHistory.unshift({
            case_number: caseNumber,
            case_name: caseName,
            verdict: result.verdict,
            timestamp: new Date().toISOString(),
            analysis_id: result.analysis_id
        });
        localStorage.setItem('fexsicsHistory', JSON.stringify(analysisHistory));
        
        // Display results
        currentAnalysis = result;
        navigateTo('results');
        renderResults(result);
        
        showToast('Analysis complete!', 'success');
        
    } catch (error) {
        hideLoading();
        showToast(`Analysis failed: ${error.message}`, 'error');
        navigateTo('upload');
        console.error('Analysis error:', error);
    }
}

// ========================================
// Navigation
// ========================================

function navigateTo(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Load section-specific content
    if (sectionName === 'history') {
        renderHistory(analysisHistory);
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// ========================================
// Progress Simulation (for demo)
// ========================================

function simulateProgress() {
    const engines = ['ELA', 'Metadata', 'Noise', 'Illumination', 'Geometry', 'Deepfake', 'AI-Gen'];
    let currentEngine = 0;
    
    const progressInterval = setInterval(() => {
        if (currentEngine < engines.length) {
            updateEngineStatus(engines[currentEngine], 'running');
            
            setTimeout(() => {
                updateEngineStatus(engines[currentEngine], 'complete', 'authentic');
                currentEngine++;
            }, 2000);
        } else {
            clearInterval(progressInterval);
        }
    }, 2500);
}

// ========================================
// Utility Functions
// ========================================

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// ========================================
// Demo Mode
// ========================================

/**
 * Demo analysis with simulated results
 */
async function demoAnalysis(caseNumber, caseName) {
    navigateTo('progress');
    
    document.getElementById('progressCaseNumber').textContent = caseNumber;
    document.getElementById('progressCaseName').textContent = caseName;
    
    // Simulate progress
    const engines = ['ELA', 'Metadata', 'Noise', 'Illumination', 'Geometry', 'Deepfake', 'AI-Gen'];
    let completedEngines = 0;
    
    const progressInterval = setInterval(() => {
        if (completedEngines < engines.length) {
            const engine = engines[completedEngines];
            updateEngineStatus(engine, 'running');
            
            setTimeout(() => {
                updateEngineStatus(engine, 'complete', 'authentic');
                completedEngines++;
                
                const progress = (completedEngines / engines.length) * 100;
                document.getElementById('overallProgress').style.width = progress + '%';
                document.getElementById('progressText').textContent = 
                    `Completed ${completedEngines}/${engines.length} engines...`;
            }, 1500 + Math.random() * 1500);
        } else {
            clearInterval(progressInterval);
            
            // Show results
            setTimeout(() => {
                const demoData = createMockAnalysisData();
                currentAnalysis = demoData;
                navigateTo('results');
                renderResults(demoData);
                
                showToast('Demo analysis complete!', 'success');
            }, 1000);
        }
    }, 2000);
}

// ========================================
// Testing & Demo
// ========================================

window.testDemo = async function() {
    // Quick demo - fills form and shows results
    document.getElementById('caseNumber').value = 'TEST-2024-001';
    document.getElementById('caseName').value = 'Test Case v. Defendant';
    document.getElementById('investigator').value = 'Test Investigator';
    
    await demoAnalysis('TEST-2024-001', 'Test Case v. Defendant');
};

// Make navigateTo available globally
window.navigateTo = navigateTo;
window.copyToClipboard = copyToClipboard;
window.showToast = showToast;
window.formatFileSize = formatFileSize;

console.log('✓ FEXsics Frontend ready');
console.log('Try: window.testDemo() for a quick demo');

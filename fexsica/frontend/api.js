/**
 * API Module - Communication with FEXsics Backend
 */

class FEXsicsAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.apiURL = `${baseURL}/api/v1`;
    }

    /**
     * Check API health
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiURL}/health`);
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    /**
     * Validate image before upload
     */
    async validateImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.apiURL}/validate-image`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            return {
                ok: response.ok,
                message: data.message || data.detail
            };
        } catch (error) {
            console.error('Validation error:', error);
            return {
                ok: false,
                message: error.message
            };
        }
    }

    /**
     * Submit image for forensic analysis
     */
    async analyzeImage(file, caseInfo) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('case_number', caseInfo.caseNumber);
        formData.append('case_name', caseInfo.caseName);
        formData.append('investigator', caseInfo.investigator || 'FEXsics System');
        formData.append('include_report', caseInfo.includeReport !== false);

        try {
            const response = await fetch(`${this.apiURL}/analyze`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Analysis failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Analysis error:', error);
            throw error;
        }
    }

    /**
     * Download PDF report
     */
    async downloadReport(analysisId) {
        try {
            const response = await fetch(`${this.apiURL}/report/${analysisId}`);

            if (!response.ok) {
                throw new Error('Failed to download report');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `forensic_report_${analysisId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download error:', error);
            throw error;
        }
    }

    /**
     * Get analysis status
     */
    async getStatus(analysisId) {
        try {
            const response = await fetch(`${this.apiURL}/status/${analysisId}`);
            return await response.json();
        } catch (error) {
            console.error('Status check error:', error);
            return null;
        }
    }

    /**
     * Stream analysis results (polling)
     */
    async streamAnalysis(analysisId, onUpdate, onComplete, onError) {
        const pollInterval = 2000; // Poll every 2 seconds
        let pollCount = 0;
        const maxPolls = 300; // 10 minutes max

        const poll = async () => {
            try {
                const status = await this.getStatus(analysisId);
                
                if (status && status.status === 'complete') {
                    onComplete(status);
                    return;
                }

                pollCount++;
                if (pollCount < maxPolls) {
                    onUpdate(status);
                    setTimeout(poll, pollInterval);
                } else {
                    onError(new Error('Analysis timeout'));
                }
            } catch (error) {
                onError(error);
            }
        };

        poll();
    }

    /**
     * Get evidence map image
     */
    async getEvidence(evidenceId) {
        try {
            const response = await fetch(`${this.apiURL}/evidence/${evidenceId}`);
            if (!response.ok) {
                throw new Error('Evidence not found');
            }
            return await response.blob();
        } catch (error) {
            console.error('Evidence retrieval error:', error);
            return null;
        }
    }
}

// Global API instance
const api = new FEXsicsAPI();

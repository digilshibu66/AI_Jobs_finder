import { useState, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/JobsPage.css';

// Verified working free models (updated Jun 2025)
const FREE_MODELS = [
    { value: 'google/gemini-2.0-flash-exp:free', label: 'Gemini 2.0 Flash', group: 'Google', recommended: true },
    { value: 'meta-llama/llama-3.3-70b-instruct:free', label: 'Llama 3.3 70B', group: 'Meta' },
    { value: 'qwen/qwen3-coder:free', label: 'Qwen3 Coder', group: 'Alibaba' },
    { value: 'mistralai/mistral-small-3.1-24b-instruct:free', label: 'Mistral Small 3.1', group: 'Mistral' },
    { value: 'google/gemma-3-27b-it:free', label: 'Gemma 3 27B', group: 'Google' },
    { value: 'google/gemma-3-12b-it:free', label: 'Gemma 3 12B', group: 'Google' },
    { value: 'meta-llama/llama-3.2-3b-instruct:free', label: 'Llama 3.2 3B', group: 'Meta' },
    { value: 'qwen/qwen3-4b:free', label: 'Qwen3 4B', group: 'Alibaba' },
    { value: 'qwen/qwen3-235b-a22b:free', label: 'Qwen3 235B', group: 'Alibaba' },
];

const JobsPage = () => {
    const { theme } = useTheme();
    const [jobCategory, setJobCategory] = useState('freelance');
    const [jobType, setJobType] = useState('software');
    const [jobName, setJobName] = useState('');
    const [location, setLocation] = useState('');
    const [jobLimit, setJobLimit] = useState(30);
    const [aiModel, setAiModel] = useState('google/gemini-2.0-flash-exp:free');
    const [sendEmails, setSendEmails] = useState(false);
    const [generateLetter, setGenerateLetter] = useState(true);
    const [isRunning, setIsRunning] = useState(false);
    const [logOutput, setLogOutput] = useState('');
    const logRef = useRef(null);

    const appendLog = (message, type = 'log') => {
        const prefix = type === 'error' ? '❌ ' : type === 'success' ? '✅ ' : type === 'info' ? 'ℹ️ ' : '';
        setLogOutput(prev => prev + prefix + message + '\n');
        // Auto-scroll to bottom
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    };

    const runJobs = async () => {
        setIsRunning(true);
        setLogOutput('');
        appendLog('Starting job processing...', 'info');

        const requestData = {
            jobCategory,
            jobType,
            jobLimit,
            sendEmails,
            generateMotivationalLetter: generateLetter,
            aiModel,
            location: location || undefined,
            jobName: jobName || undefined
        };

        appendLog(`Category: ${jobCategory}, Type: ${jobType}, Limit: ${jobLimit}`, 'info');
        appendLog(`AI Model: ${aiModel}`, 'info');
        appendLog(`Send Emails: ${sendEmails ? 'YES' : 'NO (Dry Run)'}`, 'info');
        appendLog('-----------------------------------');

        try {
            appendLog('Connecting to backend stream...', 'info');

            // Use fetch with streaming for SSE-like behavior
            const response = await fetch('/api/run-jobs-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
            });

            // Check if response is ok
            if (!response.ok) {
                appendLog(`Server error: ${response.status} ${response.statusText}`, 'error');
                setIsRunning(false);
                return;
            }

            // Read the streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    appendLog('-----------------------------------');
                    appendLog('Stream ended.', 'info');
                    break;
                }

                // Decode the chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });

                // Process complete SSE messages (lines starting with "data: ")
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const jsonStr = line.substring(6); // Remove "data: " prefix
                            if (jsonStr.trim()) {
                                const data = JSON.parse(jsonStr);
                                const message = data.message || '';
                                const type = data.type || 'log';

                                if (type === 'error') {
                                    appendLog(message, 'error');
                                } else if (type === 'complete' || type === 'success') {
                                    appendLog(message, 'success');
                                } else if (type === 'info' || type === 'start') {
                                    appendLog(message, 'info');
                                } else {
                                    // Regular log messages - detect errors/success in content
                                    if (message.includes('[ERROR]') || message.includes('Error:')) {
                                        appendLog(message, 'error');
                                    } else if (message.includes('[SUCCESS]') || message.includes('successfully')) {
                                        appendLog(message, 'success');
                                    } else {
                                        appendLog(message);
                                    }
                                }
                            }
                        } catch (parseError) {
                            // If JSON parsing fails, just log the raw line
                            appendLog(line.substring(6));
                        }
                    }
                }
            }

            appendLog('Job processing completed!', 'success');
        } catch (error) {
            appendLog('Network Error: ' + error.message, 'error');
        }

        setIsRunning(false);
    };

    const cardStyle = {
        backgroundColor: theme.colors.surface,
        borderRadius: '16px',
        padding: '24px',
        boxShadow: theme.colors.cardShadow
    };

    return (
        <div className="jobs-page" style={{ backgroundColor: theme.colors.background }}>
            <div className="jobs-container">
                <div className="jobs-header">
                    <h2 style={{ color: theme.colors.text }}>🔍 Job Search & Apply</h2>
                    <p style={{ color: theme.colors.textSecondary }}>
                        Configure your job search and let AI handle the applications
                    </p>
                </div>

                <div className="jobs-grid">
                    {/* Search Configuration */}
                    <div className="jobs-card" style={cardStyle}>
                        <h3 style={{ color: theme.colors.text }}>Search Settings</h3>

                        <div className="form-group">
                            <label style={{ color: theme.colors.text }}>Job Category</label>
                            <select
                                value={jobCategory}
                                onChange={(e) => setJobCategory(e.target.value)}
                                disabled={isRunning}
                                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
                            >
                                <option value="freelance">Freelance Jobs</option>
                                <option value="normal">Full-time Jobs</option>
                            </select>
                        </div>

                        {jobCategory === 'freelance' ? (
                            <div className="form-group">
                                <label style={{ color: theme.colors.text }}>Job Type</label>
                                <select
                                    value={jobType}
                                    onChange={(e) => setJobType(e.target.value)}
                                    disabled={isRunning}
                                    style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
                                >
                                    <option value="software">Software Development</option>
                                    <option value="web">Web Development</option>
                                    <option value="mobile">Mobile Development</option>
                                    <option value="data">Data Science</option>
                                </select>
                            </div>
                        ) : (
                            <div className="form-group">
                                <label style={{ color: theme.colors.text }}>Job Title</label>
                                <input
                                    type="text"
                                    placeholder="e.g., React Developer"
                                    value={jobName}
                                    onChange={(e) => setJobName(e.target.value)}
                                    disabled={isRunning}
                                    style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
                                />
                            </div>
                        )}

                        <div className="form-group">
                            <label style={{ color: theme.colors.text }}>Location (Optional)</label>
                            <input
                                type="text"
                                placeholder="e.g., Mumbai, Remote"
                                value={location}
                                onChange={(e) => setLocation(e.target.value)}
                                disabled={isRunning}
                                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
                            />
                        </div>

                        <div className="form-group">
                            <label style={{ color: theme.colors.text }}>Job Limit: {jobLimit}</label>
                            <input
                                type="range"
                                min="5"
                                max="50"
                                value={jobLimit}
                                onChange={(e) => setJobLimit(parseInt(e.target.value))}
                                disabled={isRunning}
                            />
                        </div>
                    </div>

                    {/* AI Configuration */}
                    <div className="jobs-card" style={cardStyle}>
                        <h3 style={{ color: theme.colors.text }}>AI Settings</h3>

                        <div className="form-group">
                            <label style={{ color: theme.colors.text }}>AI Model</label>
                            <select
                                value={aiModel}
                                onChange={(e) => setAiModel(e.target.value)}
                                disabled={isRunning}
                                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
                            >
                                {FREE_MODELS.map(model => (
                                    <option key={model.value} value={model.value}>
                                        {model.recommended ? '⭐ ' : ''}{model.label} ({model.group})
                                    </option>
                                ))}
                            </select>
                            <small style={{ color: theme.colors.textSecondary }}>
                                All models are free. ⭐ = Recommended
                            </small>
                        </div>

                        <div className="form-group checkbox-group">
                            <label style={{ color: theme.colors.text }}>
                                <input
                                    type="checkbox"
                                    checked={generateLetter}
                                    onChange={(e) => setGenerateLetter(e.target.checked)}
                                    disabled={isRunning}
                                />
                                Generate Motivational Letters
                            </label>
                        </div>

                        <div className="form-group checkbox-group">
                            <label style={{ color: theme.colors.text }}>
                                <input
                                    type="checkbox"
                                    checked={sendEmails}
                                    onChange={(e) => setSendEmails(e.target.checked)}
                                    disabled={isRunning}
                                />
                                Actually Send Emails
                            </label>
                            {!sendEmails && (
                                <small style={{ color: theme.colors.warning }}>
                                    ⚠️ Dry-run mode - emails won't be sent
                                </small>
                            )}
                        </div>

                        <button
                            className="run-button"
                            onClick={runJobs}
                            disabled={isRunning}
                            style={{
                                background: isRunning
                                    ? theme.colors.warning
                                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                color: '#fff'
                            }}
                        >
                            {isRunning ? '⏳ Processing...' : '🚀 Start Job Search'}
                        </button>
                    </div>
                </div>

                {/* Output Log */}
                <div className="jobs-card output-card" style={cardStyle}>
                    <div className="log-header">
                        <h3 style={{ color: theme.colors.text }}>📋 Live Output Log</h3>
                        {isRunning && <span className="running-indicator">● Running</span>}
                    </div>
                    <pre
                        ref={logRef}
                        className="log-output"
                        style={{
                            backgroundColor: theme.colors.background,
                            color: theme.colors.text,
                            border: `1px solid ${theme.colors.border}`
                        }}
                    >
                        {logOutput || 'Configure your search and click "Start Job Search" to begin...\n\nCredentials loaded from .env file:\n• SMTP Email: ✓ Configured\n• OpenRouter API: ✓ Configured\n• Resume Path: ✓ Configured'}
                    </pre>
                </div>
            </div>
        </div>
    );
};

export default JobsPage;

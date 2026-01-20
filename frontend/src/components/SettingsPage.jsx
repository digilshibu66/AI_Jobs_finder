import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/SettingsPage.css';

// ACTUAL verified free models from OpenRouter API (Jan 2026)
const FREE_MODELS = [
    { value: 'meta-llama/llama-3.3-70b-instruct:free', label: 'Llama 3.3 70B', group: 'Meta', recommended: true, description: 'Large model, professional tone' },
    { value: 'qwen/qwen3-coder:free', label: 'Qwen3 Coder', group: 'Alibaba', description: 'Optimized for technical content' },
    { value: 'mistralai/devstral-2512:free', label: 'Devstral 2512', group: 'Mistral', description: 'Agentic coder model' },
    { value: 'nousresearch/hermes-3-llama-3.1-405b:free', label: 'Hermes 3 Llama 405B', group: 'NousResearch', description: 'Largest free model' },
    { value: 'meta-llama/llama-3.2-3b-instruct:free', label: 'Llama 3.2 3B', group: 'Meta', description: 'Lightweight and fast' },
    { value: 'openai/gpt-oss-120b:free', label: 'GPT OSS 120B', group: 'OpenAI', description: 'High reasoning capabilities' },
    { value: 'qwen/qwen3-4b:free', label: 'Qwen3 4B', group: 'Alibaba', description: 'Efficient small model' },
];

const SettingsPage = () => {
    const { theme } = useTheme();
    const [selectedModel, setSelectedModel] = useState('meta-llama/llama-3.3-70b-instruct:free');
    const [savedMessage, setSavedMessage] = useState('');

    const cardStyle = {
        backgroundColor: theme.colors.surface,
        borderRadius: '16px',
        padding: '24px',
        boxShadow: theme.colors.cardShadow
    };

    const handleSaveModel = () => {
        // In a real app, this would save to backend/localStorage
        localStorage.setItem('preferredModel', selectedModel);
        setSavedMessage('✅ Settings saved!');
        setTimeout(() => setSavedMessage(''), 3000);
    };

    useEffect(() => {
        const saved = localStorage.getItem('preferredModel');
        if (saved) setSelectedModel(saved);
    }, []);

    return (
        <div className="settings-page" style={{ backgroundColor: theme.colors.background }}>
            <div className="settings-container">
                <div className="settings-header">
                    <h2 style={{ color: theme.colors.text }}>⚙️ Settings</h2>
                    <p style={{ color: theme.colors.textSecondary }}>
                        Configure your AI models and preferences
                    </p>
                </div>

                <div className="settings-grid">
                    {/* AI Model Selection */}
                    <div className="settings-card" style={cardStyle}>
                        <h3 style={{ color: theme.colors.text }}>🤖 AI Model Selection</h3>
                        <p style={{ color: theme.colors.textSecondary, marginBottom: '1.5rem' }}>
                            Choose your preferred AI model for email and letter generation. All models are free.
                        </p>

                        <div className="models-list">
                            {FREE_MODELS.map(model => (
                                <div
                                    key={model.value}
                                    className={`model-option ${selectedModel === model.value ? 'selected' : ''}`}
                                    onClick={() => setSelectedModel(model.value)}
                                    style={{
                                        backgroundColor: selectedModel === model.value
                                            ? theme.colors.primary + '20'
                                            : theme.colors.background,
                                        borderColor: selectedModel === model.value
                                            ? theme.colors.primary
                                            : theme.colors.border
                                    }}
                                >
                                    <div className="model-header">
                                        <span className="model-name" style={{ color: theme.colors.text }}>
                                            {model.recommended && '⭐ '}{model.label}
                                        </span>
                                        <span className="model-group" style={{ color: theme.colors.textSecondary }}>
                                            {model.group}
                                        </span>
                                    </div>
                                    <p className="model-description" style={{ color: theme.colors.textSecondary }}>
                                        {model.description}
                                    </p>
                                    {selectedModel === model.value && (
                                        <span className="model-check">✓</span>
                                    )}
                                </div>
                            ))}
                        </div>

                        <button
                            className="save-button"
                            onClick={handleSaveModel}
                            style={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                color: '#fff'
                            }}
                        >
                            💾 Save Settings
                        </button>

                        {savedMessage && (
                            <p className="save-message" style={{ color: theme.colors.success }}>
                                {savedMessage}
                            </p>
                        )}
                    </div>

                    {/* Info Card */}
                    <div className="settings-card" style={cardStyle}>
                        <h3 style={{ color: theme.colors.text }}>ℹ️ About AI Models</h3>

                        <div className="info-section">
                            <h4 style={{ color: theme.colors.text }}>Free Models</h4>
                            <p style={{ color: theme.colors.textSecondary }}>
                                All models listed are completely free through OpenRouter. No API costs!
                            </p>
                        </div>

                        <div className="info-section">
                            <h4 style={{ color: theme.colors.text }}>Recommended: Gemini Flash</h4>
                            <p style={{ color: theme.colors.textSecondary }}>
                                Google's Gemini 2.0 Flash is the most reliable and fastest option for general use.
                            </p>
                        </div>

                        <div className="info-section">
                            <h4 style={{ color: theme.colors.text }}>For Technical Jobs</h4>
                            <p style={{ color: theme.colors.textSecondary }}>
                                Use Qwen3 Coder for software development positions - it understands technical context better.
                            </p>
                        </div>

                        <div className="info-section">
                            <h4 style={{ color: theme.colors.text }}>Rate Limits</h4>
                            <p style={{ color: theme.colors.textSecondary }}>
                                Free models have rate limits. If you hit them, the system will automatically wait and retry.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;

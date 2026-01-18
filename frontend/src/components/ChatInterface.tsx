import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { sendLogMonitoring } from '../services/api';

interface Message {
    text: string;
    sender: 'user' | 'bot';
}

const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            text: "Hello! I'm your Log Monitoring assistant. Ask me about system logs, anomalies, or potential issues!",
            sender: 'bot',
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | undefined>(undefined);
    const chatContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Scroll to bottom when messages change
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');

        // Add user message
        setMessages((prev) => [...prev, { text: userMessage, sender: 'user' }]);
        setLoading(true);

        try {
            // Call log monitoring endpoint
            const result = await sendLogMonitoring(userMessage, 'default_user', sessionId);

            // Add bot response
            setMessages((prev) => [
                ...prev,
                { text: result.response, sender: 'bot' }
            ]);

            // Save session ID for continuity
            if (result.session_id) {
                setSessionId(result.session_id);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages((prev) => [
                ...prev,
                { text: 'Sorry, I encountered an error while analyzing the logs. Please try again.', sender: 'bot' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="tab-content active">
            <div className="chat-container" ref={chatContainerRef}>
                {messages.map((message, index) => (
                    <div key={index} className={`chat-message ${message.sender}-message`}>
                        <div className="message-content">
                            {message.sender === 'bot' ? (
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {message.text}
                                </ReactMarkdown>
                            ) : (
                                <p>{message.text}</p>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <div className="input-container">
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about system logs, anomalies, or issues..."
                        disabled={loading}
                        autoComplete="off"
                    />
                    <button type="submit" disabled={loading}>
                        Send
                    </button>
                </form>
            </div>

            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                    <span>Thinking...</span>
                </div>
            )}
        </div>
    );
};

export default ChatInterface;

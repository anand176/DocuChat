import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';

interface Message {
    text: string;
    sender: 'user' | 'bot';
}

const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            text: "Hello! I'm DocuChat, your document knowledge assistant. Upload your documents and ask me anything about them!",
            sender: 'bot',
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [chatHistory, setChatHistory] = useState<string[][]>([]);
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
            const response = await sendChatMessage(userMessage, chatHistory);

            // Add bot response
            setMessages((prev) => [...prev, { text: response.response, sender: 'bot' }]);

            // Update chat history
            setChatHistory((prev) => [...prev, [userMessage, response.response]]);
        } catch (error) {
            console.error('Error:', error);
            setMessages((prev) => [
                ...prev,
                { text: 'Sorry, I encountered an error. Please try again.', sender: 'bot' },
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
                            <p>{message.text}</p>
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
                        placeholder="Type your question about your documents..."
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

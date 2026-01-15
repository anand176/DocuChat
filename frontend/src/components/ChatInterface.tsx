import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { streamChatMessage } from '../services/api';

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
            // Initial empty bot message for streaming
            setMessages((prev) => [...prev, { text: '', sender: 'bot' }]);

            let fullResponse = '';
            for await (const chunk of streamChatMessage(userMessage, chatHistory)) {
                fullResponse += chunk;
                // Update the last message (the bot's streaming message)
                setMessages((prev) => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1] = {
                        text: fullResponse,
                        sender: 'bot'
                    };
                    return newMessages;
                });
            }

            // Update chat history after full response is received
            setChatHistory((prev) => [...prev, [userMessage, fullResponse]]);
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

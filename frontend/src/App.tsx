import { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import KnowledgeBase from './components/KnowledgeBase';
import './App.css';

type Tab = 'chat' | 'knowledge';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  return (
    <div className="container">
      <div className="header">
        <h1>💬 DocuChat</h1>
        <p>Ask me anything about your documents!</p>
        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
          <button
            className={`tab-btn ${activeTab === 'knowledge' ? 'active' : ''}`}
            onClick={() => setActiveTab('knowledge')}
          >
            Knowledge Base
          </button>
        </div>
      </div>

      {activeTab === 'chat' ? <ChatInterface /> : <KnowledgeBase />}
    </div>
  );
}

export default App;

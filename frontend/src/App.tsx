import { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import KnowledgeBase from './components/KnowledgeBase';
import MonitoringDashboard from './components/MonitoringDashboard';
import './App.css';

type Tab = 'chat' | 'knowledge' | 'monitoring';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  return (
    <div className="container">
      <div className="header">
        <h1>💬 DocuChat</h1>
        <p>Your Document Assistant & System Monitoring Hub</p>
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
          <button
            className={`tab-btn ${activeTab === 'monitoring' ? 'active' : ''}`}
            onClick={() => setActiveTab('monitoring')}
          >
            🛡️ Monitoring
          </button>
        </div>
      </div>

      {activeTab === 'chat' && <ChatInterface />}
      {activeTab === 'knowledge' && <KnowledgeBase />}
      {activeTab === 'monitoring' && <MonitoringDashboard />}
    </div>
  );
}

export default App;

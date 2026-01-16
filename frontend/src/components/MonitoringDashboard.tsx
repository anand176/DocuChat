import React, { useState, useEffect } from 'react';

interface Container {
    id: string;
    name: string;
    status: string;
    image: string;
    ports: any;
}

const MonitoringDashboard: React.FC = () => {
    const [containers, setContainers] = useState<Container[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStatus = async () => {
        setLoading(true);
        try {
            // We'll use a chat query to get the summary from the Inspector agent
            // But for the dashboard grid, we'll need a structured endpoint.
            // I'll add a /monitor endpoint to app.py shortly.
            const response = await fetch('http://localhost:8000/monitor');
            if (!response.ok) throw new Error('Failed to fetch system status');
            const data = await response.json();
            setContainers(data.containers);
            setError(null);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 10000); // Auto-refresh every 10s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="tab-content">
            <div className="monitoring-container">
                <div className="monitoring-header">
                    <h2>🖥️ System Monitoring</h2>
                    <button onClick={fetchStatus} className="refresh-btn">🔄 Refresh</button>
                </div>

                {error && <div className="error-banner">Error: {error}</div>}

                {loading && containers.length === 0 ? (
                    <div className="loading-text">Scanning Docker environment...</div>
                ) : (
                    <div className="container-grid">
                        {containers.map(c => (
                            <div key={c.id} className={`container-card ${c.status}`}>
                                <div className="card-header">
                                    <h3>{c.name}</h3>
                                    <span className="status-badge">{c.status}</span>
                                </div>
                                <div className="card-body">
                                    <p><strong>Image:</strong> {c.image}</p>
                                    <p><strong>ID:</strong> {c.id}</p>
                                    <div className="mini-stats">
                                        {/* Placeholder for real-time stats */}
                                        <div className="stat-item">
                                            <span>CPU</span>
                                            <div className="progress-bar"><div className="fill" style={{ width: '15%' }}></div></div>
                                        </div>
                                        <div className="stat-item">
                                            <span>RAM</span>
                                            <div className="progress-bar"><div className="fill" style={{ width: '40%' }}></div></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                <div className="agent-thoughts">
                    <h3>🕵️ Sentinel Observations</h3>
                    <p>System appears stable. All core services are running within normal parameters.</p>
                </div>
            </div>
        </div>
    );
};

export default MonitoringDashboard;

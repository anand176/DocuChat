import React, { useState, useEffect } from 'react';
import { uploadDocument, listDocuments, deleteDocument } from '../services/api';
import type { DocumentInfo } from '../services/api';

const KnowledgeBase: React.FC = () => {
    const [documents, setDocuments] = useState<DocumentInfo[]>([]);
    const [loading, setLoading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [fileName, setFileName] = useState('No file chosen');

    useEffect(() => {
        loadDocuments();
    }, []);

    useEffect(() => {
        if (uploadStatus) {
            const timer = setTimeout(() => setUploadStatus(null), 5000);
            return () => clearTimeout(timer);
        }
    }, [uploadStatus]);

    const loadDocuments = async () => {
        setLoading(true);
        try {
            const response = await listDocuments();
            setDocuments(response.documents);
        } catch (error) {
            console.error('Error loading documents:', error);
            setDocuments([]);
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedFile(file);
            setFileName(file.name);
        } else {
            setSelectedFile(null);
            setFileName('No file chosen');
        }
    };

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedFile) {
            setUploadStatus({ message: 'Please select a file', type: 'error' });
            return;
        }

        setLoading(true);
        setUploadStatus({ message: 'Uploading file...', type: 'info' });

        try {
            const response = await uploadDocument(selectedFile);
            setUploadStatus({ message: `✅ ${response.message}`, type: 'success' });
            setSelectedFile(null);
            setFileName('No file chosen');
            // Reset file input
            const fileInput = document.getElementById('fileInput') as HTMLInputElement;
            if (fileInput) fileInput.value = '';
            // Reload documents
            await loadDocuments();
        } catch (error: any) {
            setUploadStatus({ message: `❌ Error: ${error.message}`, type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (source: string) => {
        if (!window.confirm(`Are you sure you want to delete "${source}"? This cannot be undone.`)) {
            return;
        }

        try {
            const response = await deleteDocument(source);
            alert(`✅ ${response.message}`);
            await loadDocuments();
        } catch (error: any) {
            alert(`❌ Error: ${error.message}`);
        }
    };

    return (
        <div className="tab-content">
            <div className="knowledge-container">
                <div className="upload-section">
                    <h2>📄 Upload Document</h2>
                    <p className="upload-hint">Upload PDF, DOCX, or TXT files to add to the knowledge base</p>
                    <form onSubmit={handleUpload}>
                        <div className="file-upload-wrapper">
                            <input
                                type="file"
                                id="fileInput"
                                accept=".pdf,.docx,.doc,.txt"
                                onChange={handleFileChange}
                            />
                            <label htmlFor="fileInput" className="file-label">
                                Choose File
                            </label>
                            <span className="file-name">{fileName}</span>
                        </div>
                        <button type="submit" className="upload-btn" disabled={loading}>
                            {loading ? 'Uploading...' : 'Upload'}
                        </button>
                    </form>
                    {uploadStatus && (
                        <div className={`status-message ${uploadStatus.type}`}>
                            {uploadStatus.message}
                        </div>
                    )}
                </div>

                <div className="documents-section">
                    <h2>📚 Documents in Knowledge Base</h2>
                    <button onClick={loadDocuments} className="refresh-btn" disabled={loading}>
                        🔄 Refresh
                    </button>
                    <div className="documents-list">
                        {loading && documents.length === 0 ? (
                            <div className="loading-text">Loading documents...</div>
                        ) : documents.length === 0 ? (
                            <div className="empty-message">
                                No documents in knowledge base yet. Upload a file to get started!
                            </div>
                        ) : (
                            documents.map((doc) => (
                                <div key={doc.source} className="document-item">
                                    <div className="document-info">
                                        <span className="document-name">{doc.file_name || doc.source}</span>
                                        <span className="document-type">{doc.file_type || 'text'}</span>
                                        <span className="document-count">{doc.count} chunks</span>
                                    </div>
                                    <button onClick={() => handleDelete(doc.source)} className="delete-btn">
                                        Delete
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default KnowledgeBase;

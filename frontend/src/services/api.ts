// API service for backend communication
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  message: string;
  history: string[][];
}

export interface ChatResponse {
  response: string;
  sources?: string[];
}

export interface LogMonitoringRequest {
  query: string;
  user_id: string;
  session_id?: string;
}

export interface LogMonitoringResponse {
  status: string;
  response: string;
  session_id: string;
}

export interface DocumentInfo {
  source: string;
  file_name: string;
  file_type: string;
  count: number;
}

export interface DocumentsResponse {
  status: string;
  documents: DocumentInfo[];
  total: number;
}

export interface UploadResponse {
  status: string;
  message: string;
  filename: string;
  chunks_added: number;
}

export interface DeleteResponse {
  status: string;
  message: string;
  source: string;
  deleted_count: number;
}

// Chat endpoint
export const sendChatMessage = async (message: string, history: string[][] = []): Promise<ChatResponse> => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
};

// Log Monitoring endpoint
export const sendLogMonitoring = async (query: string, user_id: string, session_id?: string): Promise<LogMonitoringResponse> => {
  const response = await fetch(`${API_BASE_URL}/agents/log_monitoring`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, user_id, session_id }),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch log monitoring response');
  }

  return response.json();
};

// Streaming Chat endpoint
export async function* streamChatMessage(message: string, history: string[][] = []): AsyncGenerator<string> {
  const response = await fetch(`${API_BASE_URL}/chat_stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error('Failed to start stream');
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Response body is null');
  }

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    yield decoder.decode(value, { stream: true });
  }
}

// Upload document
export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/add_document`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload document');
  }

  return response.json();
};

// List documents
export const listDocuments = async (): Promise<DocumentsResponse> => {
  const response = await fetch(`${API_BASE_URL}/list_documents`);

  if (!response.ok) {
    throw new Error('Failed to fetch documents');
  }

  return response.json();
};

// Delete document
export const deleteDocument = async (source: string): Promise<DeleteResponse> => {
  const response = await fetch(`${API_BASE_URL}/delete_document/${encodeURIComponent(source)}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete document');
  }

  return response.json();
};

// Health check
export const healthCheck = async (): Promise<{ status: string; service: string }> => {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
};

/**
 * Documents API
 */

import api from './client';
import type {
  Folder,
  Document,
  DocumentVersion,
  FolderCreateRequest,
  DocumentSearchParams,
} from '@/types/documents';

export const documentsApi = {
  // Folders
  getFolders: async (): Promise<Folder[]> => {
    return api.get<Folder[]>('/edms/folders');
  },

  getFolder: async (id: string): Promise<Folder> => {
    return api.get<Folder>(`/edms/folders/${id}`);
  },

  createFolder: async (data: FolderCreateRequest): Promise<Folder> => {
    return api.post<Folder>('/edms/folders', data);
  },

  updateFolder: async (id: string, name: string): Promise<Folder> => {
    return api.patch<Folder>(`/edms/folders/${id}`, { name });
  },

  deleteFolder: async (id: string): Promise<void> => {
    await api.delete(`/edms/folders/${id}`);
  },

  // Documents
  getDocuments: async (folderId: string): Promise<Document[]> => {
    return api.get<Document[]>(`/edms/folders/${folderId}/documents`);
  },

  getDocument: async (id: string): Promise<Document> => {
    return api.get<Document>(`/edms/documents/${id}`);
  },

  uploadDocument: async (
    folderId: string,
    file: File,
    description?: string,
    tags?: string[]
  ): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    if (description) formData.append('description', description);
    if (tags) formData.append('tags', JSON.stringify(tags));

    const token = localStorage.getItem('access_token');
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/edms/folders/${folderId}/documents`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload document');
    }

    return response.json();
  },

  updateDocument: async (
    id: string,
    data: { name?: string; description?: string; tags?: string[] }
  ): Promise<Document> => {
    return api.patch<Document>(`/edms/documents/${id}`, data);
  },

  deleteDocument: async (id: string): Promise<void> => {
    await api.delete(`/edms/documents/${id}`);
  },

  downloadDocument: async (id: string, version?: number): Promise<Blob> => {
    const token = localStorage.getItem('access_token');
    const url = version
      ? `/edms/documents/${id}/download?version=${version}`
      : `/edms/documents/${id}/download`;

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}${url}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Failed to download document');
    }

    return response.blob();
  },

  // Versions
  getVersions: async (documentId: string): Promise<DocumentVersion[]> => {
    return api.get<DocumentVersion[]>(`/edms/documents/${documentId}/versions`);
  },

  uploadNewVersion: async (
    documentId: string,
    file: File,
    changeNotes?: string
  ): Promise<DocumentVersion> => {
    const formData = new FormData();
    formData.append('file', file);
    if (changeNotes) formData.append('change_notes', changeNotes);

    const token = localStorage.getItem('access_token');
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/edms/documents/${documentId}/versions`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload new version');
    }

    return response.json();
  },

  // Search
  searchDocuments: async (params: DocumentSearchParams): Promise<Document[]> => {
    const searchParams: Record<string, string> = {};
    if (params.query) searchParams.q = params.query;
    if (params.folder_id) searchParams.folder_id = params.folder_id;
    if (params.recursive !== undefined) searchParams.recursive = String(params.recursive);
    if (params.extension) searchParams.extension = params.extension;
    if (params.tags) searchParams.tags = params.tags.join(',');
    if (params.date_from) searchParams.date_from = params.date_from;
    if (params.date_to) searchParams.date_to = params.date_to;

    return api.get<Document[]>('/edms/documents/search', { params: searchParams });
  },

  // Recent
  getRecentDocuments: async (): Promise<Document[]> => {
    return api.get<Document[]>('/edms/documents/recent');
  },
};

export default documentsApi;

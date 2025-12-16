/**
 * Document Management Types
 */

export interface Folder {
  id: string;
  name: string;
  slug: string;
  parent_id: string | null;
  path: string;
  depth: number;
  owner_id: string;
  is_system: boolean;
  document_count?: number;
  children?: Folder[];
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  folder_id: string;
  name: string;
  slug: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  extension: string;
  current_version: number;
  uploaded_by: string;
  uploaded_by_name?: string;
  description?: string;
  tags?: string[];
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  file_path: string;
  file_size: number;
  uploaded_by: string;
  uploaded_by_name?: string;
  change_notes?: string;
  created_at: string;
}

export type FolderPermission = 'view' | 'upload' | 'edit' | 'delete' | 'manage';

export interface FolderPermissionRecord {
  id: string;
  folder_id: string;
  user_id?: string;
  role?: string;
  permission: FolderPermission;
  granted_by: string;
}

export interface FolderCreateRequest {
  name: string;
  parent_id?: string;
}

export interface DocumentUploadRequest {
  folder_id: string;
  description?: string;
  tags?: string[];
}

export interface DocumentSearchParams {
  query?: string;
  folder_id?: string;
  recursive?: boolean;
  extension?: string;
  tags?: string[];
  date_from?: string;
  date_to?: string;
  uploaded_by?: string;
}

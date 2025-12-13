'use client';

/**
 * Documents Page - EDMS
 */

import { useState, useEffect, useCallback } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { FolderTree } from '@/components/documents/folder-tree';
import { DocumentList } from '@/components/documents/document-list';
import { UploadDialog } from '@/components/documents/upload-dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import documentsApi from '@/lib/api/documents';
import type { Folder, Document } from '@/types/documents';

export default function DocumentsPage() {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Dialogs
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [createFolderDialogOpen, setCreateFolderDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderParentId, setNewFolderParentId] = useState<string | null>(null);
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);

  // Load folders
  const loadFolders = useCallback(async () => {
    try {
      const data = await documentsApi.getFolders();
      setFolders(data);
    } catch (error) {
      console.error('Failed to load folders:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load documents
  const loadDocuments = useCallback(async (folderId?: string) => {
    setIsLoadingDocs(true);
    try {
      if (folderId) {
        const data = await documentsApi.getDocuments(folderId);
        setDocuments(data);
      } else {
        // Load recent or search results
        const data = await documentsApi.getRecentDocuments();
        setDocuments(data);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
      setDocuments([]);
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    loadFolders();
  }, [loadFolders]);

  useEffect(() => {
    loadDocuments(selectedFolder?.id);
  }, [selectedFolder, loadDocuments]);

  // Handle folder selection
  const handleSelectFolder = (folder: Folder) => {
    setSelectedFolder(folder.id ? folder : null);
  };

  // Handle create folder
  const handleCreateFolder = (parentId: string | null) => {
    setNewFolderParentId(parentId);
    setNewFolderName('');
    setCreateFolderDialogOpen(true);
  };

  const submitCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    setIsCreatingFolder(true);
    try {
      await documentsApi.createFolder({
        name: newFolderName.trim(),
        parent_id: newFolderParentId || undefined,
      });
      await loadFolders();
      setCreateFolderDialogOpen(false);
    } catch (error) {
      console.error('Failed to create folder:', error);
    } finally {
      setIsCreatingFolder(false);
    }
  };

  // Handle upload
  const handleUpload = async (file: File, description?: string, tags?: string[]) => {
    if (!selectedFolder?.id) {
      throw new Error('Please select a folder first');
    }
    await documentsApi.uploadDocument(selectedFolder.id, file, description, tags);
    await loadDocuments(selectedFolder.id);
  };

  // Handle download
  const handleDownload = async (doc: Document) => {
    try {
      const blob = await documentsApi.downloadDocument(doc.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download:', error);
    }
  };

  // Handle delete
  const handleDelete = async (doc: Document) => {
    if (!confirm(`Are you sure you want to delete "${doc.name}"?`)) return;

    try {
      await documentsApi.deleteDocument(doc.id);
      await loadDocuments(selectedFolder?.id);
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  // Handle search
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadDocuments(selectedFolder?.id);
      return;
    }

    setIsLoadingDocs(true);
    try {
      const results = await documentsApi.searchDocuments({
        query: searchQuery,
        folder_id: selectedFolder?.id,
        recursive: true,
      });
      setDocuments(results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  // Breadcrumb
  const getBreadcrumb = () => {
    if (!selectedFolder) return ['All Documents'];
    const parts = selectedFolder.path.split('/').filter(Boolean);
    return ['All Documents', ...parts];
  };

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-8rem)]">
        {/* Sidebar - Folder Tree */}
        <div className="w-64 flex-shrink-0 border-r overflow-auto">
          <div className="p-4 border-b">
            <h2 className="font-semibold">Folders</h2>
          </div>
          {isLoading ? (
            <div className="p-4 text-center text-muted-foreground">
              Loading folders...
            </div>
          ) : (
            <FolderTree
              folders={folders}
              selectedFolderId={selectedFolder?.id}
              onSelectFolder={handleSelectFolder}
              onCreateFolder={handleCreateFolder}
            />
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b space-y-4">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm">
              {getBreadcrumb().map((crumb, index, arr) => (
                <span key={index} className="flex items-center gap-2">
                  {index > 0 && (
                    <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  )}
                  <span
                    className={
                      index === arr.length - 1
                        ? 'font-medium'
                        : 'text-muted-foreground hover:text-foreground cursor-pointer'
                    }
                  >
                    {crumb}
                  </span>
                </span>
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <div className="flex-1 flex gap-2">
                <Input
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="max-w-xs"
                />
                <Button variant="outline" onClick={handleSearch}>
                  Search
                </Button>
              </div>

              <Button
                onClick={() => setUploadDialogOpen(true)}
                disabled={!selectedFolder?.id}
              >
                <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Upload
              </Button>
            </div>
          </div>

          {/* Document List */}
          <div className="flex-1 overflow-auto p-4">
            <DocumentList
              documents={documents}
              isLoading={isLoadingDocs}
              onDownload={handleDownload}
              onDelete={handleDelete}
            />
          </div>
        </div>
      </div>

      {/* Upload Dialog */}
      <UploadDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        folderName={selectedFolder?.name || 'folder'}
        onUpload={handleUpload}
      />

      {/* Create Folder Dialog */}
      <Dialog open={createFolderDialogOpen} onOpenChange={setCreateFolderDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create New Folder</DialogTitle>
            <DialogDescription>
              {newFolderParentId
                ? 'Create a subfolder'
                : 'Create a new root folder'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="folderName">Folder Name</Label>
              <Input
                id="folderName"
                placeholder="Enter folder name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && submitCreateFolder()}
                disabled={isCreatingFolder}
                autoFocus
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateFolderDialogOpen(false)}
              disabled={isCreatingFolder}
            >
              Cancel
            </Button>
            <Button
              onClick={submitCreateFolder}
              disabled={!newFolderName.trim() || isCreatingFolder}
            >
              {isCreatingFolder ? 'Creating...' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}

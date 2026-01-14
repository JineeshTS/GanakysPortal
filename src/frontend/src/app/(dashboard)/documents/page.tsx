'use client';

import { useState, useEffect, useRef } from 'react';
import {
  Upload, Grid, List, Search, Filter, Plus, FolderPlus,
  Download, RefreshCw, Loader2, FileText, X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/layout/page-header';
import { useApi } from '@/hooks/use-api';

// API Response Types
interface ApiFolder {
  id: string;
  name: string;
  path: string;
  parent_id: string | null;
  is_system: boolean;
  created_at: string;
  document_count?: number;
  children?: ApiFolder[];
}

interface ApiDocument {
  id: string;
  name: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  category: string;
  document_type: string;
  version: number;
  is_confidential: boolean;
  folder_id: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}
import { FolderTree } from '@/components/documents/FolderTree';
import { DocumentList } from '@/components/documents/DocumentList';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';

// Sample data
const sampleFolders = [
  {
    id: '1',
    name: 'HR Documents',
    path: '/HR Documents',
    level: 0,
    documentCount: 24,
    isSystem: true,
    children: [
      { id: '1-1', name: 'Policies', path: '/HR Documents/Policies', level: 1, documentCount: 8 },
      { id: '1-2', name: 'Templates', path: '/HR Documents/Templates', level: 1, documentCount: 12 },
    ],
  },
  {
    id: '2',
    name: 'Employee Records',
    path: '/Employee Records',
    level: 0,
    documentCount: 156,
    isSystem: true,
  },
  {
    id: '3',
    name: 'Payroll',
    path: '/Payroll',
    level: 0,
    documentCount: 45,
    isSystem: true,
    children: [
      { id: '3-1', name: 'Payslips', path: '/Payroll/Payslips', level: 1, documentCount: 30 },
      { id: '3-2', name: 'Form 16', path: '/Payroll/Form 16', level: 1, documentCount: 15 },
    ],
  },
  {
    id: '4',
    name: 'Compliance',
    path: '/Compliance',
    level: 0,
    documentCount: 28,
    isSystem: true,
  },
  {
    id: '5',
    name: 'Finance',
    path: '/Finance',
    level: 0,
    documentCount: 67,
    isSystem: true,
    children: [
      { id: '5-1', name: 'Invoices', path: '/Finance/Invoices', level: 1, documentCount: 40 },
      { id: '5-2', name: 'Bills', path: '/Finance/Bills', level: 1, documentCount: 27 },
    ],
  },
];

const sampleDocuments = [
  {
    id: '1',
    name: 'Leave Policy 2024',
    fileName: 'leave_policy_2024.pdf',
    fileSize: 245000,
    mimeType: 'application/pdf',
    category: 'HR',
    documentType: 'policy',
    version: 2,
    isConfidential: false,
    createdBy: 'Admin',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-03-10T14:20:00Z',
  },
  {
    id: '2',
    name: 'Employee Handbook',
    fileName: 'employee_handbook_v3.pdf',
    fileSize: 1250000,
    mimeType: 'application/pdf',
    category: 'HR',
    documentType: 'handbook',
    version: 3,
    isConfidential: false,
    createdBy: 'HR Manager',
    createdAt: '2023-06-01T09:00:00Z',
    updatedAt: '2024-02-28T16:45:00Z',
  },
  {
    id: '3',
    name: 'Salary Structure Template',
    fileName: 'salary_template.xlsx',
    fileSize: 85000,
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    category: 'Payroll',
    documentType: 'template',
    version: 1,
    isConfidential: true,
    createdBy: 'Finance Manager',
    createdAt: '2024-04-01T11:00:00Z',
    updatedAt: '2024-04-01T11:00:00Z',
  },
  {
    id: '4',
    name: 'Company Logo',
    fileName: 'logo_high_res.png',
    fileSize: 450000,
    mimeType: 'image/png',
    category: 'General',
    documentType: 'asset',
    version: 1,
    isConfidential: false,
    createdBy: 'Admin',
    createdAt: '2023-01-10T08:00:00Z',
    updatedAt: '2023-01-10T08:00:00Z',
  },
];

// Helper function to transform API folder to local format
function transformFolder(apiFolder: ApiFolder, level: number = 0): any {
  return {
    id: apiFolder.id,
    name: apiFolder.name,
    path: apiFolder.path,
    level,
    documentCount: apiFolder.document_count || 0,
    isSystem: apiFolder.is_system,
    children: apiFolder.children?.map(child => transformFolder(child, level + 1)),
  };
}

// Helper function to transform API document to local format
function transformDocument(apiDoc: ApiDocument): any {
  return {
    id: apiDoc.id,
    name: apiDoc.name,
    fileName: apiDoc.file_name,
    fileSize: apiDoc.file_size,
    mimeType: apiDoc.mime_type,
    category: apiDoc.category,
    documentType: apiDoc.document_type,
    version: apiDoc.version,
    isConfidential: apiDoc.is_confidential,
    createdBy: apiDoc.created_by,
    createdAt: apiDoc.created_at,
    updatedAt: apiDoc.updated_at,
  };
}

export default function DocumentsPage() {
  const api = useApi();
  const [selectedFolder, setSelectedFolder] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [createFolderDialogOpen, setCreateFolderDialogOpen] = useState(false);
  const [folders, setFolders] = useState<any[]>(sampleFolders);
  const [documents, setDocuments] = useState<any[]>(sampleDocuments);
  const [loading, setLoading] = useState(true);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderDescription, setNewFolderDescription] = useState('');
  const [creatingFolder, setCreatingFolder] = useState(false);

  // Upload state
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState('');
  const [uploadCategoryId, setUploadCategoryId] = useState('');
  const [uploadTypeId, setUploadTypeId] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [uploading, setUploading] = useState(false);

  // Categories and types from API
  const [documentCategories, setDocumentCategories] = useState<Array<{id: string, code: string, name: string}>>([]);
  const [documentTypes, setDocumentTypes] = useState<Array<{id: string, code: string, name: string, category_id: string}>>([]);

  // Filtered types based on selected category
  const filteredTypes = uploadCategoryId
    ? documentTypes.filter(t => t.category_id === uploadCategoryId)
    : documentTypes;

  // Fetch folders, documents, categories and types from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch folders
        const foldersResponse = await api.get('/documents/folders');
        if (Array.isArray(foldersResponse) && foldersResponse.length > 0) {
          setFolders(foldersResponse.map((f: ApiFolder) => transformFolder(f)));
        }

        // Fetch documents
        const docsResponse = await api.get('/documents?limit=100');
        if (docsResponse?.data && Array.isArray(docsResponse.data) && docsResponse.data.length > 0) {
          setDocuments(docsResponse.data.map(transformDocument));
        }

        // Fetch categories
        const categoriesResponse = await api.get('/documents/settings/categories');
        if (Array.isArray(categoriesResponse) && categoriesResponse.length > 0) {
          setDocumentCategories(categoriesResponse);
          // Set default category to 'general'
          const generalCat = categoriesResponse.find((c: any) => c.code === 'general');
          if (generalCat) setUploadCategoryId(generalCat.id);
        }

        // Fetch document types
        const typesResponse = await api.get('/documents/settings/types');
        if (Array.isArray(typesResponse) && typesResponse.length > 0) {
          setDocumentTypes(typesResponse);
          // Set default type to 'other'
          const otherType = typesResponse.find((t: any) => t.code === 'other');
          if (otherType) setUploadTypeId(otherType.id);
        }
      } catch (error) {
        console.error('Failed to fetch documents:', error);
        // Keep sample data on error
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once on mount

  // Auto-select first type when category changes
  useEffect(() => {
    if (uploadCategoryId && documentTypes.length > 0) {
      const typesForCategory = documentTypes.filter(t => t.category_id === uploadCategoryId);
      if (typesForCategory.length > 0 && !typesForCategory.find(t => t.id === uploadTypeId)) {
        setUploadTypeId(typesForCategory[0].id);
      }
    }
  }, [uploadCategoryId, documentTypes, uploadTypeId]);

  // Create folder handler
  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    setCreatingFolder(true);
    try {
      const response = await api.post('/documents/folders', {
        name: newFolderName.trim(),
        description: newFolderDescription.trim() || null,
        parent_id: selectedFolder?.id || null,
      });

      if (response) {
        // Add new folder to list
        const newFolder = transformFolder(response as ApiFolder);
        setFolders(prev => [...prev, newFolder]);
        setNewFolderName('');
        setNewFolderDescription('');
        setCreateFolderDialogOpen(false);
      }
    } catch (error) {
      console.error('Failed to create folder:', error);
    } finally {
      setCreatingFolder(false);
    }
  };

  // File selection handler
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      // Auto-fill name from filename if empty
      if (!uploadName) {
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
        setUploadName(nameWithoutExt);
      }
    }
  };

  // Upload handler
  const handleUpload = async () => {
    if (!selectedFile || !uploadName.trim() || !uploadCategoryId || !uploadTypeId) return;

    // Get category and type codes
    const selectedCategory = documentCategories.find(c => c.id === uploadCategoryId);
    const selectedType = documentTypes.find(t => t.id === uploadTypeId);

    if (!selectedCategory || !selectedType) {
      alert('Please select a category and document type');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Build query params for the upload
      const params = new URLSearchParams({
        name: uploadName.trim(),
        category: selectedCategory.code,
        document_type: selectedType.code,
      });
      if (uploadDescription.trim()) {
        params.append('description', uploadDescription.trim());
      }
      if (selectedFolder?.id) {
        params.append('folder_id', selectedFolder.id);
      }

      const response = await fetch(`/api/v1/documents?${params.toString()}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const newDoc = await response.json();

      // Add to documents list
      setDocuments(prev => [transformDocument(newDoc), ...prev]);

      // Reset form
      resetUploadForm();
      setUploadDialogOpen(false);
    } catch (error) {
      console.error('Upload failed:', error);
      alert(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // Reset upload form
  const resetUploadForm = () => {
    setSelectedFile(null);
    setUploadName('');
    setUploadDescription('');
    // Reset to defaults
    const generalCat = documentCategories.find(c => c.code === 'general');
    if (generalCat) setUploadCategoryId(generalCat.id);
    const otherType = documentTypes.find(t => t.code === 'other');
    if (otherType) setUploadTypeId(otherType.id);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Reset upload form when dialog closes
  const handleUploadDialogChange = (open: boolean) => {
    setUploadDialogOpen(open);
    if (!open) {
      resetUploadForm();
    }
  };

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.fileName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || doc.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Documents"
        description="Manage company documents and files"
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => setCreateFolderDialogOpen(true)}>
              <FolderPlus className="h-4 w-4 mr-2" />
              New Folder
            </Button>
            <Button size="sm" onClick={() => setUploadDialogOpen(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Upload
            </Button>
          </>
        }
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r bg-muted/30 overflow-y-auto hidden md:block">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <FolderTree
              folders={folders}
              selectedFolderId={selectedFolder?.id}
              onSelectFolder={setSelectedFolder}
              onCreateFolder={() => setCreateFolderDialogOpen(true)}
            />
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* Toolbar */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>

            <div className="flex items-center gap-2">
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-36">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="HR">HR</SelectItem>
                  <SelectItem value="Payroll">Payroll</SelectItem>
                  <SelectItem value="Finance">Finance</SelectItem>
                  <SelectItem value="Compliance">Compliance</SelectItem>
                  <SelectItem value="General">General</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex border rounded-lg">
                <Button
                  variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                  size="icon"
                  className="rounded-r-none"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
                  size="icon"
                  className="rounded-l-none"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Breadcrumb */}
          {selectedFolder && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
              <button
                className="hover:text-foreground"
                onClick={() => setSelectedFolder(null)}
              >
                All Documents
              </button>
              <span>/</span>
              <span className="text-foreground">{selectedFolder.name}</span>
            </div>
          )}

          {/* Document List */}
          <DocumentList
            documents={filteredDocuments}
            viewMode={viewMode}
            onView={(doc) => console.log('View:', doc)}
            onDownload={(doc) => console.log('Download:', doc)}
            onShare={(doc) => console.log('Share:', doc)}
            onDelete={(doc) => console.log('Delete:', doc)}
            onEdit={(doc) => console.log('Edit:', doc)}
          />
        </main>
      </div>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={handleUploadDialogChange}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <DialogDescription>
              Upload a new document{selectedFolder ? ` to "${selectedFolder.name}"` : ' to the system'}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {/* File Selection */}
            <div>
              <Label>File</Label>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                className="hidden"
                accept="*/*"
              />
              {selectedFile ? (
                <div className="mt-1.5 flex items-center gap-2 p-3 border rounded-lg bg-muted/50">
                  <FileText className="h-8 w-8 text-blue-500" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => {
                      setSelectedFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = '';
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div
                  className="mt-1.5 border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Click to browse or drag and drop
                  </p>
                </div>
              )}
            </div>

            {/* Document Name */}
            <div>
              <Label htmlFor="uploadName">Document Name *</Label>
              <Input
                id="uploadName"
                placeholder="Enter document name"
                className="mt-1.5"
                value={uploadName}
                onChange={(e) => setUploadName(e.target.value)}
              />
            </div>

            {/* Category and Type Row */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Category *</Label>
                <Select value={uploadCategoryId} onValueChange={setUploadCategoryId}>
                  <SelectTrigger className="mt-1.5">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {documentCategories.map((cat) => (
                      <SelectItem key={cat.id} value={cat.id}>
                        {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Document Type *</Label>
                <Select value={uploadTypeId} onValueChange={setUploadTypeId}>
                  <SelectTrigger className="mt-1.5">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {filteredTypes.map((type) => (
                      <SelectItem key={type.id} value={type.id}>
                        {type.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Description */}
            <div>
              <Label htmlFor="uploadDescription">Description (Optional)</Label>
              <Input
                id="uploadDescription"
                placeholder="Enter description"
                className="mt-1.5"
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => handleUploadDialogChange(false)} disabled={uploading}>
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploading || !selectedFile || !uploadName.trim() || !uploadCategoryId || !uploadTypeId}
            >
              {uploading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Folder Dialog */}
      <Dialog open={createFolderDialogOpen} onOpenChange={setCreateFolderDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Folder</DialogTitle>
            <DialogDescription>
              Create a new folder to organize your documents
              {selectedFolder && ` inside "${selectedFolder.name}"`}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <Label htmlFor="folderName">Folder Name</Label>
              <Input
                id="folderName"
                placeholder="Enter folder name"
                className="mt-1.5"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="folderDescription">Description (Optional)</Label>
              <Input
                id="folderDescription"
                placeholder="Enter description"
                className="mt-1.5"
                value={newFolderDescription}
                onChange={(e) => setNewFolderDescription(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateFolderDialogOpen(false)} disabled={creatingFolder}>
              Cancel
            </Button>
            <Button onClick={handleCreateFolder} disabled={creatingFolder || !newFolderName.trim()}>
              {creatingFolder ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Folder'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

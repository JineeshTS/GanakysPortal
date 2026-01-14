'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useApi, useAuthStore, useToast } from '@/hooks'
import {
  FileText,
  Upload,
  Download,
  Eye,
  Search,
  Folder,
  File,
  FileImage,
  FileBadge,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react'

interface Document {
  id: string
  name: string
  description?: string
  category: string
  document_type: string
  folder_id?: string
  folder_name?: string
  file_name: string
  file_size?: number
  mime_type?: string
  file_extension?: string
  version: number
  is_latest: boolean
  is_confidential: boolean
  access_level: string
  status: string
  tags?: string[]
  expiry_date?: string
  created_by: string
  created_at: string
  updated_at: string
}

interface DocumentListResponse {
  success: boolean
  data: Document[]
  meta: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

// Document type mappings for display
const documentTypeLabels: Record<string, string> = {
  offer_letter: 'Offer Letter',
  appointment_letter: 'Appointment Letter',
  experience_letter: 'Experience Letter',
  relieving_letter: 'Relieving Letter',
  salary_slip: 'Salary Slip',
  form_16: 'Form 16',
  bonus_letter: 'Bonus Letter',
  increment_letter: 'Increment Letter',
  resume: 'Resume',
  photo: 'Photo',
  id_proof: 'ID Proof',
  address_proof: 'Address Proof',
  pan_card: 'PAN Card',
  aadhaar: 'Aadhaar Card',
  passport: 'Passport',
  educational_cert: 'Educational Certificate',
  experience_cert: 'Experience Certificate',
  bank_details: 'Bank Details',
  nda: 'NDA Agreement',
  other: 'Other',
}

// Category mappings for display
const categoryLabels: Record<string, string> = {
  hr: 'HR',
  employee: 'Employee',
  legal: 'Legal',
  finance: 'Finance',
  compliance: 'Compliance',
  general: 'General',
  payroll: 'Payroll',
}

// Required document types for employees
const requiredDocumentTypes = [
  { type: 'aadhaar', label: 'Aadhaar Card' },
  { type: 'pan_card', label: 'PAN Card' },
  { type: 'photo', label: 'Passport Size Photo' },
  { type: 'educational_cert', label: 'Educational Certificate' },
  { type: 'experience_cert', label: 'Experience Certificate' },
  { type: 'bank_details', label: 'Bank Details' },
  { type: 'address_proof', label: 'Address Proof' },
]

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  draft: 'bg-yellow-100 text-yellow-800',
  archived: 'bg-gray-100 text-gray-800',
  expired: 'bg-red-100 text-red-800',
}

const categoryIcons: Record<string, React.ReactNode> = {
  employee: <FileBadge className="h-4 w-4" />,
  hr: <FileText className="h-4 w-4" />,
  legal: <FileBadge className="h-4 w-4" />,
  finance: <File className="h-4 w-4" />,
  compliance: <Folder className="h-4 w-4" />,
  payroll: <FileText className="h-4 w-4" />,
  general: <File className="h-4 w-4" />,
}

const formatFileSize = (bytes?: number) => {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function MyDocumentsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('uploaded')
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false)
  const [uploadForm, setUploadForm] = useState({
    name: '',
    document_type: '',
    description: ''
  })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { user } = useAuthStore()
  const { showToast } = useToast()

  // API hooks
  const { data: myDocsData, isLoading: isLoadingMyDocs, error: myDocsError, get: getMyDocs } = useApi<DocumentListResponse>()
  const { data: companyDocsData, isLoading: isLoadingCompanyDocs, get: getCompanyDocs } = useApi<DocumentListResponse>()
  const { isLoading: isUploading, post: uploadDocument } = useApi<Document>()

  // Fetch documents
  const fetchData = useCallback(() => {
    // Fetch employee documents (category=employee)
    getMyDocs('/documents?category=employee&limit=50')
    // Fetch company HR documents (category=hr for offer letters, appointment letters, etc.)
    getCompanyDocs('/documents?category=hr&limit=50')
  }, [getMyDocs, getCompanyDocs])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const myDocuments = myDocsData?.data || []
  const companyDocuments = companyDocsData?.data || []

  const filteredMyDocuments = myDocuments.filter(doc =>
    doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.document_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Calculate document completion status
  const uploadedTypes = new Set(myDocuments.map(d => d.document_type))
  const documentRequirements = requiredDocumentTypes.map(req => ({
    ...req,
    status: uploadedTypes.has(req.type) ? 'uploaded' : 'pending'
  }))
  const uploadedCount = documentRequirements.filter(d => d.status === 'uploaded').length
  const totalRequired = documentRequirements.length

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      if (!uploadForm.name) {
        setUploadForm(prev => ({ ...prev, name: file.name.split('.')[0] }))
      }
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || !uploadForm.name || !uploadForm.document_type) {
      showToast('error', 'Please fill all required fields and select a file')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    // Build query params for upload
    const params = new URLSearchParams({
      name: uploadForm.name,
      category: 'employee',
      document_type: uploadForm.document_type,
    })
    if (uploadForm.description) {
      params.append('description', uploadForm.description)
    }

    try {
      const response = await fetch(`/api/v1/documents?${params.toString()}`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (response.ok) {
        showToast('success', 'Document uploaded successfully')
        setIsUploadDialogOpen(false)
        setUploadForm({ name: '', document_type: '', description: '' })
        setSelectedFile(null)
        fetchData()
      } else {
        const error = await response.json()
        showToast('error', error.detail || 'Failed to upload document')
      }
    } catch {
      showToast('error', 'Failed to upload document')
    }
  }

  const handleDownload = async (docId: string, fileName: string) => {
    try {
      const response = await fetch(`/api/v1/documents/${docId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = fileName
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        showToast('error', 'Failed to download document')
      }
    } catch {
      showToast('error', 'Failed to download document')
    }
  }

  const isLoading = isLoadingMyDocs || isLoadingCompanyDocs

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Documents"
          description="Manage your personal and company documents"
          icon={<FileText className="h-6 w-6" />}
        />
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-24 w-full" />
          </CardContent>
        </Card>
        <div className="grid grid-cols-1 gap-4">
          {[1, 2, 3].map(i => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Documents"
        description="Manage your personal and company documents"
        icon={<FileText className="h-6 w-6" />}
        actions={
          <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload Document
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Upload Document</DialogTitle>
                <DialogDescription>
                  Upload a document to your employee file
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="file">Select File</Label>
                  <Input
                    id="file"
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  />
                  {selectedFile && (
                    <p className="text-sm text-muted-foreground">
                      Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="doc-name">Document Name</Label>
                  <Input
                    id="doc-name"
                    placeholder="Enter document name"
                    value={uploadForm.name}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="doc-type">Document Type</Label>
                  <Select
                    value={uploadForm.document_type}
                    onValueChange={(value) => setUploadForm(prev => ({ ...prev, document_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select document type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="aadhaar">Aadhaar Card</SelectItem>
                      <SelectItem value="pan_card">PAN Card</SelectItem>
                      <SelectItem value="passport">Passport</SelectItem>
                      <SelectItem value="id_proof">ID Proof</SelectItem>
                      <SelectItem value="address_proof">Address Proof</SelectItem>
                      <SelectItem value="photo">Passport Size Photo</SelectItem>
                      <SelectItem value="educational_cert">Educational Certificate</SelectItem>
                      <SelectItem value="experience_cert">Experience Certificate</SelectItem>
                      <SelectItem value="bank_details">Bank Details</SelectItem>
                      <SelectItem value="resume">Resume</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description (Optional)</Label>
                  <Input
                    id="description"
                    placeholder="Brief description..."
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, description: e.target.value }))}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsUploadDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleUpload} disabled={isUploading || !selectedFile}>
                    {isUploading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                    Upload
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        }
      />

      {/* Document Completion Status */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg">Document Completion Status</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {uploadedCount} of {totalRequired} required documents uploaded
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-48 bg-muted rounded-full h-3">
                <div
                  className="bg-green-500 h-3 rounded-full transition-all"
                  style={{ width: `${(uploadedCount / totalRequired) * 100}%` }}
                />
              </div>
              <span className="text-lg font-bold text-green-600">
                {Math.round((uploadedCount / totalRequired) * 100)}%
              </span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            {documentRequirements.map((doc) => (
              <Badge
                key={doc.type}
                variant="outline"
                className={doc.status === 'uploaded' ? 'bg-green-50' : 'bg-yellow-50'}
              >
                {doc.status === 'uploaded' ? (
                  <CheckCircle className="h-3 w-3 mr-1 text-green-600" />
                ) : (
                  <AlertCircle className="h-3 w-3 mr-1 text-yellow-600" />
                )}
                {doc.label}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="uploaded">My Uploads</TabsTrigger>
            <TabsTrigger value="company">Company Documents</TabsTrigger>
          </TabsList>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        <TabsContent value="uploaded" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Documents</CardTitle>
              <CardDescription>Documents you have submitted to the company</CardDescription>
            </CardHeader>
            <CardContent>
              {myDocsError ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <AlertCircle className="h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-muted-foreground">{myDocsError}</p>
                  <Button variant="outline" onClick={fetchData} className="mt-4">
                    Try Again
                  </Button>
                </div>
              ) : filteredMyDocuments.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <FileText className="h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-muted-foreground">No documents uploaded yet</p>
                  <Button variant="outline" onClick={() => setIsUploadDialogOpen(true)} className="mt-4">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Your First Document
                  </Button>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Document</th>
                        <th className="text-left p-4 font-medium">Type</th>
                        <th className="text-center p-4 font-medium">Size</th>
                        <th className="text-left p-4 font-medium">Uploaded</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredMyDocuments.map((doc) => (
                        <tr key={doc.id} className="border-t hover:bg-muted/30">
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <FileText className="h-4 w-4 text-red-500" />
                              <span className="font-medium">{doc.name}</span>
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center gap-1 text-muted-foreground">
                              {categoryIcons[doc.category] || <File className="h-4 w-4" />}
                              {documentTypeLabels[doc.document_type] || doc.document_type}
                            </div>
                          </td>
                          <td className="p-4 text-center text-muted-foreground">{formatFileSize(doc.file_size)}</td>
                          <td className="p-4 text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(doc.created_at).toLocaleDateString('en-IN')}
                            </div>
                          </td>
                          <td className="p-4 text-center">
                            <Badge className={statusColors[doc.status] || 'bg-gray-100 text-gray-800'}>{doc.status}</Badge>
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <Button variant="ghost" size="icon" onClick={() => handleDownload(doc.id, doc.file_name)}>
                                <Download className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="company" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Company Documents</CardTitle>
              <CardDescription>Documents issued to you by the company</CardDescription>
            </CardHeader>
            <CardContent>
              {companyDocuments.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <Folder className="h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-muted-foreground">No company documents available</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {companyDocuments.map((doc) => (
                    <Card key={doc.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-red-100 rounded-lg">
                              <FileText className="h-6 w-6 text-red-600" />
                            </div>
                            <div>
                              <p className="font-medium">{doc.name}</p>
                              <p className="text-sm text-muted-foreground">
                                {documentTypeLabels[doc.document_type] || doc.document_type}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="mt-4 flex items-center justify-between">
                          <div className="text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(doc.created_at).toLocaleDateString('en-IN')}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDownload(doc.id, doc.file_name)}
                            >
                              <Download className="h-4 w-4 mr-1" />
                              Download
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

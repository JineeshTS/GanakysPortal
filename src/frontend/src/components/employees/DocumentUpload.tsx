'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/format'
import {
  Upload,
  X,
  FileText,
  Image,
  File,
  CheckCircle,
  Clock,
  AlertCircle,
  Download,
  Eye,
  Trash2,
  RefreshCw
} from 'lucide-react'
import type { EmployeeDocument, DocumentType } from '@/types'

// ============================================================================
// Types
// ============================================================================

interface DocumentUploadProps {
  documents?: EmployeeDocument[]
  onUpload?: (type: DocumentType, file: File) => Promise<void>
  onDelete?: (documentId: string) => Promise<void>
  onVerify?: (documentId: string) => Promise<void>
  onReupload?: (documentId: string, file: File) => Promise<void>
  onView?: (document: EmployeeDocument) => void
  onDownload?: (document: EmployeeDocument) => void
  employeeId: string
  readOnly?: boolean
  requiredDocuments?: DocumentType[]
  className?: string
}

interface DocumentCategoryProps {
  title: string
  description?: string
  documents: EmployeeDocument[]
  documentTypes: { type: DocumentType; label: string; required?: boolean }[]
  onUpload?: (type: DocumentType, file: File) => Promise<void>
  onDelete?: (documentId: string) => Promise<void>
  onVerify?: (documentId: string) => Promise<void>
  onReupload?: (documentId: string, file: File) => Promise<void>
  onView?: (document: EmployeeDocument) => void
  onDownload?: (document: EmployeeDocument) => void
  readOnly?: boolean
}

interface SingleDocumentUploadProps {
  type: DocumentType
  label: string
  document?: EmployeeDocument
  required?: boolean
  onUpload?: (type: DocumentType, file: File) => Promise<void>
  onDelete?: (documentId: string) => Promise<void>
  onVerify?: (documentId: string) => Promise<void>
  onReupload?: (documentId: string, file: File) => Promise<void>
  onView?: (document: EmployeeDocument) => void
  onDownload?: (document: EmployeeDocument) => void
  readOnly?: boolean
  accept?: string
  maxSize?: number
}

// ============================================================================
// Helper Functions
// ============================================================================

const documentTypeLabels: Record<DocumentType, string> = {
  pan_card: 'PAN Card',
  aadhaar_card: 'Aadhaar Card',
  passport: 'Passport',
  driving_license: 'Driving License',
  offer_letter: 'Offer Letter',
  appointment_letter: 'Appointment Letter',
  relieving_letter: 'Relieving Letter',
  payslip: 'Payslip',
  form16: 'Form 16',
  education_certificate: 'Education Certificate',
  other: 'Other Document'
}

const getFileIcon = (type: string) => {
  if (type.includes('image')) return <Image className="h-5 w-5" />
  if (type.includes('pdf')) return <FileText className="h-5 w-5" />
  return <File className="h-5 w-5" />
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// ============================================================================
// Single Document Upload Component
// ============================================================================

function SingleDocumentUpload({
  type,
  label,
  document,
  required = false,
  onUpload,
  onDelete,
  onVerify,
  onReupload,
  onView,
  onDownload,
  readOnly = false,
  accept = '.pdf,.jpg,.jpeg,.png',
  maxSize = 5
}: SingleDocumentUploadProps) {
  const inputRef = React.useRef<HTMLInputElement>(null)
  const [isUploading, setIsUploading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file size
    if (file.size > maxSize * 1024 * 1024) {
      setError(`File size exceeds ${maxSize}MB limit`)
      return
    }

    setError(null)
    setIsUploading(true)

    try {
      if (document) {
        await onReupload?.(document.id, file)
      } else {
        await onUpload?.(type, file)
      }
    } catch (err) {
      setError('Failed to upload document')
    } finally {
      setIsUploading(false)
      if (inputRef.current) {
        inputRef.current.value = ''
      }
    }
  }

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={cn(
            'w-10 h-10 rounded flex items-center justify-center',
            document ? 'bg-green-100 text-green-600' : 'bg-muted text-muted-foreground'
          )}>
            {document ? <FileText className="h-5 w-5" /> : <Upload className="h-5 w-5" />}
          </div>
          <div>
            <p className="font-medium">
              {label}
              {required && <span className="text-destructive ml-1">*</span>}
            </p>
            {document ? (
              <div className="text-sm text-muted-foreground mt-1">
                <p>{document.name}</p>
                <p>Uploaded {formatDate(document.uploaded_at, { format: 'long' })}</p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground mt-1">
                {required ? 'Required document' : 'Optional document'}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          {document && (
            <>
              {document.verified ? (
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Verified
                </Badge>
              ) : (
                <Badge className="bg-yellow-100 text-yellow-800">
                  <Clock className="h-3 w-3 mr-1" />
                  Pending
                </Badge>
              )}
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-2 flex items-center gap-1 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      <div className="mt-3 flex items-center gap-2">
        {document ? (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onView?.(document)}
            >
              <Eye className="h-4 w-4 mr-1" />
              View
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDownload?.(document)}
            >
              <Download className="h-4 w-4 mr-1" />
              Download
            </Button>
            {!readOnly && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => inputRef.current?.click()}
                  disabled={isUploading}
                >
                  <RefreshCw className={cn('h-4 w-4 mr-1', isUploading && 'animate-spin')} />
                  Replace
                </Button>
                {!document.verified && onVerify && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onVerify(document.id)}
                  >
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Verify
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete?.(document.id)}
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </>
            )}
          </>
        ) : (
          !readOnly && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => inputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-1" />
                  Upload Document
                </>
              )}
            </Button>
          )
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  )
}

// ============================================================================
// Document Category Component
// ============================================================================

function DocumentCategory({
  title,
  description,
  documents,
  documentTypes,
  onUpload,
  onDelete,
  onVerify,
  onReupload,
  onView,
  onDownload,
  readOnly
}: DocumentCategoryProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <h3 className="font-semibold mb-1">{title}</h3>
        {description && (
          <p className="text-sm text-muted-foreground mb-4">{description}</p>
        )}
        <div className="grid gap-4 md:grid-cols-2">
          {documentTypes.map(({ type, label, required }) => (
            <SingleDocumentUpload
              key={type}
              type={type}
              label={label}
              document={documents.find(d => d.type === type)}
              required={required}
              onUpload={onUpload}
              onDelete={onDelete}
              onVerify={onVerify}
              onReupload={onReupload}
              onView={onView}
              onDownload={onDownload}
              readOnly={readOnly}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Main Document Upload Component
// ============================================================================

export function DocumentUpload({
  documents = [],
  onUpload,
  onDelete,
  onVerify,
  onReupload,
  onView,
  onDownload,
  employeeId,
  readOnly = false,
  requiredDocuments = ['pan_card', 'aadhaar_card'],
  className
}: DocumentUploadProps) {
  const identityDocuments = [
    { type: 'aadhaar_card' as DocumentType, label: 'Aadhaar Card', required: requiredDocuments.includes('aadhaar_card') },
    { type: 'pan_card' as DocumentType, label: 'PAN Card', required: requiredDocuments.includes('pan_card') },
    { type: 'passport' as DocumentType, label: 'Passport', required: false },
    { type: 'driving_license' as DocumentType, label: 'Driving License', required: false }
  ]

  const employmentDocuments = [
    { type: 'offer_letter' as DocumentType, label: 'Offer Letter', required: requiredDocuments.includes('offer_letter') },
    { type: 'appointment_letter' as DocumentType, label: 'Appointment Letter', required: false },
    { type: 'relieving_letter' as DocumentType, label: 'Relieving Letter (Previous)', required: false }
  ]

  const educationDocuments = [
    { type: 'education_certificate' as DocumentType, label: 'Highest Education Certificate', required: false }
  ]

  const taxDocuments = [
    { type: 'form16' as DocumentType, label: 'Form 16', required: false },
    { type: 'payslip' as DocumentType, label: 'Previous Payslips', required: false }
  ]

  // Summary stats
  const totalRequired = requiredDocuments.length
  const uploadedRequired = documents.filter(d => requiredDocuments.includes(d.type)).length
  const verifiedCount = documents.filter(d => d.verified).length
  const pendingCount = documents.filter(d => !d.verified).length

  return (
    <div className={cn('space-y-6', className)}>
      {/* Summary */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Documents</p>
              <p className="text-2xl font-bold">{documents.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Required</p>
              <p className="text-2xl font-bold">
                <span className={uploadedRequired === totalRequired ? 'text-green-600' : 'text-yellow-600'}>
                  {uploadedRequired}
                </span>
                <span className="text-muted-foreground">/{totalRequired}</span>
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Verified</p>
              <p className="text-2xl font-bold text-green-600">{verifiedCount}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending Verification</p>
              <p className="text-2xl font-bold text-yellow-600">{pendingCount}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document Categories */}
      <DocumentCategory
        title="Identity Documents"
        description="Government-issued identification documents"
        documents={documents}
        documentTypes={identityDocuments}
        onUpload={onUpload}
        onDelete={onDelete}
        onVerify={onVerify}
        onReupload={onReupload}
        onView={onView}
        onDownload={onDownload}
        readOnly={readOnly}
      />

      <DocumentCategory
        title="Employment Documents"
        description="Offer letters, appointment letters, and previous employment records"
        documents={documents}
        documentTypes={employmentDocuments}
        onUpload={onUpload}
        onDelete={onDelete}
        onVerify={onVerify}
        onReupload={onReupload}
        onView={onView}
        onDownload={onDownload}
        readOnly={readOnly}
      />

      <DocumentCategory
        title="Education Documents"
        description="Educational qualifications and certificates"
        documents={documents}
        documentTypes={educationDocuments}
        onUpload={onUpload}
        onDelete={onDelete}
        onVerify={onVerify}
        onReupload={onReupload}
        onView={onView}
        onDownload={onDownload}
        readOnly={readOnly}
      />

      <DocumentCategory
        title="Tax Documents"
        description="Tax-related documents from previous employment"
        documents={documents}
        documentTypes={taxDocuments}
        onUpload={onUpload}
        onDelete={onDelete}
        onVerify={onVerify}
        onReupload={onReupload}
        onView={onView}
        onDownload={onDownload}
        readOnly={readOnly}
      />
    </div>
  )
}

// ============================================================================
// Document List Component (Simple list view)
// ============================================================================

interface DocumentListProps {
  documents: EmployeeDocument[]
  onView?: (document: EmployeeDocument) => void
  onDownload?: (document: EmployeeDocument) => void
  showVerificationStatus?: boolean
  className?: string
}

export function DocumentList({
  documents,
  onView,
  onDownload,
  showVerificationStatus = true,
  className
}: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className={cn('text-center py-8 text-muted-foreground', className)}>
        No documents uploaded
      </div>
    )
  }

  return (
    <div className={cn('space-y-2', className)}>
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-3 border rounded-lg"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-muted rounded flex items-center justify-center">
              <FileText className="h-4 w-4 text-muted-foreground" />
            </div>
            <div>
              <p className="font-medium text-sm">{doc.name}</p>
              <p className="text-xs text-muted-foreground">
                {documentTypeLabels[doc.type]} - {formatDate(doc.uploaded_at, { format: 'long' })}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {showVerificationStatus && (
              doc.verified ? (
                <Badge className="bg-green-100 text-green-800 text-xs">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Verified
                </Badge>
              ) : (
                <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                  <Clock className="h-3 w-3 mr-1" />
                  Pending
                </Badge>
              )
            )}
            <Button variant="ghost" size="icon" onClick={() => onView?.(doc)}>
              <Eye className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => onDownload?.(doc)}>
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default DocumentUpload

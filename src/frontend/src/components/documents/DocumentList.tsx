'use client';

import { useState } from 'react';
import {
  FileText, FileImage, FileSpreadsheet, File, Download, Eye, Share2,
  MoreVertical, Trash2, Edit, Clock, User
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Document {
  id: string;
  name: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
  category: string;
  documentType: string;
  version: number;
  isConfidential: boolean;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

interface DocumentListProps {
  documents: Document[];
  viewMode: 'list' | 'grid';
  onView: (doc: Document) => void;
  onDownload: (doc: Document) => void;
  onShare: (doc: Document) => void;
  onDelete: (doc: Document) => void;
  onEdit: (doc: Document) => void;
}

function getFileIcon(mimeType: string) {
  if (mimeType.includes('image')) return FileImage;
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return FileSpreadsheet;
  if (mimeType.includes('pdf') || mimeType.includes('document')) return FileText;
  return File;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function DocumentCard({ doc, onView, onDownload, onShare, onDelete, onEdit }: {
  doc: Document;
  onView: () => void;
  onDownload: () => void;
  onShare: () => void;
  onDelete: () => void;
  onEdit: () => void;
}) {
  const Icon = getFileIcon(doc.mimeType);

  return (
    <div className="group border rounded-lg p-4 hover:shadow-md transition-shadow bg-card">
      <div className="flex items-start justify-between mb-3">
        <div className="p-2 bg-primary/10 rounded-lg">
          <Icon className="h-8 w-8 text-primary" />
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={onView}>
              <Eye className="h-4 w-4 mr-2" /> View
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onDownload}>
              <Download className="h-4 w-4 mr-2" /> Download
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onShare}>
              <Share2 className="h-4 w-4 mr-2" /> Share
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onEdit}>
              <Edit className="h-4 w-4 mr-2" /> Edit
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={onDelete} className="text-destructive">
              <Trash2 className="h-4 w-4 mr-2" /> Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <h3 className="font-medium text-sm truncate mb-1" title={doc.name}>
        {doc.name}
      </h3>
      <p className="text-xs text-muted-foreground truncate mb-2">{doc.fileName}</p>

      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="secondary" className="text-xs">
          {doc.category}
        </Badge>
        {doc.isConfidential && (
          <Badge variant="destructive" className="text-xs">
            Confidential
          </Badge>
        )}
        {doc.version > 1 && (
          <Badge variant="outline" className="text-xs">
            v{doc.version}
          </Badge>
        )}
      </div>

      <div className="mt-3 pt-3 border-t flex items-center justify-between text-xs text-muted-foreground">
        <span>{formatFileSize(doc.fileSize)}</span>
        <span>{formatDate(doc.updatedAt)}</span>
      </div>
    </div>
  );
}

function DocumentRow({ doc, onView, onDownload, onShare, onDelete, onEdit }: {
  doc: Document;
  onView: () => void;
  onDownload: () => void;
  onShare: () => void;
  onDelete: () => void;
  onEdit: () => void;
}) {
  const Icon = getFileIcon(doc.mimeType);

  return (
    <div className="group flex items-center gap-4 p-3 border-b hover:bg-muted/50 transition-colors">
      <div className="p-2 bg-primary/10 rounded">
        <Icon className="h-5 w-5 text-primary" />
      </div>

      <div className="flex-1 min-w-0">
        <h3 className="font-medium text-sm truncate">{doc.name}</h3>
        <p className="text-xs text-muted-foreground truncate">{doc.fileName}</p>
      </div>

      <div className="hidden md:flex items-center gap-2">
        <Badge variant="secondary" className="text-xs">
          {doc.category}
        </Badge>
        {doc.isConfidential && (
          <Badge variant="destructive" className="text-xs">
            Confidential
          </Badge>
        )}
      </div>

      <div className="hidden lg:block text-sm text-muted-foreground w-20">
        {formatFileSize(doc.fileSize)}
      </div>

      <div className="hidden lg:block text-sm text-muted-foreground w-24">
        {formatDate(doc.updatedAt)}
      </div>

      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onView}>
          <Eye className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onDownload}>
          <Download className="h-4 w-4" />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={onShare}>
              <Share2 className="h-4 w-4 mr-2" /> Share
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onEdit}>
              <Edit className="h-4 w-4 mr-2" /> Edit
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={onDelete} className="text-destructive">
              <Trash2 className="h-4 w-4 mr-2" /> Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}

export function DocumentList({
  documents,
  viewMode,
  onView,
  onDownload,
  onShare,
  onDelete,
  onEdit,
}: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FileText className="h-12 w-12 text-muted-foreground/50 mb-4" />
        <h3 className="font-medium text-lg mb-1">No documents</h3>
        <p className="text-sm text-muted-foreground">
          Upload documents to get started
        </p>
      </div>
    );
  }

  if (viewMode === 'grid') {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {documents.map((doc) => (
          <DocumentCard
            key={doc.id}
            doc={doc}
            onView={() => onView(doc)}
            onDownload={() => onDownload(doc)}
            onShare={() => onShare(doc)}
            onDelete={() => onDelete(doc)}
            onEdit={() => onEdit(doc)}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="hidden md:flex items-center gap-4 p-3 bg-muted/50 border-b text-xs font-medium text-muted-foreground">
        <div className="w-10" />
        <div className="flex-1">Name</div>
        <div className="w-32">Category</div>
        <div className="hidden lg:block w-20">Size</div>
        <div className="hidden lg:block w-24">Modified</div>
        <div className="w-28">Actions</div>
      </div>
      {documents.map((doc) => (
        <DocumentRow
          key={doc.id}
          doc={doc}
          onView={() => onView(doc)}
          onDownload={() => onDownload(doc)}
          onShare={() => onShare(doc)}
          onDelete={() => onDelete(doc)}
          onEdit={() => onEdit(doc)}
        />
      ))}
    </div>
  );
}

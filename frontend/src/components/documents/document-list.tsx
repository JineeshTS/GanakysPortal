'use client';

/**
 * Document List Component
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { Document } from '@/types/documents';

interface DocumentListProps {
  documents: Document[];
  isLoading?: boolean;
  onDocumentClick?: (document: Document) => void;
  onDownload?: (document: Document) => void;
  onDelete?: (document: Document) => void;
  onEdit?: (document: Document) => void;
  selectedIds?: string[];
  onSelectionChange?: (ids: string[]) => void;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function getFileIcon(extension: string): React.ReactNode {
  const iconClass = 'h-8 w-8';
  const ext = extension.toLowerCase();

  if (['pdf'].includes(ext)) {
    return (
      <svg className={cn(iconClass, 'text-red-500')} fill="currentColor" viewBox="0 0 24 24">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM8.5 13H10v5H8.5v-2h-1v2H6v-5h1.5v1.5h1V13zm4 0c.55 0 1 .45 1 1v3c0 .55-.45 1-1 1h-2v-5h2zm-.5 1.5v2h.5v-2h-.5zm4.5-1.5h2v1h-1.5v1h1v1h-1v2H16v-5z" />
      </svg>
    );
  }

  if (['doc', 'docx'].includes(ext)) {
    return (
      <svg className={cn(iconClass, 'text-blue-500')} fill="currentColor" viewBox="0 0 24 24">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm4 18H6V4h7v5h5v11zM9.5 13v5H8v-5h1.5zm2.5 0c.55 0 1 .45 1 1v3c0 .55-.45 1-1 1h-1.5v-5H12zm-.5 1.5v2h.5v-2h-.5zm4.5-1.5h1.5v5H16v-1.5h-1v-1h1v-1h-1V13h1.5z" />
      </svg>
    );
  }

  if (['xls', 'xlsx'].includes(ext)) {
    return (
      <svg className={cn(iconClass, 'text-green-500')} fill="currentColor" viewBox="0 0 24 24">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 13h2l1 2 1-2h2l-2 2.5L14 18h-2l-1-2-1 2H8l2-2.5L8 13z" />
      </svg>
    );
  }

  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) {
    return (
      <svg className={cn(iconClass, 'text-purple-500')} fill="currentColor" viewBox="0 0 24 24">
        <path d="M21 19V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z" />
      </svg>
    );
  }

  // Default file icon
  return (
    <svg className={cn(iconClass, 'text-gray-400')} fill="currentColor" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm4 18H6V4h7v5h5v11z" />
    </svg>
  );
}

export function DocumentList({
  documents,
  isLoading,
  onDocumentClick,
  onDownload,
  onDelete,
  onEdit,
  selectedIds = [],
  onSelectionChange,
}: DocumentListProps) {
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  const isSelected = (id: string) => selectedIds.includes(id);

  const toggleSelection = (id: string) => {
    if (!onSelectionChange) return;
    if (isSelected(id)) {
      onSelectionChange(selectedIds.filter((s) => s !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  const toggleAllSelection = () => {
    if (!onSelectionChange) return;
    if (selectedIds.length === documents.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(documents.map((d) => d.id));
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading documents...</p>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <svg
          className="h-12 w-12 text-muted-foreground/50"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
          />
        </svg>
        <h3 className="mt-4 text-lg font-medium">No documents</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Upload documents to this folder to get started.
        </p>
      </div>
    );
  }

  if (viewMode === 'grid') {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className={cn(
              'group relative flex flex-col items-center rounded-lg border p-4 hover:bg-muted/50 cursor-pointer transition-colors',
              isSelected(doc.id) && 'ring-2 ring-primary'
            )}
            onClick={() => onDocumentClick?.(doc)}
          >
            {onSelectionChange && (
              <div
                className="absolute top-2 left-2"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleSelection(doc.id);
                }}
              >
                <Checkbox checked={isSelected(doc.id)} />
              </div>
            )}
            {getFileIcon(doc.extension)}
            <p className="mt-2 text-sm font-medium text-center truncate w-full">
              {doc.name}
            </p>
            <p className="text-xs text-muted-foreground">{formatFileSize(doc.file_size)}</p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <table className="w-full">
        <thead className="bg-muted/50">
          <tr>
            {onSelectionChange && (
              <th className="w-10 px-4 py-3">
                <Checkbox
                  checked={selectedIds.length === documents.length}
                  onCheckedChange={toggleAllSelection}
                />
              </th>
            )}
            <th className="text-left px-4 py-3 text-sm font-medium">Name</th>
            <th className="text-left px-4 py-3 text-sm font-medium hidden md:table-cell">Size</th>
            <th className="text-left px-4 py-3 text-sm font-medium hidden lg:table-cell">
              Modified
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium hidden xl:table-cell">
              Uploaded By
            </th>
            <th className="w-10 px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr
              key={doc.id}
              className={cn(
                'border-t hover:bg-muted/30 cursor-pointer transition-colors',
                isSelected(doc.id) && 'bg-primary/5'
              )}
              onClick={() => onDocumentClick?.(doc)}
            >
              {onSelectionChange && (
                <td className="px-4 py-3">
                  <div onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={isSelected(doc.id)}
                      onCheckedChange={() => toggleSelection(doc.id)}
                    />
                  </div>
                </td>
              )}
              <td className="px-4 py-3">
                <div className="flex items-center gap-3">
                  {getFileIcon(doc.extension)}
                  <div className="min-w-0">
                    <p className="font-medium truncate">{doc.name}</p>
                    {doc.tags && doc.tags.length > 0 && (
                      <div className="flex gap-1 mt-1">
                        {doc.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="text-xs bg-muted px-1.5 py-0.5 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground hidden md:table-cell">
                {formatFileSize(doc.file_size)}
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground hidden lg:table-cell">
                {formatDate(doc.updated_at)}
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground hidden xl:table-cell">
                {doc.uploaded_by_name || 'Unknown'}
              </td>
              <td className="px-4 py-3">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                        />
                      </svg>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    {onDownload && (
                      <DropdownMenuItem onClick={() => onDownload(doc)}>
                        <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download
                      </DropdownMenuItem>
                    )}
                    {onEdit && (
                      <DropdownMenuItem onClick={() => onEdit(doc)}>
                        <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Edit
                      </DropdownMenuItem>
                    )}
                    {onDelete && (
                      <DropdownMenuItem
                        onClick={() => onDelete(doc)}
                        className="text-destructive"
                      >
                        <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                      </DropdownMenuItem>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DocumentList;

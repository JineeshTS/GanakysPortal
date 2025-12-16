'use client';

/**
 * Folder Tree Component for EDMS
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { Folder } from '@/types/documents';

interface FolderTreeProps {
  folders: Folder[];
  selectedFolderId?: string;
  onSelectFolder: (folder: Folder) => void;
  onCreateFolder?: (parentId: string | null) => void;
}

interface FolderNodeProps {
  folder: Folder;
  level: number;
  selectedId?: string;
  onSelect: (folder: Folder) => void;
  onCreateFolder?: (parentId: string) => void;
}

function FolderNode({ folder, level, selectedId, onSelect, onCreateFolder }: FolderNodeProps) {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const hasChildren = folder.children && folder.children.length > 0;
  const isSelected = folder.id === selectedId;

  return (
    <div>
      <div
        className={cn(
          'group flex items-center gap-1 rounded-md px-2 py-1.5 text-sm cursor-pointer transition-colors',
          isSelected
            ? 'bg-primary text-primary-foreground'
            : 'hover:bg-muted text-foreground'
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => onSelect(folder)}
      >
        {/* Expand/Collapse button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsExpanded(!isExpanded);
          }}
          className={cn(
            'h-4 w-4 flex items-center justify-center rounded hover:bg-black/10 dark:hover:bg-white/10',
            !hasChildren && 'invisible'
          )}
        >
          <svg
            className={cn(
              'h-3 w-3 transition-transform',
              isExpanded && 'rotate-90'
            )}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>

        {/* Folder icon */}
        <svg
          className={cn(
            'h-4 w-4 flex-shrink-0',
            isSelected ? 'text-primary-foreground' : 'text-yellow-500'
          )}
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          {isExpanded ? (
            <path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h6l2 2h6a2 2 0 012 2v10a2 2 0 01-2 2z" />
          ) : (
            <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          )}
        </svg>

        {/* Folder name */}
        <span className="flex-1 truncate">{folder.name}</span>

        {/* Document count */}
        {folder.document_count !== undefined && folder.document_count > 0 && (
          <span
            className={cn(
              'text-xs px-1.5 py-0.5 rounded-full',
              isSelected
                ? 'bg-primary-foreground/20 text-primary-foreground'
                : 'bg-muted text-muted-foreground'
            )}
          >
            {folder.document_count}
          </span>
        )}

        {/* Add subfolder button */}
        {onCreateFolder && !folder.is_system && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onCreateFolder(folder.id);
            }}
            className={cn(
              'h-5 w-5 flex items-center justify-center rounded opacity-0 group-hover:opacity-100 transition-opacity',
              isSelected
                ? 'hover:bg-primary-foreground/20'
                : 'hover:bg-muted'
            )}
            title="Add subfolder"
          >
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        )}
      </div>

      {/* Children */}
      {isExpanded && hasChildren && (
        <div>
          {folder.children!.map((child) => (
            <FolderNode
              key={child.id}
              folder={child}
              level={level + 1}
              selectedId={selectedId}
              onSelect={onSelect}
              onCreateFolder={onCreateFolder}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function FolderTree({
  folders,
  selectedFolderId,
  onSelectFolder,
  onCreateFolder,
}: FolderTreeProps) {
  return (
    <div className="py-2">
      {/* Root folder option */}
      <div
        className={cn(
          'flex items-center gap-2 rounded-md px-2 py-1.5 text-sm cursor-pointer transition-colors mb-1',
          !selectedFolderId
            ? 'bg-primary text-primary-foreground'
            : 'hover:bg-muted text-foreground'
        )}
        onClick={() =>
          onSelectFolder({ id: '', name: 'All Documents', path: '/', depth: 0 } as Folder)
        }
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
          />
        </svg>
        <span>All Documents</span>
      </div>

      {/* Folder tree */}
      {folders.map((folder) => (
        <FolderNode
          key={folder.id}
          folder={folder}
          level={0}
          selectedId={selectedFolderId}
          onSelect={onSelectFolder}
          onCreateFolder={onCreateFolder}
        />
      ))}

      {/* Create root folder button */}
      {onCreateFolder && (
        <button
          onClick={() => onCreateFolder(null)}
          className="flex items-center gap-2 w-full rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors mt-2"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>New Folder</span>
        </button>
      )}
    </div>
  );
}

export default FolderTree;

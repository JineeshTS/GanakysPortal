'use client';

import { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, FolderOpen, Plus, MoreVertical } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface FolderNode {
  id: string;
  name: string;
  path: string;
  level: number;
  children?: FolderNode[];
  documentCount?: number;
  isSystem?: boolean;
}

interface FolderTreeProps {
  folders: FolderNode[];
  selectedFolderId?: string;
  onSelectFolder: (folder: FolderNode) => void;
  onCreateFolder?: (parentId: string | null) => void;
}

function FolderItem({
  folder,
  selectedId,
  onSelect,
  onCreateFolder,
  level = 0,
}: {
  folder: FolderNode;
  selectedId?: string;
  onSelect: (folder: FolderNode) => void;
  onCreateFolder?: (parentId: string) => void;
  level?: number;
}) {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const hasChildren = folder.children && folder.children.length > 0;
  const isSelected = folder.id === selectedId;

  return (
    <div>
      <div
        className={cn(
          'flex items-center gap-1 py-1.5 px-2 rounded-md cursor-pointer group',
          'hover:bg-muted/50 transition-colors',
          isSelected && 'bg-primary/10 text-primary'
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => onSelect(folder)}
      >
        <button
          className="p-0.5 hover:bg-muted rounded"
          onClick={(e) => {
            e.stopPropagation();
            setIsExpanded(!isExpanded);
          }}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )
          ) : (
            <span className="w-4" />
          )}
        </button>

        {isExpanded ? (
          <FolderOpen className="h-4 w-4 text-yellow-500" />
        ) : (
          <Folder className="h-4 w-4 text-yellow-500" />
        )}

        <span className="flex-1 text-sm truncate">{folder.name}</span>

        {folder.documentCount !== undefined && folder.documentCount > 0 && (
          <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
            {folder.documentCount}
          </span>
        )}

        {onCreateFolder && !folder.isSystem && (
          <button
            className="p-1 hover:bg-muted rounded opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => {
              e.stopPropagation();
              onCreateFolder(folder.id);
            }}
          >
            <Plus className="h-3 w-3" />
          </button>
        )}
      </div>

      {hasChildren && isExpanded && (
        <div>
          {folder.children!.map((child) => (
            <FolderItem
              key={child.id}
              folder={child}
              selectedId={selectedId}
              onSelect={onSelect}
              onCreateFolder={onCreateFolder}
              level={level + 1}
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
      <div className="flex items-center justify-between px-3 mb-2">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Folders
        </span>
        {onCreateFolder && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2"
            onClick={() => onCreateFolder(null)}
          >
            <Plus className="h-3 w-3 mr-1" />
            New
          </Button>
        )}
      </div>

      <div className="space-y-0.5">
        {folders.map((folder) => (
          <FolderItem
            key={folder.id}
            folder={folder}
            selectedId={selectedFolderId}
            onSelect={onSelectFolder}
            onCreateFolder={onCreateFolder}
          />
        ))}
      </div>
    </div>
  );
}

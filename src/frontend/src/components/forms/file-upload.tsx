"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Upload, X, File, Image, FileText, AlertCircle } from "lucide-react"

// ============================================================================
// File Upload Component
// ============================================================================

interface FileUploadProps {
  label: string
  name: string
  accept?: string
  multiple?: boolean
  maxSize?: number // in MB
  maxFiles?: number
  value?: File[]
  onChange?: (files: File[]) => void
  onError?: (error: string) => void
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  className?: string
  containerClassName?: string
}

export function FileUpload({
  label,
  name,
  accept,
  multiple = false,
  maxSize = 5, // 5MB default
  maxFiles = 5,
  value = [],
  onChange,
  onError,
  error,
  hint,
  required,
  disabled,
  className,
  containerClassName
}: FileUploadProps) {
  const inputRef = React.useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = React.useState(false)

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return

    const files = Array.from(fileList)
    const validFiles: File[] = []
    const errors: string[] = []

    files.forEach((file) => {
      // Check file size
      if (file.size > maxSize * 1024 * 1024) {
        errors.push(`${file.name} exceeds ${maxSize}MB limit`)
        return
      }

      // Check file type if accept is specified
      if (accept) {
        const acceptedTypes = accept.split(',').map((t) => t.trim())
        const isAccepted = acceptedTypes.some((type) => {
          if (type.startsWith('.')) {
            return file.name.toLowerCase().endsWith(type.toLowerCase())
          }
          if (type.endsWith('/*')) {
            return file.type.startsWith(type.replace('/*', ''))
          }
          return file.type === type
        })

        if (!isAccepted) {
          errors.push(`${file.name} is not an accepted file type`)
          return
        }
      }

      validFiles.push(file)
    })

    // Check max files
    const totalFiles = value.length + validFiles.length
    if (multiple && totalFiles > maxFiles) {
      errors.push(`Maximum ${maxFiles} files allowed`)
      validFiles.splice(maxFiles - value.length)
    }

    if (errors.length > 0) {
      onError?.(errors.join('. '))
    }

    if (validFiles.length > 0) {
      if (multiple) {
        onChange?.([...value, ...validFiles])
      } else {
        onChange?.(validFiles.slice(0, 1))
      }
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (!disabled) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
    // Reset input to allow selecting same file again
    e.target.value = ''
  }

  const removeFile = (index: number) => {
    const newFiles = [...value]
    newFiles.splice(index, 1)
    onChange?.(newFiles)
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="h-4 w-4" />
    }
    if (file.type === 'application/pdf') {
      return <FileText className="h-4 w-4" />
    }
    return <File className="h-4 w-4" />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className={cn("space-y-2", containerClassName)}>
      <Label className="flex items-center gap-1">
        {label}
        {required && <span className="text-destructive">*</span>}
      </Label>

      {/* Drop Zone */}
      <div
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center transition-colors",
          dragActive && "border-primary bg-primary/5",
          !dragActive && "border-input hover:border-muted-foreground/50",
          disabled && "opacity-50 cursor-not-allowed",
          error && "border-destructive",
          className
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          name={name}
          accept={accept}
          multiple={multiple}
          onChange={handleInputChange}
          disabled={disabled}
          className="hidden"
        />

        <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
        <p className="text-sm text-muted-foreground mb-2">
          Drag and drop files here, or
        </p>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={() => inputRef.current?.click()}
          disabled={disabled}
        >
          Browse Files
        </Button>
        <p className="text-xs text-muted-foreground mt-2">
          {accept ? `Accepted: ${accept}` : 'All file types accepted'}
          {' • '}Max size: {maxSize}MB
          {multiple && ` • Max ${maxFiles} files`}
        </p>
      </div>

      {/* File List */}
      {value.length > 0 && (
        <ul className="space-y-2">
          {value.map((file, index) => (
            <li
              key={`${file.name}-${index}`}
              className="flex items-center gap-2 p-2 rounded-md bg-muted"
            >
              {getFileIcon(file)}
              <span className="flex-1 text-sm truncate">{file.name}</span>
              <span className="text-xs text-muted-foreground">
                {formatFileSize(file.size)}
              </span>
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="p-1 hover:bg-background rounded-md"
                disabled={disabled}
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Remove file</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {error && (
        <p className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
      {hint && !error && (
        <p className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}
    </div>
  )
}

export default FileUpload

"use client"

import * as React from "react"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import { FormSelect } from "@/components/forms/form-field"
import { ConfigFormRow } from "@/components/settings/ConfigForm"
import { useApi } from "@/hooks/use-api"
import {
  FolderOpen,
  FileText,
  Plus,
  Search,
  Edit,
  Trash2,
  Loader2,
  Tag,
  Palette,
  AlertCircle
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface Category {
  id: string
  code: string
  name: string
  description: string | null
  color: string
  icon: string | null
  sort_order: number
  is_system: boolean
  is_active: boolean
}

interface DocumentType {
  id: string
  code: string
  name: string
  description: string | null
  category_id: string
  sort_order: number
  is_system: boolean
  is_active: boolean
  category_code: string | null
  category_name: string | null
}

// ============================================================================
// Color Options
// ============================================================================

const COLOR_OPTIONS = [
  { value: '#3B82F6', label: 'Blue' },
  { value: '#8B5CF6', label: 'Purple' },
  { value: '#10B981', label: 'Green' },
  { value: '#F59E0B', label: 'Amber' },
  { value: '#EF4444', label: 'Red' },
  { value: '#06B6D4', label: 'Cyan' },
  { value: '#EC4899', label: 'Pink' },
  { value: '#6366F1', label: 'Indigo' },
  { value: '#6B7280', label: 'Gray' },
]

// ============================================================================
// Document Settings Page
// ============================================================================

export default function DocumentSettingsPage() {
  const api = useApi()

  // State
  const [categories, setCategories] = React.useState<Category[]>([])
  const [types, setTypes] = React.useState<DocumentType[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  // Dialog state
  const [isCategoryDialogOpen, setIsCategoryDialogOpen] = React.useState(false)
  const [isTypeDialogOpen, setIsTypeDialogOpen] = React.useState(false)
  const [editingCategory, setEditingCategory] = React.useState<Category | null>(null)
  const [editingType, setEditingType] = React.useState<DocumentType | null>(null)
  const [isSaving, setIsSaving] = React.useState(false)

  // Search/filter state
  const [categorySearch, setCategorySearch] = React.useState('')
  const [typeSearch, setTypeSearch] = React.useState('')
  const [selectedCategoryFilter, setSelectedCategoryFilter] = React.useState<string>('all')

  // Form state
  const [categoryForm, setCategoryForm] = React.useState({
    code: '',
    name: '',
    description: '',
    color: '#3B82F6'
  })
  const [typeForm, setTypeForm] = React.useState({
    code: '',
    name: '',
    description: '',
    category_id: ''
  })

  // Fetch data
  React.useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [categoriesRes, typesRes] = await Promise.all([
        api.get('/documents/settings/categories?active_only=false'),
        api.get('/documents/settings/types?active_only=false')
      ])
      setCategories(categoriesRes.data)
      setTypes(typesRes.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load document settings')
    } finally {
      setLoading(false)
    }
  }

  // Filter data
  const filteredCategories = categories.filter(cat =>
    cat.name.toLowerCase().includes(categorySearch.toLowerCase()) ||
    cat.code.toLowerCase().includes(categorySearch.toLowerCase())
  )

  const filteredTypes = types.filter(type => {
    const matchesSearch = type.name.toLowerCase().includes(typeSearch.toLowerCase()) ||
      type.code.toLowerCase().includes(typeSearch.toLowerCase())
    const matchesCategory = selectedCategoryFilter === 'all' || type.category_id === selectedCategoryFilter
    return matchesSearch && matchesCategory
  })

  // Category handlers
  const handleAddCategory = () => {
    setEditingCategory(null)
    setCategoryForm({ code: '', name: '', description: '', color: '#3B82F6' })
    setIsCategoryDialogOpen(true)
  }

  const handleEditCategory = (category: Category) => {
    setEditingCategory(category)
    setCategoryForm({
      code: category.code,
      name: category.name,
      description: category.description || '',
      color: category.color || '#3B82F6'
    })
    setIsCategoryDialogOpen(true)
  }

  const handleSaveCategory = async () => {
    setIsSaving(true)
    try {
      if (editingCategory) {
        await api.put(`/documents/settings/categories/${editingCategory.id}`, {
          name: categoryForm.name,
          description: categoryForm.description || null,
          color: categoryForm.color
        })
      } else {
        await api.post('/documents/settings/categories', categoryForm)
      }
      await fetchData()
      setIsCategoryDialogOpen(false)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save category')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteCategory = async (category: Category) => {
    if (!confirm(`Are you sure you want to delete "${category.name}"?`)) return
    try {
      await api.delete(`/documents/settings/categories/${category.id}`)
      await fetchData()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete category')
    }
  }

  // Type handlers
  const handleAddType = () => {
    setEditingType(null)
    setTypeForm({ code: '', name: '', description: '', category_id: categories[0]?.id || '' })
    setIsTypeDialogOpen(true)
  }

  const handleEditType = (type: DocumentType) => {
    setEditingType(type)
    setTypeForm({
      code: type.code,
      name: type.name,
      description: type.description || '',
      category_id: type.category_id
    })
    setIsTypeDialogOpen(true)
  }

  const handleSaveType = async () => {
    setIsSaving(true)
    try {
      if (editingType) {
        await api.put(`/documents/settings/types/${editingType.id}`, {
          name: typeForm.name,
          description: typeForm.description || null,
          category_id: typeForm.category_id
        })
      } else {
        await api.post('/documents/settings/types', typeForm)
      }
      await fetchData()
      setIsTypeDialogOpen(false)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save document type')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteType = async (type: DocumentType) => {
    if (!confirm(`Are you sure you want to delete "${type.name}"?`)) return
    try {
      await api.delete(`/documents/settings/types/${type.id}`)
      await fetchData()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete document type')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Document Settings"
        description="Manage document categories and types for organizing your documents"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "Documents" }
        ]}
      />

      {error && (
        <Card className="border-destructive">
          <CardContent className="py-4 flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" />
            {error}
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="categories" className="space-y-6">
        <TabsList>
          <TabsTrigger value="categories">
            <FolderOpen className="h-4 w-4 mr-2" />
            Categories ({categories.length})
          </TabsTrigger>
          <TabsTrigger value="types">
            <FileText className="h-4 w-4 mr-2" />
            Document Types ({types.length})
          </TabsTrigger>
        </TabsList>

        {/* Categories Tab */}
        <TabsContent value="categories" className="space-y-4">
          <Card>
            <CardContent className="py-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-between">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search categories..."
                    value={categorySearch}
                    onChange={(e) => setCategorySearch(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Button onClick={handleAddCategory}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Category
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredCategories.map(category => (
              <Card key={category.id} className={!category.is_active ? 'opacity-60' : ''}>
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div
                        className="h-10 w-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: category.color + '20' }}
                      >
                        <FolderOpen className="h-5 w-5" style={{ color: category.color }} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{category.name}</h3>
                          {category.is_system && (
                            <Badge variant="secondary" className="text-xs">System</Badge>
                          )}
                          {!category.is_active && (
                            <Badge variant="outline" className="text-xs">Inactive</Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">{category.code}</p>
                        {category.description && (
                          <p className="text-sm text-muted-foreground mt-1">{category.description}</p>
                        )}
                        <p className="text-xs text-muted-foreground mt-2">
                          {types.filter(t => t.category_id === category.id).length} document types
                        </p>
                      </div>
                    </div>
                    {!category.is_system && (
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleEditCategory(category)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDeleteCategory(category)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredCategories.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <FolderOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-medium">No categories found</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {categorySearch ? 'Try a different search term' : 'Create your first category to get started'}
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Document Types Tab */}
        <TabsContent value="types" className="space-y-4">
          <Card>
            <CardContent className="py-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-between">
                <div className="flex flex-col sm:flex-row gap-4 flex-1">
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search document types..."
                      value={typeSearch}
                      onChange={(e) => setTypeSearch(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                  <FormSelect
                    label=""
                    name="category-filter"
                    options={[
                      { value: 'all', label: 'All Categories' },
                      ...categories.map(c => ({ value: c.id, label: c.name }))
                    ]}
                    value={selectedCategoryFilter}
                    onChange={(e) => setSelectedCategoryFilter(e.target.value)}
                    containerClassName="w-full sm:w-48"
                  />
                </div>
                <Button onClick={handleAddType}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Type
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-3">
            {filteredTypes.map(type => {
              const category = categories.find(c => c.id === type.category_id)
              return (
                <Card key={type.id} className={!type.is_active ? 'opacity-60' : ''}>
                  <CardContent className="py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div
                          className="h-10 w-10 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: (category?.color || '#3B82F6') + '20' }}
                        >
                          <FileText className="h-5 w-5" style={{ color: category?.color || '#3B82F6' }} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium">{type.name}</h3>
                            {type.is_system && (
                              <Badge variant="secondary" className="text-xs">System</Badge>
                            )}
                            {!type.is_active && (
                              <Badge variant="outline" className="text-xs">Inactive</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <span>{type.code}</span>
                            <span>|</span>
                            <Badge variant="outline" style={{ borderColor: category?.color, color: category?.color }}>
                              {type.category_name || 'Unknown'}
                            </Badge>
                          </div>
                          {type.description && (
                            <p className="text-sm text-muted-foreground mt-1">{type.description}</p>
                          )}
                        </div>
                      </div>
                      {!type.is_system && (
                        <div className="flex gap-1">
                          <Button variant="ghost" size="icon" onClick={() => handleEditType(type)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={() => handleDeleteType(type)}>
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {filteredTypes.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-medium">No document types found</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {typeSearch || selectedCategoryFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Create your first document type to get started'
                  }
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Category Dialog */}
      <Dialog open={isCategoryDialogOpen} onOpenChange={setIsCategoryDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingCategory ? 'Edit Category' : 'Add New Category'}</DialogTitle>
            <DialogDescription>
              {editingCategory
                ? 'Update the category details'
                : 'Create a new document category for organizing your documents'
              }
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Code *</Label>
                <Input
                  value={categoryForm.code}
                  onChange={(e) => setCategoryForm(prev => ({ ...prev, code: e.target.value.toLowerCase().replace(/\s+/g, '_') }))}
                  placeholder="e.g., contracts"
                  disabled={!!editingCategory}
                />
              </div>
              <div className="space-y-2">
                <Label>Name *</Label>
                <Input
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Contracts"
                />
              </div>
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Description</Label>
              <Input
                value={categoryForm.description}
                onChange={(e) => setCategoryForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of this category"
              />
            </div>

            <div className="space-y-2">
              <Label>Color</Label>
              <div className="flex flex-wrap gap-2">
                {COLOR_OPTIONS.map(color => (
                  <button
                    key={color.value}
                    type="button"
                    className={`h-8 w-8 rounded-full border-2 transition-all ${
                      categoryForm.color === color.value ? 'border-foreground scale-110' : 'border-transparent'
                    }`}
                    style={{ backgroundColor: color.value }}
                    onClick={() => setCategoryForm(prev => ({ ...prev, color: color.value }))}
                    title={color.label}
                  />
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCategoryDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveCategory} disabled={isSaving || !categoryForm.code || !categoryForm.name}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingCategory ? 'Update Category' : 'Create Category'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Type Dialog */}
      <Dialog open={isTypeDialogOpen} onOpenChange={setIsTypeDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingType ? 'Edit Document Type' : 'Add New Document Type'}</DialogTitle>
            <DialogDescription>
              {editingType
                ? 'Update the document type details'
                : 'Create a new document type within a category'
              }
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Code *</Label>
                <Input
                  value={typeForm.code}
                  onChange={(e) => setTypeForm(prev => ({ ...prev, code: e.target.value.toLowerCase().replace(/\s+/g, '_') }))}
                  placeholder="e.g., service_agreement"
                  disabled={!!editingType}
                />
              </div>
              <div className="space-y-2">
                <Label>Name *</Label>
                <Input
                  value={typeForm.name}
                  onChange={(e) => setTypeForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Service Agreement"
                />
              </div>
            </ConfigFormRow>

            <FormSelect
              label="Category *"
              name="category"
              options={categories.filter(c => c.is_active).map(c => ({ value: c.id, label: c.name }))}
              value={typeForm.category_id}
              onChange={(e) => setTypeForm(prev => ({ ...prev, category_id: e.target.value }))}
              placeholder="Select a category"
            />

            <div className="space-y-2">
              <Label>Description</Label>
              <Input
                value={typeForm.description}
                onChange={(e) => setTypeForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of this document type"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsTypeDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveType} disabled={isSaving || !typeForm.code || !typeForm.name || !typeForm.category_id}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingType ? 'Update Type' : 'Create Type'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

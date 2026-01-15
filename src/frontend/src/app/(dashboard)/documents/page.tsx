"use client";
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText, Folder, Upload, Search, Plus, Download, Filter, Eye, Share2, Clock, CheckCircle, FileWarning, Settings } from "lucide-react";

const documents = [
  { id: "1", number: "DOC-000001", title: "Quality Policy Manual", category: "policy", status: "published", version: "3.0", lastModified: "2026-01-10", owner: "Quality Dept" },
  { id: "2", number: "DOC-000002", title: "Purchase Order Procedure", category: "procedure", status: "approved", version: "2.1", lastModified: "2026-01-08", owner: "Procurement" },
  { id: "3", number: "DOC-000003", title: "Work Instruction - Assembly", category: "work_instruction", status: "draft", version: "1.0", lastModified: "2026-01-14", owner: "Production" },
  { id: "4", number: "DOC-000004", title: "Annual Report Template", category: "template", status: "published", version: "1.2", lastModified: "2025-12-20", owner: "Finance" },
];

const folders = [
  { id: "1", name: "Quality Documents", count: 45, lastModified: "2026-01-10" },
  { id: "2", name: "HR Policies", count: 23, lastModified: "2026-01-05" },
  { id: "3", name: "Finance Reports", count: 67, lastModified: "2026-01-12" },
  { id: "4", name: "Engineering Drawings", count: 156, lastModified: "2026-01-14" },
];

export default function DocumentsPage() {
  const [activeTab, setActiveTab] = useState("browse");
  const [searchTerm, setSearchTerm] = useState("");

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      pending_review: "bg-yellow-100 text-yellow-800",
      approved: "bg-blue-100 text-blue-800",
      published: "bg-green-100 text-green-800",
      obsolete: "bg-red-100 text-red-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Document Management</h1>
          <p className="text-muted-foreground">Centralized document control and version management</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Download className="mr-2 h-4 w-4" />Export</Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button><Upload className="mr-2 h-4 w-4" />Upload Document</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Document</DialogTitle>
                <DialogDescription>Upload a new document to the system</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="space-y-2">
                  <Label>Document Title</Label>
                  <Input placeholder="Enter document title" />
                </div>
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select>
                    <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="policy">Policy</SelectItem>
                      <SelectItem value="procedure">Procedure</SelectItem>
                      <SelectItem value="work_instruction">Work Instruction</SelectItem>
                      <SelectItem value="form">Form</SelectItem>
                      <SelectItem value="template">Template</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>File</Label>
                  <Input type="file" />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Upload</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="browse"><Folder className="mr-2 h-4 w-4" />Browse</TabsTrigger>
          <TabsTrigger value="documents"><FileText className="mr-2 h-4 w-4" />All Documents</TabsTrigger>
          <TabsTrigger value="pending"><Clock className="mr-2 h-4 w-4" />Pending Approval</TabsTrigger>
          <TabsTrigger value="recent"><CheckCircle className="mr-2 h-4 w-4" />Recent</TabsTrigger>
        </TabsList>

        <TabsContent value="browse" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {folders.map((folder) => (
              <Card key={folder.id} className="cursor-pointer hover:bg-muted/50">
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Folder className="h-5 w-5 text-yellow-500" />
                    <CardTitle className="text-base">{folder.name}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground">
                    {folder.count} documents
                    <br />
                    Modified: {folder.lastModified}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="documents" className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search documents..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-8" />
            </div>
            <Select>
              <SelectTrigger className="w-[150px]"><Filter className="mr-2 h-4 w-4" /><SelectValue placeholder="Category" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="policy">Policy</SelectItem>
                <SelectItem value="procedure">Procedure</SelectItem>
                <SelectItem value="work_instruction">Work Instruction</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Document #</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Modified</TableHead>
                  <TableHead>Owner</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">{doc.number}</TableCell>
                    <TableCell>{doc.title}</TableCell>
                    <TableCell className="capitalize">{doc.category.replace("_", " ")}</TableCell>
                    <TableCell>v{doc.version}</TableCell>
                    <TableCell><Badge className={getStatusBadge(doc.status)}>{doc.status}</Badge></TableCell>
                    <TableCell>{doc.lastModified}</TableCell>
                    <TableCell>{doc.owner}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="sm"><Download className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="sm"><Share2 className="h-4 w-4" /></Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="pending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Documents Pending Approval</CardTitle>
              <CardDescription>Review and approve pending documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">Documents awaiting your approval will appear here</div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recently Accessed</CardTitle>
              <CardDescription>Your recently viewed documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">Recent documents will appear here</div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  FileText,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Download,
  Upload,
  ArrowRight,
  Trash2,
  Loader2,
} from "lucide-react";
import { PageHeader } from "@/components/layout";
import { Button, Card, Badge } from "@/components/ui";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useApi, useToast } from "@/hooks";

interface ComplianceItem {
  id: string;
  name: string;
  type: "pf" | "esi" | "tds" | "pt";
  dueDate: string;
  status: "pending" | "submitted" | "verified" | "overdue";
  amount: number;
  period: string;
}

const mockComplianceItems: ComplianceItem[] = [
  {
    id: "1",
    name: "PF ECR - January 2026",
    type: "pf",
    dueDate: "2026-02-15",
    status: "pending",
    amount: 294000,
    period: "January 2026",
  },
  {
    id: "2",
    name: "ESI Contribution - January 2026",
    type: "esi",
    dueDate: "2026-02-15",
    status: "pending",
    amount: 78400,
    period: "January 2026",
  },
  {
    id: "3",
    name: "TDS Payment - January 2026",
    type: "tds",
    dueDate: "2026-02-07",
    status: "overdue",
    amount: 145000,
    period: "January 2026",
  },
  {
    id: "4",
    name: "Professional Tax - January 2026",
    type: "pt",
    dueDate: "2026-02-20",
    status: "pending",
    amount: 9000,
    period: "January 2026",
  },
  {
    id: "5",
    name: "PF ECR - December 2025",
    type: "pf",
    dueDate: "2026-01-15",
    status: "submitted",
    amount: 289000,
    period: "December 2025",
  },
  {
    id: "6",
    name: "ESI Contribution - December 2025",
    type: "esi",
    dueDate: "2026-01-15",
    status: "verified",
    amount: 76200,
    period: "December 2025",
  },
];

const complianceStats = {
  totalDue: 526400,
  pending: 3,
  overdue: 1,
  submitted: 1,
  verified: 1,
};

export default function StatutoryPage() {
  const [filter, setFilter] = useState<"all" | "pending" | "overdue" | "submitted" | "verified">("all");
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Local state for data management
  const [complianceItems, setComplianceItems] = useState<ComplianceItem[]>(mockComplianceItems);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<ComplianceItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (item: ComplianceItem) => {
    setItemToDelete(item);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/statutory/compliance/${itemToDelete.id}`);
      setComplianceItems(complianceItems.filter(c => c.id !== itemToDelete.id));
      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast("success", "Compliance record deleted successfully");
    } catch (error) {
      showToast("error", "Failed to delete compliance record");
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredItems = complianceItems.filter((item) => {
    if (filter === "all") return true;
    return item.status === filter;
  });

  const getStatusBadge = (status: ComplianceItem["status"]) => {
    switch (status) {
      case "pending":
        return (
          <Badge variant="warning">
            <Clock className="h-3 w-3 mr-1" />
            Pending
          </Badge>
        );
      case "submitted":
        return (
          <Badge variant="info">
            <Upload className="h-3 w-3 mr-1" />
            Submitted
          </Badge>
        );
      case "verified":
        return (
          <Badge variant="success">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Verified
          </Badge>
        );
      case "overdue":
        return (
          <Badge variant="destructive">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Overdue
          </Badge>
        );
    }
  };

  const getTypeLink = (type: ComplianceItem["type"]) => {
    switch (type) {
      case "pf":
        return "/statutory/pf";
      case "esi":
        return "/statutory/esi";
      case "tds":
        return "/statutory/tds";
      default:
        return "/statutory";
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Statutory Compliance"
        description="Manage PF, ESI, TDS, and Professional Tax filings"
        icon={FileText}
        actions={
          <Button>
            <Calendar className="h-4 w-4 mr-2" />
            Compliance Calendar
          </Button>
        }
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Total Due</div>
          <div className="text-2xl font-bold">{formatCurrency(complianceStats.totalDue)}</div>
        </Card>
        <Card
          className={`p-4 cursor-pointer hover:border-warning ${
            filter === "pending" ? "border-warning bg-warning/5" : ""
          }`}
          onClick={() => setFilter("pending")}
        >
          <div className="text-sm text-muted-foreground">Pending</div>
          <div className="text-2xl font-bold text-warning">{complianceStats.pending}</div>
        </Card>
        <Card
          className={`p-4 cursor-pointer hover:border-destructive ${
            filter === "overdue" ? "border-destructive bg-destructive/5" : ""
          }`}
          onClick={() => setFilter("overdue")}
        >
          <div className="text-sm text-muted-foreground">Overdue</div>
          <div className="text-2xl font-bold text-destructive">{complianceStats.overdue}</div>
        </Card>
        <Card
          className={`p-4 cursor-pointer hover:border-info ${
            filter === "submitted" ? "border-info bg-info/5" : ""
          }`}
          onClick={() => setFilter("submitted")}
        >
          <div className="text-sm text-muted-foreground">Submitted</div>
          <div className="text-2xl font-bold text-info">{complianceStats.submitted}</div>
        </Card>
        <Card
          className={`p-4 cursor-pointer hover:border-success ${
            filter === "verified" ? "border-success bg-success/5" : ""
          }`}
          onClick={() => setFilter("verified")}
        >
          <div className="text-sm text-muted-foreground">Verified</div>
          <div className="text-2xl font-bold text-success">{complianceStats.verified}</div>
        </Card>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link href="/statutory/pf">
          <Card className="p-4 hover:border-primary cursor-pointer transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold">Provident Fund</div>
                <div className="text-sm text-muted-foreground">ECR Generation & Filing</div>
              </div>
              <ArrowRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </Card>
        </Link>
        <Link href="/statutory/esi">
          <Card className="p-4 hover:border-primary cursor-pointer transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold">ESI</div>
                <div className="text-sm text-muted-foreground">Contribution & Returns</div>
              </div>
              <ArrowRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </Card>
        </Link>
        <Link href="/statutory/tds">
          <Card className="p-4 hover:border-primary cursor-pointer transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold">TDS</div>
                <div className="text-sm text-muted-foreground">24Q Returns & Form 16</div>
              </div>
              <ArrowRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </Card>
        </Link>
        <Card className="p-4 hover:border-primary cursor-pointer transition-colors">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-semibold">Professional Tax</div>
              <div className="text-sm text-muted-foreground">Karnataka PT Filing</div>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground" />
          </div>
        </Card>
      </div>

      {/* Compliance Items List */}
      <Card>
        <div className="p-4 border-b flex items-center justify-between">
          <h3 className="font-semibold">Compliance Filings</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setFilter("all")}
            className={filter === "all" ? "bg-muted" : ""}
          >
            Show All
          </Button>
        </div>
        <div className="divide-y">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="p-4 flex items-center justify-between hover:bg-muted/50"
            >
              <div className="flex items-center gap-4">
                <div
                  className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    item.type === "pf"
                      ? "bg-blue-100 text-blue-600"
                      : item.type === "esi"
                      ? "bg-green-100 text-green-600"
                      : item.type === "tds"
                      ? "bg-orange-100 text-orange-600"
                      : "bg-purple-100 text-purple-600"
                  }`}
                >
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <div className="font-medium">{item.name}</div>
                  <div className="text-sm text-muted-foreground">
                    Due: {new Date(item.dueDate).toLocaleDateString("en-IN")}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="font-semibold">{formatCurrency(item.amount)}</div>
                  <div className="text-sm text-muted-foreground">{item.period}</div>
                </div>
                {getStatusBadge(item.status)}
                <div className="flex items-center gap-2">
                  <Link href={getTypeLink(item.type)}>
                    <Button variant="outline" size="sm">
                      {item.status === "pending" || item.status === "overdue" ? (
                        <>
                          <Upload className="h-4 w-4 mr-1" />
                          Generate
                        </>
                      ) : (
                        <>
                          <Download className="h-4 w-4 mr-1" />
                          View
                        </>
                      )}
                    </Button>
                  </Link>
                  {item.status === "verified" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => handleDeleteClick(item)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Compliance Record
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{itemToDelete?.name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

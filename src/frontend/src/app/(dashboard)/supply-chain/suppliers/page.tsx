'use client';

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  Loader2,
  AlertTriangle,
  Users,
  TrendingUp,
  Package,
  Star,
  Download,
  Mail,
  Phone,
  MapPin,
  Building2,
  X,
  Clock,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useApi, useToast } from '@/hooks';
import { formatCurrency, formatDate, formatPhone } from '@/lib/format';

// Types
interface Supplier {
  id: string;
  code: string;
  name: string;
  tier: 'strategic' | 'preferred' | 'approved' | 'probationary';
  status: 'active' | 'inactive' | 'blacklisted';
  // Contact Information
  contact_person: string;
  email: string;
  phone: string;
  alternate_phone?: string;
  website?: string;
  // Address
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  pincode: string;
  country: string;
  // Business Details
  gstin: string;
  pan: string;
  bank_name: string;
  bank_account: string;
  bank_ifsc: string;
  // Terms
  payment_terms: number; // days
  credit_limit: number;
  currency: string;
  // Performance Metrics
  rating: number; // 1-5
  total_orders: number;
  on_time_delivery: number; // percentage
  quality_score: number; // percentage
  total_value: number;
  // Notes
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Status and tier colors
const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  blacklisted: 'bg-red-100 text-red-800',
};

const tierColors: Record<string, string> = {
  strategic: 'bg-purple-100 text-purple-800',
  preferred: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  probationary: 'bg-yellow-100 text-yellow-800',
};

// Mock data
const mockSuppliers: Supplier[] = [
  {
    id: '1',
    code: 'SUP-001',
    name: 'Tata Steel Ltd',
    tier: 'strategic',
    status: 'active',
    contact_person: 'Ravi Sharma',
    email: 'procurement@tatasteel.com',
    phone: '9876543210',
    alternate_phone: '9876543211',
    website: 'www.tatasteel.com',
    address_line1: 'Tata Steel Plant',
    address_line2: 'Jamshedpur Road',
    city: 'Jamshedpur',
    state: 'Jharkhand',
    pincode: '831001',
    country: 'India',
    gstin: '20AABCT1234F1ZA',
    pan: 'AABCT1234F',
    bank_name: 'HDFC Bank',
    bank_account: '50100012345678',
    bank_ifsc: 'HDFC0000123',
    payment_terms: 30,
    credit_limit: 50000000,
    currency: 'INR',
    rating: 4.8,
    total_orders: 156,
    on_time_delivery: 98,
    quality_score: 97,
    total_value: 125000000,
    notes: 'Strategic partner for steel requirements',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2026-01-10T14:30:00Z',
  },
  {
    id: '2',
    code: 'SUP-002',
    name: 'Reliance Industries',
    tier: 'strategic',
    status: 'active',
    contact_person: 'Amit Patel',
    email: 'vendor@relianceindustries.com',
    phone: '9988776655',
    website: 'www.ril.com',
    address_line1: 'Maker Chambers IV',
    address_line2: 'Nariman Point',
    city: 'Mumbai',
    state: 'Maharashtra',
    pincode: '400021',
    country: 'India',
    gstin: '27AABCR1234G1ZB',
    pan: 'AABCR1234G',
    bank_name: 'ICICI Bank',
    bank_account: '004405012345',
    bank_ifsc: 'ICIC0000044',
    payment_terms: 45,
    credit_limit: 100000000,
    currency: 'INR',
    rating: 4.6,
    total_orders: 89,
    on_time_delivery: 95,
    quality_score: 94,
    total_value: 89000000,
    created_at: '2024-03-20T09:00:00Z',
    updated_at: '2026-01-08T11:00:00Z',
  },
  {
    id: '3',
    code: 'SUP-003',
    name: 'Mahindra Components',
    tier: 'preferred',
    status: 'active',
    contact_person: 'Priya Mehta',
    email: 'sales@mahindracomponents.in',
    phone: '8877665544',
    address_line1: 'Auto Cluster',
    city: 'Pune',
    state: 'Maharashtra',
    pincode: '411018',
    country: 'India',
    gstin: '27AABCM5678H1ZC',
    pan: 'AABCM5678H',
    bank_name: 'Axis Bank',
    bank_account: '917020012345678',
    bank_ifsc: 'UTIB0001234',
    payment_terms: 30,
    credit_limit: 25000000,
    currency: 'INR',
    rating: 4.2,
    total_orders: 67,
    on_time_delivery: 92,
    quality_score: 90,
    total_value: 45000000,
    created_at: '2024-06-10T14:00:00Z',
    updated_at: '2026-01-06T16:00:00Z',
  },
  {
    id: '4',
    code: 'SUP-004',
    name: 'Jindal Steel & Power',
    tier: 'approved',
    status: 'active',
    contact_person: 'Vikram Singh',
    email: 'vendor.sales@jindalsteel.com',
    phone: '7766554433',
    address_line1: 'Jindal Centre',
    city: 'New Delhi',
    state: 'Delhi',
    pincode: '110001',
    country: 'India',
    gstin: '07AABCJ9012K1ZD',
    pan: 'AABCJ9012K',
    bank_name: 'State Bank of India',
    bank_account: '38706543210',
    bank_ifsc: 'SBIN0001234',
    payment_terms: 30,
    credit_limit: 30000000,
    currency: 'INR',
    rating: 4.0,
    total_orders: 45,
    on_time_delivery: 88,
    quality_score: 85,
    total_value: 32000000,
    created_at: '2024-08-15T11:00:00Z',
    updated_at: '2026-01-10T09:00:00Z',
  },
  {
    id: '5',
    code: 'SUP-005',
    name: 'Larsen & Toubro Ltd',
    tier: 'strategic',
    status: 'active',
    contact_person: 'Sanjay Gupta',
    email: 'procurement@larsentoubro.com',
    phone: '6655443322',
    address_line1: 'L&T House',
    address_line2: 'Ballard Estate',
    city: 'Mumbai',
    state: 'Maharashtra',
    pincode: '400001',
    country: 'India',
    gstin: '27AABCL3456L1ZE',
    pan: 'AABCL3456L',
    bank_name: 'Kotak Mahindra Bank',
    bank_account: '1234567890',
    bank_ifsc: 'KKBK0001234',
    payment_terms: 60,
    credit_limit: 75000000,
    currency: 'INR',
    rating: 4.7,
    total_orders: 112,
    on_time_delivery: 96,
    quality_score: 95,
    total_value: 98000000,
    notes: 'Major supplier for engineering equipment',
    created_at: '2023-11-20T10:00:00Z',
    updated_at: '2026-01-12T14:00:00Z',
  },
  {
    id: '6',
    code: 'SUP-006',
    name: 'ABC Traders',
    tier: 'probationary',
    status: 'inactive',
    contact_person: 'Raj Kumar',
    email: 'info@abctraders.com',
    phone: '5544332211',
    address_line1: 'Industrial Area',
    city: 'Noida',
    state: 'Uttar Pradesh',
    pincode: '201301',
    country: 'India',
    gstin: '09AABCA7890M1ZF',
    pan: 'AABCA7890M',
    bank_name: 'Punjab National Bank',
    bank_account: '0123456789',
    bank_ifsc: 'PUNB0123400',
    payment_terms: 15,
    credit_limit: 5000000,
    currency: 'INR',
    rating: 3.2,
    total_orders: 12,
    on_time_delivery: 75,
    quality_score: 70,
    total_value: 3500000,
    notes: 'On probation due to delivery issues',
    created_at: '2025-06-01T10:00:00Z',
    updated_at: '2025-12-15T14:00:00Z',
  },
];

// Empty form data
const emptyFormData = {
  name: '',
  tier: '' as Supplier['tier'] | '',
  status: 'active' as Supplier['status'],
  contact_person: '',
  email: '',
  phone: '',
  alternate_phone: '',
  website: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  pincode: '',
  country: 'India',
  gstin: '',
  pan: '',
  bank_name: '',
  bank_account: '',
  bank_ifsc: '',
  payment_terms: 30,
  credit_limit: 0,
  notes: '',
};

export default function SuppliersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [tierFilter, setTierFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);
  const { showToast } = useToast();

  // API hooks
  const { data: suppliersData, isLoading, get: getSuppliers } = useApi<{ data: Supplier[] }>();
  const createApi = useApi<Supplier>();
  const updateApi = useApi<Supplier>();
  const deleteApi = useApi();

  // Local state
  const [localSuppliers, setLocalSuppliers] = useState<Supplier[]>(mockSuppliers);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state
  const [formData, setFormData] = useState(emptyFormData);

  useEffect(() => {
    getSuppliers('/supply-chain/suppliers');
  }, [getSuppliers]);

  useEffect(() => {
    if (suppliersData?.data) {
      setLocalSuppliers(suppliersData.data);
    }
  }, [suppliersData]);

  const suppliers = localSuppliers;

  // Filter suppliers
  const filteredSuppliers = suppliers.filter((supplier) => {
    const matchesSearch =
      !searchQuery ||
      supplier.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      supplier.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      supplier.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      supplier.city.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || supplier.status === statusFilter;
    const matchesTier = tierFilter === 'all' || supplier.tier === tierFilter;

    return matchesSearch && matchesStatus && matchesTier;
  });

  // Stats
  const stats = {
    total: suppliers.length,
    active: suppliers.filter((s) => s.status === 'active').length,
    strategic: suppliers.filter((s) => s.tier === 'strategic').length,
    avgRating: suppliers.length > 0 ? (suppliers.reduce((sum, s) => sum + s.rating, 0) / suppliers.length).toFixed(1) : '0',
    totalValue: suppliers.reduce((sum, s) => sum + s.total_value, 0),
  };

  // Generate supplier code
  const generateSupplierCode = () => {
    const maxCode = suppliers.reduce((max, s) => {
      const num = parseInt(s.code.replace('SUP-', ''));
      return num > max ? num : max;
    }, 0);
    return `SUP-${String(maxCode + 1).padStart(3, '0')}`;
  };

  // Handle create supplier
  const handleCreateSupplier = async () => {
    if (!formData.name || !formData.tier || !formData.email || !formData.phone) {
      showToast('error', 'Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    try {
      const newSupplier: Supplier = {
        id: String(Date.now()),
        code: generateSupplierCode(),
        name: formData.name,
        tier: formData.tier as Supplier['tier'],
        status: formData.status,
        contact_person: formData.contact_person,
        email: formData.email,
        phone: formData.phone,
        alternate_phone: formData.alternate_phone,
        website: formData.website,
        address_line1: formData.address_line1,
        address_line2: formData.address_line2,
        city: formData.city,
        state: formData.state,
        pincode: formData.pincode,
        country: formData.country,
        gstin: formData.gstin,
        pan: formData.pan,
        bank_name: formData.bank_name,
        bank_account: formData.bank_account,
        bank_ifsc: formData.bank_ifsc,
        payment_terms: formData.payment_terms,
        credit_limit: formData.credit_limit,
        currency: 'INR',
        rating: 0,
        total_orders: 0,
        on_time_delivery: 0,
        quality_score: 0,
        total_value: 0,
        notes: formData.notes,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      await createApi.post('/supply-chain/suppliers', newSupplier);
      setLocalSuppliers([newSupplier, ...localSuppliers]);
      setCreateDialogOpen(false);
      resetForm();
      showToast('success', 'Supplier created successfully');
    } catch (error) {
      console.error('Failed to create supplier:', error);
      showToast('error', 'Failed to create supplier');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle edit supplier
  const handleEditSupplier = async () => {
    if (!selectedSupplier) return;

    if (!formData.name || !formData.tier || !formData.email || !formData.phone) {
      showToast('error', 'Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    try {
      const updatedSupplier: Supplier = {
        ...selectedSupplier,
        name: formData.name,
        tier: formData.tier as Supplier['tier'],
        status: formData.status,
        contact_person: formData.contact_person,
        email: formData.email,
        phone: formData.phone,
        alternate_phone: formData.alternate_phone,
        website: formData.website,
        address_line1: formData.address_line1,
        address_line2: formData.address_line2,
        city: formData.city,
        state: formData.state,
        pincode: formData.pincode,
        country: formData.country,
        gstin: formData.gstin,
        pan: formData.pan,
        bank_name: formData.bank_name,
        bank_account: formData.bank_account,
        bank_ifsc: formData.bank_ifsc,
        payment_terms: formData.payment_terms,
        credit_limit: formData.credit_limit,
        notes: formData.notes,
        updated_at: new Date().toISOString(),
      };

      await updateApi.put(`/supply-chain/suppliers/${selectedSupplier.id}`, updatedSupplier);
      setLocalSuppliers(localSuppliers.map((s) => (s.id === selectedSupplier.id ? updatedSupplier : s)));
      setEditDialogOpen(false);
      setSelectedSupplier(null);
      resetForm();
      showToast('success', 'Supplier updated successfully');
    } catch (error) {
      console.error('Failed to update supplier:', error);
      showToast('error', 'Failed to update supplier');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle delete supplier
  const handleDeleteSupplier = async () => {
    if (!selectedSupplier) return;

    setIsDeleting(true);
    try {
      await deleteApi.delete(`/supply-chain/suppliers/${selectedSupplier.id}`);
      setLocalSuppliers(localSuppliers.filter((s) => s.id !== selectedSupplier.id));
      setDeleteDialogOpen(false);
      setSelectedSupplier(null);
      showToast('success', 'Supplier deleted successfully');
    } catch (error) {
      console.error('Failed to delete supplier:', error);
      showToast('error', 'Failed to delete supplier');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData(emptyFormData);
  };

  const openEditDialog = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setFormData({
      name: supplier.name,
      tier: supplier.tier,
      status: supplier.status,
      contact_person: supplier.contact_person,
      email: supplier.email,
      phone: supplier.phone,
      alternate_phone: supplier.alternate_phone || '',
      website: supplier.website || '',
      address_line1: supplier.address_line1,
      address_line2: supplier.address_line2 || '',
      city: supplier.city,
      state: supplier.state,
      pincode: supplier.pincode,
      country: supplier.country,
      gstin: supplier.gstin,
      pan: supplier.pan,
      bank_name: supplier.bank_name,
      bank_account: supplier.bank_account,
      bank_ifsc: supplier.bank_ifsc,
      payment_terms: supplier.payment_terms,
      credit_limit: supplier.credit_limit,
      notes: supplier.notes || '',
    });
    setEditDialogOpen(true);
  };

  const openViewDialog = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setViewDialogOpen(true);
  };

  const openDeleteDialog = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setDeleteDialogOpen(true);
  };

  const clearFilters = () => {
    setStatusFilter('all');
    setTierFilter('all');
  };

  const activeFiltersCount = [statusFilter !== 'all', tierFilter !== 'all'].filter(Boolean).length;

  // Render star rating
  const renderRating = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />);
      } else if (i === fullStars && hasHalfStar) {
        stars.push(<Star key={i} className="h-4 w-4 fill-yellow-400/50 text-yellow-400" />);
      } else {
        stars.push(<Star key={i} className="h-4 w-4 text-gray-300" />);
      }
    }
    return stars;
  };

  // Supplier form component
  const SupplierForm = ({ isEdit = false }: { isEdit?: boolean }) => (
    <div className="space-y-6 py-4 max-h-[60vh] overflow-y-auto">
      {/* Basic Information */}
      <div>
        <h4 className="font-medium mb-4">Basic Information</h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <Label htmlFor="name">Supplier Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Enter supplier name"
            />
          </div>
          <div>
            <Label htmlFor="tier">Tier *</Label>
            <Select value={formData.tier} onValueChange={(value) => setFormData({ ...formData, tier: value as Supplier['tier'] })}>
              <SelectTrigger>
                <SelectValue placeholder="Select tier" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="strategic">Strategic</SelectItem>
                <SelectItem value="preferred">Preferred</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="probationary">Probationary</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="status">Status *</Label>
            <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value as Supplier['status'] })}>
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="blacklisted">Blacklisted</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div>
        <h4 className="font-medium mb-4">Contact Information</h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="contact_person">Contact Person *</Label>
            <Input
              id="contact_person"
              value={formData.contact_person}
              onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
              placeholder="Primary contact name"
            />
          </div>
          <div>
            <Label htmlFor="email">Email *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="email@company.com"
            />
          </div>
          <div>
            <Label htmlFor="phone">Phone *</Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="9876543210"
            />
          </div>
          <div>
            <Label htmlFor="alternate_phone">Alternate Phone</Label>
            <Input
              id="alternate_phone"
              value={formData.alternate_phone}
              onChange={(e) => setFormData({ ...formData, alternate_phone: e.target.value })}
              placeholder="Optional"
            />
          </div>
          <div className="md:col-span-2">
            <Label htmlFor="website">Website</Label>
            <Input
              id="website"
              value={formData.website}
              onChange={(e) => setFormData({ ...formData, website: e.target.value })}
              placeholder="www.company.com"
            />
          </div>
        </div>
      </div>

      {/* Address */}
      <div>
        <h4 className="font-medium mb-4">Address</h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <Label htmlFor="address_line1">Address Line 1</Label>
            <Input
              id="address_line1"
              value={formData.address_line1}
              onChange={(e) => setFormData({ ...formData, address_line1: e.target.value })}
              placeholder="Street address"
            />
          </div>
          <div className="md:col-span-2">
            <Label htmlFor="address_line2">Address Line 2</Label>
            <Input
              id="address_line2"
              value={formData.address_line2}
              onChange={(e) => setFormData({ ...formData, address_line2: e.target.value })}
              placeholder="Optional"
            />
          </div>
          <div>
            <Label htmlFor="city">City</Label>
            <Input
              id="city"
              value={formData.city}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              placeholder="City"
            />
          </div>
          <div>
            <Label htmlFor="state">State</Label>
            <Input
              id="state"
              value={formData.state}
              onChange={(e) => setFormData({ ...formData, state: e.target.value })}
              placeholder="State"
            />
          </div>
          <div>
            <Label htmlFor="pincode">Pincode</Label>
            <Input
              id="pincode"
              value={formData.pincode}
              onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
              placeholder="400001"
            />
          </div>
          <div>
            <Label htmlFor="country">Country</Label>
            <Input
              id="country"
              value={formData.country}
              onChange={(e) => setFormData({ ...formData, country: e.target.value })}
              placeholder="India"
            />
          </div>
        </div>
      </div>

      {/* Business Details */}
      <div>
        <h4 className="font-medium mb-4">Business Details</h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="gstin">GSTIN</Label>
            <Input
              id="gstin"
              value={formData.gstin}
              onChange={(e) => setFormData({ ...formData, gstin: e.target.value.toUpperCase() })}
              placeholder="27AABCT1234F1ZA"
            />
          </div>
          <div>
            <Label htmlFor="pan">PAN</Label>
            <Input
              id="pan"
              value={formData.pan}
              onChange={(e) => setFormData({ ...formData, pan: e.target.value.toUpperCase() })}
              placeholder="AABCT1234F"
            />
          </div>
          <div>
            <Label htmlFor="bank_name">Bank Name</Label>
            <Input
              id="bank_name"
              value={formData.bank_name}
              onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
              placeholder="HDFC Bank"
            />
          </div>
          <div>
            <Label htmlFor="bank_account">Bank Account Number</Label>
            <Input
              id="bank_account"
              value={formData.bank_account}
              onChange={(e) => setFormData({ ...formData, bank_account: e.target.value })}
              placeholder="50100012345678"
            />
          </div>
          <div>
            <Label htmlFor="bank_ifsc">IFSC Code</Label>
            <Input
              id="bank_ifsc"
              value={formData.bank_ifsc}
              onChange={(e) => setFormData({ ...formData, bank_ifsc: e.target.value.toUpperCase() })}
              placeholder="HDFC0000123"
            />
          </div>
        </div>
      </div>

      {/* Payment Terms */}
      <div>
        <h4 className="font-medium mb-4">Payment Terms</h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="payment_terms">Payment Terms (Days)</Label>
            <Input
              id="payment_terms"
              type="number"
              value={formData.payment_terms || ''}
              onChange={(e) => setFormData({ ...formData, payment_terms: Number(e.target.value) })}
              placeholder="30"
            />
          </div>
          <div>
            <Label htmlFor="credit_limit">Credit Limit (INR)</Label>
            <Input
              id="credit_limit"
              type="number"
              value={formData.credit_limit || ''}
              onChange={(e) => setFormData({ ...formData, credit_limit: Number(e.target.value) })}
              placeholder="5000000"
            />
          </div>
        </div>
      </div>

      {/* Notes */}
      <div>
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          placeholder="Additional notes about this supplier..."
        />
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Supplier Master"
        description="Manage supplier information, performance, and relationships"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Supply Chain', href: '/supply-chain' },
          { label: 'Suppliers' },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Supplier
            </Button>
          </div>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading suppliers...</span>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-5">
        <StatCard title="Total Suppliers" value={stats.total} icon={Users} description="All vendors" />
        <StatCard
          title="Active"
          value={stats.active}
          icon={CheckCircle}
          description="Active suppliers"
          className="border-green-200 bg-green-50"
        />
        <StatCard
          title="Strategic"
          value={stats.strategic}
          icon={TrendingUp}
          description="Strategic partners"
          className="border-purple-200 bg-purple-50"
        />
        <StatCard title="Avg Rating" value={stats.avgRating} icon={Star} description="Performance score" />
        <StatCard
          title="Total Value"
          value={formatCurrency(stats.totalValue)}
          icon={Package}
          description="Lifetime purchases"
        />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name, code, email, or city..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Button
                variant={showFilters ? 'secondary' : 'outline'}
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {activeFiltersCount > 0 && (
                  <Badge className="ml-2 bg-primary text-primary-foreground">{activeFiltersCount}</Badge>
                )}
              </Button>
            </div>

            {showFilters && (
              <div className="pt-4 border-t">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label className="text-sm font-medium mb-1 block">Status</Label>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                        <SelectItem value="blacklisted">Blacklisted</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-sm font-medium mb-1 block">Tier</Label>
                    <Select value={tierFilter} onValueChange={setTierFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Tiers" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Tiers</SelectItem>
                        <SelectItem value="strategic">Strategic</SelectItem>
                        <SelectItem value="preferred">Preferred</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="probationary">Probationary</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                {activeFiltersCount > 0 && (
                  <div className="mt-4 flex justify-end">
                    <Button variant="ghost" size="sm" onClick={clearFilters}>
                      <X className="h-4 w-4 mr-1" />
                      Clear all filters
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Suppliers Table */}
      <Card>
        <CardHeader>
          <CardTitle>Suppliers ({filteredSuppliers.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Supplier</th>
                  <th className="text-left p-4 font-medium">Contact</th>
                  <th className="text-left p-4 font-medium">Tier</th>
                  <th className="text-center p-4 font-medium">Rating</th>
                  <th className="text-right p-4 font-medium">Orders</th>
                  <th className="text-right p-4 font-medium">On-Time %</th>
                  <th className="text-right p-4 font-medium">Credit Limit</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredSuppliers.map((supplier) => (
                  <tr key={supplier.id} className="border-t hover:bg-muted/30">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                          <Building2 className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium">{supplier.name}</p>
                          <p className="text-xs text-muted-foreground">{supplier.code}</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="space-y-1 text-sm">
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Mail className="h-3 w-3" />
                          <span className="truncate max-w-[150px]">{supplier.email}</span>
                        </div>
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Phone className="h-3 w-3" />
                          <span>{formatPhone(supplier.phone)}</span>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <Badge className={tierColors[supplier.tier]}>{supplier.tier}</Badge>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-center gap-1">
                        {renderRating(supplier.rating)}
                        <span className="ml-1 text-sm font-medium">{supplier.rating}</span>
                      </div>
                    </td>
                    <td className="p-4 text-right">{supplier.total_orders}</td>
                    <td className="p-4 text-right">
                      <span className={supplier.on_time_delivery >= 90 ? 'text-green-600' : 'text-yellow-600'}>
                        {supplier.on_time_delivery}%
                      </span>
                    </td>
                    <td className="p-4 text-right font-medium">{formatCurrency(supplier.credit_limit)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[supplier.status]}>{supplier.status}</Badge>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon" onClick={() => openViewDialog(supplier)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => openEditDialog(supplier)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        {supplier.status === 'blacklisted' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => openDeleteDialog(supplier)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredSuppliers.length === 0 && (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-muted-foreground">
                      No suppliers found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Create Supplier Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add New Supplier</DialogTitle>
            <DialogDescription>Add a new supplier to your vendor master</DialogDescription>
          </DialogHeader>

          <SupplierForm />

          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateSupplier} disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Add Supplier'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Supplier Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Supplier</DialogTitle>
            <DialogDescription>
              {selectedSupplier?.name} ({selectedSupplier?.code})
            </DialogDescription>
          </DialogHeader>

          <SupplierForm isEdit />

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditSupplier} disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Supplier Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Supplier Details</DialogTitle>
            <DialogDescription>
              {selectedSupplier?.name} ({selectedSupplier?.code})
            </DialogDescription>
          </DialogHeader>

          {selectedSupplier && (
            <div className="space-y-6 py-4">
              {/* Status and Tier */}
              <div className="flex items-center gap-3">
                <Badge className={statusColors[selectedSupplier.status]}>{selectedSupplier.status}</Badge>
                <Badge className={tierColors[selectedSupplier.tier]}>{selectedSupplier.tier}</Badge>
                <div className="flex items-center gap-1 ml-auto">
                  {renderRating(selectedSupplier.rating)}
                  <span className="ml-1 font-medium">{selectedSupplier.rating}</span>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="grid gap-4 md:grid-cols-4 p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label className="text-muted-foreground text-xs">Total Orders</Label>
                  <p className="text-xl font-bold">{selectedSupplier.total_orders}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground text-xs">On-Time Delivery</Label>
                  <p className="text-xl font-bold text-green-600">{selectedSupplier.on_time_delivery}%</p>
                </div>
                <div>
                  <Label className="text-muted-foreground text-xs">Quality Score</Label>
                  <p className="text-xl font-bold text-blue-600">{selectedSupplier.quality_score}%</p>
                </div>
                <div>
                  <Label className="text-muted-foreground text-xs">Total Value</Label>
                  <p className="text-xl font-bold">{formatCurrency(selectedSupplier.total_value)}</p>
                </div>
              </div>

              {/* Contact Information */}
              <div>
                <h4 className="font-medium mb-3">Contact Information</h4>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedSupplier.contact_person}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedSupplier.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span>{formatPhone(selectedSupplier.phone)}</span>
                  </div>
                  {selectedSupplier.website && (
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-muted-foreground" />
                      <span>{selectedSupplier.website}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Address */}
              <div>
                <h4 className="font-medium mb-3">Address</h4>
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p>{selectedSupplier.address_line1}</p>
                    {selectedSupplier.address_line2 && <p>{selectedSupplier.address_line2}</p>}
                    <p>
                      {selectedSupplier.city}, {selectedSupplier.state} - {selectedSupplier.pincode}
                    </p>
                    <p>{selectedSupplier.country}</p>
                  </div>
                </div>
              </div>

              {/* Business Details */}
              <div>
                <h4 className="font-medium mb-3">Business Details</h4>
                <div className="grid gap-3 md:grid-cols-2">
                  <div>
                    <Label className="text-muted-foreground text-xs">GSTIN</Label>
                    <p className="font-mono">{selectedSupplier.gstin}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-xs">PAN</Label>
                    <p className="font-mono">{selectedSupplier.pan}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-xs">Bank</Label>
                    <p>{selectedSupplier.bank_name}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-xs">Account Number</Label>
                    <p className="font-mono">{selectedSupplier.bank_account}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-xs">IFSC</Label>
                    <p className="font-mono">{selectedSupplier.bank_ifsc}</p>
                  </div>
                </div>
              </div>

              {/* Payment Terms */}
              <div>
                <h4 className="font-medium mb-3">Payment Terms</h4>
                <div className="grid gap-3 md:grid-cols-2">
                  <div>
                    <Label className="text-muted-foreground text-xs">Payment Terms</Label>
                    <p>{selectedSupplier.payment_terms} days</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-xs">Credit Limit</Label>
                    <p className="font-medium">{formatCurrency(selectedSupplier.credit_limit)}</p>
                  </div>
                </div>
              </div>

              {/* Notes */}
              {selectedSupplier.notes && (
                <div>
                  <h4 className="font-medium mb-3">Notes</h4>
                  <p className="text-muted-foreground">{selectedSupplier.notes}</p>
                </div>
              )}

              {/* Timestamps */}
              <div className="text-xs text-muted-foreground flex items-center gap-4">
                <span>Created: {formatDate(selectedSupplier.created_at, { format: 'long', showTime: true })}</span>
                <span>Updated: {formatDate(selectedSupplier.updated_at, { format: 'long', showTime: true })}</span>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
            <Button
              onClick={() => {
                setViewDialogOpen(false);
                if (selectedSupplier) openEditDialog(selectedSupplier);
              }}
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit Supplier
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Supplier
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{selectedSupplier?.name}</strong> ({selectedSupplier?.code})?
              This will remove all supplier data permanently. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteSupplier}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

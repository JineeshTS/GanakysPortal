'use client';

/**
 * Tax Declaration Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import payrollApi from '@/lib/api/payroll';
import type { TaxDeclaration, TaxRegime } from '@/types/payroll';

export default function TaxDeclarationPage() {
  const router = useRouter();
  const [declaration, setDeclaration] = useState<TaxDeclaration | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // Financial year options
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth();
  const defaultFY = currentMonth >= 3 ? `${currentYear}-${currentYear + 1}` : `${currentYear - 1}-${currentYear}`;
  const [selectedFY, setSelectedFY] = useState(defaultFY);

  // Form state
  const [formData, setFormData] = useState({
    tax_regime: 'new' as TaxRegime,
    section_80c: 0,
    section_80d: 0,
    section_80g: 0,
    hra_exemption: 0,
    lta_exemption: 0,
  });

  const loadDeclaration = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await payrollApi.getMyTaxDeclaration(selectedFY);
      setDeclaration(data);
      setFormData({
        tax_regime: data.tax_regime,
        section_80c: data.section_80c,
        section_80d: data.section_80d,
        section_80g: data.section_80g,
        hra_exemption: data.hra_exemption,
        lta_exemption: data.lta_exemption,
      });
    } catch (error) {
      console.error('Failed to load tax declaration:', error);
      // Create empty form for new declaration
      setDeclaration(null);
      setFormData({
        tax_regime: 'new',
        section_80c: 0,
        section_80d: 0,
        section_80g: 0,
        hra_exemption: 0,
        lta_exemption: 0,
      });
    } finally {
      setIsLoading(false);
    }
  }, [selectedFY]);

  useEffect(() => {
    loadDeclaration();
  }, [loadDeclaration]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await payrollApi.updateTaxDeclaration({
        financial_year: selectedFY,
        ...formData,
      });
      await loadDeclaration();
      setEditMode(false);
    } catch (error) {
      console.error('Failed to save declaration:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSubmit = async () => {
    if (!confirm('Are you sure you want to submit this declaration? You will not be able to edit it after submission.')) return;

    setIsSubmitting(true);
    try {
      await payrollApi.submitTaxDeclaration();
      await loadDeclaration();
    } catch (error) {
      console.error('Failed to submit declaration:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const totalInvestments = formData.section_80c + formData.section_80d + formData.section_80g + formData.hra_exemption + formData.lta_exemption;

  const canEdit = !declaration || declaration.status === 'draft';
  const fyOptions = [
    `${currentYear - 1}-${currentYear}`,
    `${currentYear}-${currentYear + 1}`,
  ];

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/payroll')}>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Tax Declaration</h1>
              <p className="text-muted-foreground">
                Declare your tax-saving investments
              </p>
            </div>
          </div>
          <Select value={selectedFY} onValueChange={setSelectedFY}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {fyOptions.map((fy) => (
                <SelectItem key={fy} value={fy}>
                  FY {fy}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {isLoading ? (
          <Card>
            <CardContent className="py-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Loading declaration...</p>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Status Card */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Declaration Status</CardTitle>
                    <CardDescription>FY {selectedFY}</CardDescription>
                  </div>
                  {declaration && (
                    <Badge
                      variant="secondary"
                      className={
                        declaration.status === 'verified'
                          ? 'bg-green-100 text-green-800'
                          : declaration.status === 'submitted'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                      }
                    >
                      {declaration.status.charAt(0).toUpperCase() + declaration.status.slice(1)}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold">{formatCurrency(totalInvestments)}</div>
                    <div className="text-sm text-muted-foreground">Total Declared Investments</div>
                  </div>
                  {canEdit && !editMode && (
                    <Button onClick={() => setEditMode(true)}>
                      <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                      </svg>
                      Edit Declaration
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Declaration Form */}
            <Card>
              <CardHeader>
                <CardTitle>Investment Details</CardTitle>
                <CardDescription>
                  Enter your tax-saving investments for the financial year
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Tax Regime */}
                <div className="space-y-2">
                  <Label>Tax Regime</Label>
                  {editMode ? (
                    <Select
                      value={formData.tax_regime}
                      onValueChange={(v) => setFormData({ ...formData, tax_regime: v as TaxRegime })}
                      disabled={isSaving}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="new">New Regime (Lower rates, no deductions)</SelectItem>
                        <SelectItem value="old">Old Regime (Higher rates, with deductions)</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <div className="font-medium">
                      {formData.tax_regime === 'new' ? 'New Regime' : 'Old Regime'}
                    </div>
                  )}
                </div>

                {formData.tax_regime === 'old' && (
                  <>
                    {/* Section 80C */}
                    <div className="space-y-2">
                      <Label>Section 80C (Max: 1,50,000)</Label>
                      <p className="text-xs text-muted-foreground">
                        PPF, ELSS, LIC, EPF, NSC, Tax Saver FD, etc.
                      </p>
                      {editMode ? (
                        <Input
                          type="number"
                          value={formData.section_80c}
                          onChange={(e) => setFormData({ ...formData, section_80c: Math.min(150000, parseInt(e.target.value) || 0) })}
                          disabled={isSaving}
                          max={150000}
                        />
                      ) : (
                        <div className="font-medium">{formatCurrency(formData.section_80c)}</div>
                      )}
                    </div>

                    {/* Section 80D */}
                    <div className="space-y-2">
                      <Label>Section 80D (Max: 75,000)</Label>
                      <p className="text-xs text-muted-foreground">
                        Health Insurance Premium (Self, Family, Parents)
                      </p>
                      {editMode ? (
                        <Input
                          type="number"
                          value={formData.section_80d}
                          onChange={(e) => setFormData({ ...formData, section_80d: Math.min(75000, parseInt(e.target.value) || 0) })}
                          disabled={isSaving}
                          max={75000}
                        />
                      ) : (
                        <div className="font-medium">{formatCurrency(formData.section_80d)}</div>
                      )}
                    </div>

                    {/* Section 80G */}
                    <div className="space-y-2">
                      <Label>Section 80G</Label>
                      <p className="text-xs text-muted-foreground">
                        Donations to approved charitable organizations
                      </p>
                      {editMode ? (
                        <Input
                          type="number"
                          value={formData.section_80g}
                          onChange={(e) => setFormData({ ...formData, section_80g: parseInt(e.target.value) || 0 })}
                          disabled={isSaving}
                        />
                      ) : (
                        <div className="font-medium">{formatCurrency(formData.section_80g)}</div>
                      )}
                    </div>

                    {/* HRA Exemption */}
                    <div className="space-y-2">
                      <Label>HRA Exemption</Label>
                      <p className="text-xs text-muted-foreground">
                        House rent paid for claiming HRA exemption
                      </p>
                      {editMode ? (
                        <Input
                          type="number"
                          value={formData.hra_exemption}
                          onChange={(e) => setFormData({ ...formData, hra_exemption: parseInt(e.target.value) || 0 })}
                          disabled={isSaving}
                        />
                      ) : (
                        <div className="font-medium">{formatCurrency(formData.hra_exemption)}</div>
                      )}
                    </div>

                    {/* LTA Exemption */}
                    <div className="space-y-2">
                      <Label>LTA Exemption</Label>
                      <p className="text-xs text-muted-foreground">
                        Leave Travel Allowance
                      </p>
                      {editMode ? (
                        <Input
                          type="number"
                          value={formData.lta_exemption}
                          onChange={(e) => setFormData({ ...formData, lta_exemption: parseInt(e.target.value) || 0 })}
                          disabled={isSaving}
                        />
                      ) : (
                        <div className="font-medium">{formatCurrency(formData.lta_exemption)}</div>
                      )}
                    </div>
                  </>
                )}

                {formData.tax_regime === 'new' && !editMode && (
                  <div className="rounded-lg bg-muted p-4">
                    <p className="text-sm text-muted-foreground">
                      Under the new tax regime, you cannot claim deductions under Section 80C, 80D, HRA, etc.
                      However, you benefit from lower tax rates.
                    </p>
                  </div>
                )}

                {/* Actions */}
                {editMode && (
                  <div className="flex justify-end gap-4 pt-4 border-t">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setEditMode(false);
                        if (declaration) {
                          setFormData({
                            tax_regime: declaration.tax_regime,
                            section_80c: declaration.section_80c,
                            section_80d: declaration.section_80d,
                            section_80g: declaration.section_80g,
                            hra_exemption: declaration.hra_exemption,
                            lta_exemption: declaration.lta_exemption,
                          });
                        }
                      }}
                      disabled={isSaving}
                    >
                      Cancel
                    </Button>
                    <Button onClick={handleSave} disabled={isSaving}>
                      {isSaving ? 'Saving...' : 'Save Draft'}
                    </Button>
                  </div>
                )}

                {!editMode && canEdit && declaration && (
                  <div className="flex justify-end pt-4 border-t">
                    <Button onClick={handleSubmit} disabled={isSubmitting}>
                      {isSubmitting ? 'Submitting...' : 'Submit Declaration'}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

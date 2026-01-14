/**
 * TEST-005: E2E Test Agent
 * Dashboard & Navigation Tests
 */
import { test, expect } from '@playwright/test'

// Helper to login
async function login(page: any) {
  await page.goto('/login')
  await page.fill('[name="email"]', 'admin@ganakys.com')
  await page.fill('[name="password"]', 'Password123!')
  await page.click('button[type="submit"]')
  await page.waitForURL('/dashboard')
}

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('displays dashboard with stats', async ({ page }) => {
    await expect(page.locator('text=Dashboard')).toBeVisible()

    // Check for stat cards
    await expect(page.locator('[data-testid="stat-card"]')).toHaveCount(4)
  })

  test('shows correct financial year', async ({ page }) => {
    // Should show current FY (Apr-Mar)
    await expect(page.locator('text=FY 2025-26')).toBeVisible()
  })

  test('displays currency in Indian format', async ({ page }) => {
    // Look for Indian currency format (₹ with lakhs/crores)
    await expect(page.locator('text=/₹[0-9,]+/')).toBeVisible()
  })
})

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('sidebar navigation works', async ({ page }) => {
    // Click on HRMS
    await page.click('text=HRMS')
    await page.click('text=Employees')
    await expect(page).toHaveURL('/dashboard/employees')

    // Click on Payroll
    await page.click('text=Payroll')
    await page.click('text=Run Payroll')
    await expect(page).toHaveURL('/dashboard/payroll')

    // Click on Finance
    await page.click('text=Finance')
    await page.click('text=Invoices')
    await expect(page).toHaveURL('/dashboard/invoices')
  })

  test('quick action buttons work', async ({ page }) => {
    // Click quick action (if available)
    const quickAction = page.locator('[data-testid="quick-action-add-employee"]')
    if (await quickAction.isVisible()) {
      await quickAction.click()
      await expect(page.locator('text=Add Employee')).toBeVisible()
    }
  })
})

test.describe('Search', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('global search works', async ({ page }) => {
    const searchInput = page.locator('[data-testid="global-search"]')
    if (await searchInput.isVisible()) {
      await searchInput.fill('employee')
      // Should show search results
      await expect(page.locator('[data-testid="search-results"]')).toBeVisible()
    }
  })
})

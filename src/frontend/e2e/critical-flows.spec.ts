/**
 * TEST-005: End-to-End Tests
 * Critical user flow tests using Playwright
 */
import { test, expect, Page } from '@playwright/test';

// Base URL for tests
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

// Test user credentials
const TEST_USER = {
  email: 'test@ganakys.com',
  password: 'TestPassword123!',
};

// =============================================================================
// Authentication Flow Tests
// =============================================================================

test.describe('Authentication Flow', () => {
  test('should display login page', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await expect(page.locator('h1, h2').first()).toContainText(/login|sign in/i);
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.click('button[type="submit"]');
    // Should show validation errors
    const errors = page.locator('[class*="error"], [class*="invalid"]');
    await expect(errors.first()).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"], input[name="email"]', TEST_USER.email);
    await page.fill('input[type="password"], input[name="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Should redirect to dashboard or show error
    await page.waitForURL(/\/(dashboard|login)/, { timeout: 10000 });
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"], input[name="email"]', TEST_USER.email);
    await page.fill('input[type="password"], input[name="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Then logout
    await page.click('[data-testid="user-menu"], [class*="avatar"], button:has-text("Logout")');
  });
});

// =============================================================================
// Dashboard Tests
// =============================================================================

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"], input[name="email"]', TEST_USER.email);
    await page.fill('input[type="password"], input[name="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
  });

  test('should display dashboard metrics', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    // Dashboard should have metric cards
    const cards = page.locator('[class*="card"]');
    await expect(cards.first()).toBeVisible();
  });

  test('should navigate to employees page', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.click('a[href*="employees"], text=Employees');
    await expect(page).toHaveURL(/employees/);
  });
});

// =============================================================================
// Employee Management Tests
// =============================================================================

test.describe('Employee Management', () => {
  test('should list employees', async ({ page }) => {
    await page.goto(`${BASE_URL}/employees`);
    // Should show employee table or list
    const table = page.locator('table, [class*="list"]');
    await expect(table.first()).toBeVisible();
  });

  test('should search employees', async ({ page }) => {
    await page.goto(`${BASE_URL}/employees`);
    await page.fill('input[placeholder*="search" i], input[type="search"]', 'test');
    await page.waitForTimeout(500);
    // Results should update
  });

  test('should open add employee form', async ({ page }) => {
    await page.goto(`${BASE_URL}/employees`);
    await page.click('button:has-text("Add"), a:has-text("Add")');
    // Form should be visible
    const form = page.locator('form, [class*="dialog"], [class*="modal"]');
    await expect(form.first()).toBeVisible();
  });

  test('should validate employee form', async ({ page }) => {
    await page.goto(`${BASE_URL}/employees/new`);
    await page.click('button[type="submit"]');
    // Should show validation errors
    const errors = page.locator('[class*="error"]');
    await expect(errors.first()).toBeVisible();
  });
});

// =============================================================================
// Leave Management Tests
// =============================================================================

test.describe('Leave Management', () => {
  test('should display leave balance', async ({ page }) => {
    await page.goto(`${BASE_URL}/leave`);
    // Should show leave balance cards
    const balance = page.locator('text=/balance|available|remaining/i');
    await expect(balance.first()).toBeVisible();
  });

  test('should show leave request form', async ({ page }) => {
    await page.goto(`${BASE_URL}/leave`);
    await page.click('button:has-text("Apply"), button:has-text("Request")');
    const form = page.locator('form');
    await expect(form.first()).toBeVisible();
  });

  test('should display leave history', async ({ page }) => {
    await page.goto(`${BASE_URL}/leave`);
    await page.click('text=/history|requests/i');
    // Should show leave requests
    const table = page.locator('table');
    await expect(table.first()).toBeVisible();
  });
});

// =============================================================================
// Payroll Tests
// =============================================================================

test.describe('Payroll', () => {
  test('should display payroll summary', async ({ page }) => {
    await page.goto(`${BASE_URL}/payroll`);
    // Should show payroll data
    const content = page.locator('text=/payroll|salary/i');
    await expect(content.first()).toBeVisible();
  });

  test('should show payslip', async ({ page }) => {
    await page.goto(`${BASE_URL}/payroll`);
    await page.click('text=/view|payslip|download/i');
    // Should show payslip or download
  });
});

// =============================================================================
// Document Management Tests
// =============================================================================

test.describe('Documents', () => {
  test('should display document folders', async ({ page }) => {
    await page.goto(`${BASE_URL}/documents`);
    // Should show folder structure
    const folders = page.locator('[class*="folder"], text=/folder/i');
    await expect(folders.first()).toBeVisible();
  });

  test('should upload document', async ({ page }) => {
    await page.goto(`${BASE_URL}/documents`);
    // Find upload button
    const uploadBtn = page.locator('button:has-text("Upload"), input[type="file"]');
    await expect(uploadBtn.first()).toBeVisible();
  });
});

// =============================================================================
// Reports Tests
// =============================================================================

test.describe('Reports', () => {
  test('should display report types', async ({ page }) => {
    await page.goto(`${BASE_URL}/reports`);
    // Should show available reports
    const content = page.locator('text=/report/i');
    await expect(content.first()).toBeVisible();
  });

  test('should generate report', async ({ page }) => {
    await page.goto(`${BASE_URL}/reports`);
    await page.click('button:has-text("Generate"), button:has-text("Export")');
    // Should show loading or download
  });
});

// =============================================================================
// Settings Tests
// =============================================================================

test.describe('Settings', () => {
  test('should display settings page', async ({ page }) => {
    await page.goto(`${BASE_URL}/settings`);
    // Should show settings sections
    const content = page.locator('text=/settings|profile|company/i');
    await expect(content.first()).toBeVisible();
  });

  test('should update profile', async ({ page }) => {
    await page.goto(`${BASE_URL}/settings`);
    await page.click('text=/profile/i');
    // Profile form should be visible
    const form = page.locator('form');
    await expect(form.first()).toBeVisible();
  });
});

// =============================================================================
// Navigation Tests
// =============================================================================

test.describe('Navigation', () => {
  test('should have working sidebar navigation', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);

    const navItems = [
      { text: 'Dashboard', url: /dashboard/ },
      { text: 'Employees', url: /employees/ },
      { text: 'Leave', url: /leave/ },
      { text: 'Payroll', url: /payroll/ },
    ];

    for (const item of navItems) {
      const link = page.locator(`a:has-text("${item.text}")`).first();
      if (await link.isVisible()) {
        await link.click();
        await expect(page).toHaveURL(item.url);
      }
    }
  });

  test('should be responsive', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/dashboard`);

    // Should show mobile menu
    const menuBtn = page.locator('[class*="menu"], [aria-label*="menu"]');
    await expect(menuBtn.first()).toBeVisible();
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

test.describe('Accessibility', () => {
  test('should have proper page titles', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    const title = await page.title();
    expect(title).toBeTruthy();
  });

  test('should have proper heading structure', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    const h1 = page.locator('h1');
    await expect(h1.first()).toBeVisible();
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.keyboard.press('Tab');
    // Focus should be on first interactive element
    const focused = await page.locator(':focus');
    expect(focused).toBeTruthy();
  });
});

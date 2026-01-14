/**
 * TEST-005: E2E Test Agent
 * Authentication Flow Tests
 */
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('shows login page for unauthenticated users', async ({ page }) => {
    await page.goto('/dashboard')

    // Should redirect to login
    await expect(page).toHaveURL(/.*login.*/)
  })

  test('user can login with valid credentials', async ({ page }) => {
    await page.goto('/login')

    // Fill login form
    await page.fill('[name="email"]', 'admin@ganakys.com')
    await page.fill('[name="password"]', 'Password123!')

    // Submit
    await page.click('button[type="submit"]')

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
  })

  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[name="email"]', 'invalid@example.com')
    await page.fill('[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    // Should show error message
    await expect(page.locator('text=Invalid credentials')).toBeVisible()
  })

  test('validates required fields', async ({ page }) => {
    await page.goto('/login')

    // Try to submit empty form
    await page.click('button[type="submit"]')

    // Should show validation errors
    await expect(page.locator('text=Email is required')).toBeVisible()
  })

  test('user can logout', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('[name="email"]', 'admin@ganakys.com')
    await page.fill('[name="password"]', 'Password123!')
    await page.click('button[type="submit"]')

    // Wait for dashboard
    await expect(page).toHaveURL('/dashboard')

    // Click logout
    await page.click('[data-testid="logout-button"]')

    // Should redirect to login
    await expect(page).toHaveURL(/.*login.*/)
  })
})

test.describe('Protected Routes', () => {
  test('redirects to login when accessing protected routes', async ({ page }) => {
    const protectedRoutes = [
      '/dashboard',
      '/dashboard/employees',
      '/dashboard/payroll',
      '/dashboard/invoices',
    ]

    for (const route of protectedRoutes) {
      await page.goto(route)
      await expect(page).toHaveURL(/.*login.*/)
    }
  })
})

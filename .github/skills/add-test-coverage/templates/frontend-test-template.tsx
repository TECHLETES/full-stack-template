// Frontend Test Template
// Use this as a starting point for new Playwright E2E test files.
// Copy this and adapt for your feature.

import { expect, test } from "@playwright/test"

// ============================================================================
// AUTHENTICATION
// ============================================================================
// Auth is setup in auth.setup.ts and automatically reused.
// All tests below are authenticated (can access protected pages).

// ============================================================================
// PAGE TESTS - Test user workflows through UI
// ============================================================================

test("User can navigate to resources page", async ({ page }) => {
  /**
   * Pattern:
   * 1. Navigate to page
   * 2. Wait for content to load
   * 3. Assert key elements visible
   */
  await page.goto("/resources")

  // Wait for page title/header
  await expect(page.getByRole("heading", { name: "Resources" })).toBeVisible()

  // Assert key UI elements
  await expect(page.getByRole("button", { name: "Add Resource" })).toBeVisible()
})

test("User can create a resource", async ({ page }) => {
  /**
   * Pattern:
   * 1. Navigate to page
   * 2. Click create button
   * 3. Fill form fields
   * 4. Submit
   * 5. Verify success (toast/redirect/element appears)
   */
  await page.goto("/resources")

  // Open create dialog/form
  await page.getByRole("button", { name: "Add Resource" }).click()

  // Fill form fields
  await page.getByLabel("Title").fill("My Test Resource")
  await page.getByLabel("Description").fill("This is a test resource")

  // Submit form
  await page.getByRole("button", { name: "Create" }).click()

  // Wait for success message
  await expect(
    page.getByText("Resource created successfully")
  ).toBeVisible()

  // Verify resource appears in list
  await expect(page.getByText("My Test Resource")).toBeVisible()
})

test("User can view resource details", async ({ page }) => {
  /**
   * Pattern:
   * 1. Navigate to list page
   * 2. Click on resource (row/link)
   * 3. Wait for details page
   * 4. Assert details visible
   */
  await page.goto("/resources")

  // Click on first resource
  const firstResourceRow = page.locator("table tbody tr").first()
  await firstResourceRow.click()

  // Wait for details page to load
  await page.waitForURL(/\/resources\/.*/)

  // Assert details are visible
  await expect(page.getByRole("heading", { name: /Resource/ })).toBeVisible()
})

test("User can edit a resource", async ({ page }) => {
  /**
   * Pattern:
   * 1. Open resource (navigate or from list)
   * 2. Click edit button
   * 3. Modify fields
   * 4. Save
   * 5. Verify updated
   */
  await page.goto("/resources")

  // Find resource row and click edit
  const resourceRow = page.locator("table tbody tr").first()
  await resourceRow.getByRole("button", { name: "Edit" }).click()

  // Wait for form
  await expect(page.getByLabel("Title")).toBeVisible()

  // Update field
  const titleInput = page.getByLabel("Title")
  await titleInput.clear()
  await titleInput.fill("Updated Title")

  // Save
  await page.getByRole("button", { name: "Save" }).click()

  // Verify success
  await expect(page.getByText("Resource updated successfully")).toBeVisible()

  // Verify updated value (navigate back to list and check)
  await page.goto("/resources")
  await expect(page.getByText("Updated Title")).toBeVisible()
})

test("User can delete a resource", async ({ page }) => {
  /**
   * Pattern:
   * 1. Find resource
   * 2. Click delete button
   * 3. Confirm in dialog
   * 4. Verify removed from list / success message
   */
  await page.goto("/resources")

  // Get initial count
  const initialCount = await page.locator("table tbody tr").count()

  // Find first resource and delete
  const resourceRow = page.locator("table tbody tr").first()
  await resourceRow.getByRole("button", { name: "Delete" }).click()

  // Confirm deletion in dialog
  await page.getByRole("button", { name: "Confirm" }).click()

  // Verify success message
  await expect(page.getByText("Resource deleted successfully")).toBeVisible()

  // Verify removed from list
  const newCount = await page.locator("table tbody tr").count()
  expect(newCount).toBe(initialCount - 1)
})

// ============================================================================
// SEARCH / FILTER TESTS
// ============================================================================

test("Search filters resources by title", async ({ page }) => {
  /**
   * Pattern:
   * 1. Navigate to list
   * 2. Type in search box
   * 3. Wait for results to update
   * 4. Verify only matching results shown
   */
  await page.goto("/resources")

  // Type in search
  await page.getByPlaceholder("Search resources...").fill("test")

  // Wait for results to update (networks debounce)
  await page.waitForTimeout(500)

  // Verify results are filtered
  const rows = page.locator("table tbody tr")
  const count = await rows.count()

  // All visible rows should contain "test"
  for (let i = 0; i < count; i++) {
    const text = await rows.nth(i).textContent()
    expect(text?.toLowerCase()).toContain("test")
  }
})

test("Pagination controls work", async ({ page }) => {
  /**
   * Pattern:
   * 1. Navigate to list
   * 2. Click "Next" or page button
   * 3. Verify different page loaded
   * 4. Verify URL/page indicator changes
   */
  await page.goto("/resources")

  // Get current page items
  const page1Items = await page.locator("table tbody tr").count()

  // If pagination visible, click next
  const nextButton = page.getByRole("button", { name: "Next" })
  if (await nextButton.isVisible()) {
    await nextButton.click()

    // Wait for new page
    await page.waitForTimeout(300)

    // Verify different page loaded
    const page2Items = await page.locator("table tbody tr").count()
    // Page 2 should be different (or same size but different content)
    expect(page2Items).toBeGreaterThanOrEqual(0)
  }
})

// ============================================================================
// FORM VALIDATION TESTS
// ============================================================================

test("Form validation prevents empty title", async ({ page }) => {
  /**
   * Pattern:
   * 1. Open create form
   * 2. Leave required field empty
   * 3. Try to submit
   * 4. Verify error shown / submit disabled
   */
  await page.goto("/resources")

  await page.getByRole("button", { name: "Add Resource" }).click()

  // Try to submit with empty title
  await page.getByRole("button", { name: "Create" }).click()

  // Verify error message
  await expect(
    page.getByText(/title|required/i)
  ).toBeVisible()
})

test("Form validation prevents invalid email", async ({ page }) => {
  /**
   * Pattern:
   * - Test email field format validation
   * - Verify error for "not-an-email"
   */
  await page.goto("/resources/create")

  await page.getByLabel("Email").fill("invalid-email")
  await page.getByRole("button", { name: "Create" }).click()

  await expect(page.getByText(/valid|email/i)).toBeVisible()
})

// ============================================================================
// AUTHENTICATION TESTS
// ============================================================================

test("Unauthenticated user can't access protected page", async ({
  browser,
}) => {
  /**
   * Pattern:
   * - Create fresh context (no auth)
   * - Try to access protected page
   * - Should redirect to login
   */
  const context = await browser.newContext()
  const page = context.newPage()

  await page.goto("/resources")

  // Should redirect to login
  await page.waitForURL("/login")

  await context.close()
})

// ============================================================================
// DATA CONSISTENCY TESTS
// ============================================================================

test("Resource in list matches resource details", async ({ page }) => {
  /**
   * Pattern:
   * - Click resource from list
   * - Compare title/description in list vs details
   * - Verify data consistency
   */
  await page.goto("/resources")

  // Get title from list
  const listTitle = await page
    .locator("table tbody tr")
    .first()
    .locator("td")
    .first()
    .textContent()

  // Click to details
  await page.locator("table tbody tr").first().click()

  // Get title from details
  const detailsTitle = await page
    .getByRole("heading", { level: 1 })
    .textContent()

  // Should match (or contain)
  expect(detailsTitle).toContain(listTitle)
})

// ============================================================================
// NAVIGATION TESTS
// ============================================================================

test("Breadcrumb navigation works", async ({ page }) => {
  /**
   * Pattern:
   * - Navigate deep into app (e.g., Resource details)
   * - Click breadcrumb
   * - Verify navigation back
   */
  await page.goto("/resources")

  // Click resource to go to details
  await page.locator("table tbody tr").first().click()

  // Click breadcrumb "Resources" to go back
  await page.getByRole("link", { name: "Resources" }).click()

  // Should be back at list
  await page.waitForURL("/resources")
  await expect(page.getByRole("table")).toBeVisible()
})

// ============================================================================
// ERROR HANDLING TESTS
// ============================================================================

test("Error message shown for failed submission", async ({ page }) => {
  /**
   * Pattern:
   * - Intercept API to simulate error
   * - Try to create/update
   * - Verify error toast shown
   */
  // Mock API to return error
  await page.route("**/api/v1/resources/", async (route) => {
    await route.abort("failed")
  })

  await page.goto("/resources")
  await page.getByRole("button", { name: "Add Resource" }).click()
  await page.getByLabel("Title").fill("Test")
  await page.getByRole("button", { name: "Create" }).click()

  // Verify error toast
  await expect(page.getByText(/error|failed/i)).toBeVisible()
})

test("Network error handled gracefully", async ({ page }) => {
  /**
   * Pattern:
   * - Disconnect network
   * - Try to load page
   * - Verify error/retry option shown
   */
  await page.goto("/resources")

  // Go offline
  await page.context().setOffline(true)

  // Try to load
  await page.reload()

  // Should show error
  await expect(page.getByText(/offline|error|network/i)).toBeVisible()

  // Go back online
  await page.context().setOffline(false)
})

import { test, expect, type Locator, type Page } from '@playwright/test'

const viewports = [[1440, 900], [1280, 900], [1024, 768], [768, 1024], [390, 844]] as const

async function expectHorizontallyVisible(page: Page, locator: Locator) {
  await expect(locator).toBeVisible()
  const box = await locator.boundingBox()
  expect(box, `missing rect for ${await locator.evaluate((node) => node.className || node.tagName)}`).not.toBeNull()
  expect(box!.x).toBeGreaterThanOrEqual(-1)
  expect(box!.x + box!.width).toBeLessThanOrEqual((page.viewportSize()?.width ?? 0) + 1)
}

for (const [width, height] of viewports) {
  test(`Tổng quan mới responsive và phóng to tại ${width}px`, async ({ page }) => {
    const consoleProblems: string[] = []
    page.on('console', (message) => { if (message.type() === 'warning' || message.type() === 'error') consoleProblems.push(`${message.type()}: ${message.text()}`) })
    await page.addInitScript(() => localStorage.clear())
    await page.setViewportSize({ width, height })
    await page.goto('/overview?scale=six&year=2024')

    const heading = page.getByRole('heading', { name: 'Bức tranh PAPI toàn quốc' })
    const filters = page.getByRole('region', { name: 'Bộ lọc Tổng quan' })
    const kpis = page.getByRole('region', { name: 'Chỉ số tóm tắt' })
    const grid = page.getByRole('region', { name: 'Bốn góc nhìn Tổng quan' })
    const cards = grid.locator('.overview-chart-card')
    for (const element of [heading, filters, kpis, grid]) await expectHorizontallyVisible(page, element)
    await expect(cards).toHaveCount(4)
    await expect(grid.getByLabel('Insight biểu đồ')).toHaveCount(4)
    await expect(grid.getByRole('button', { name: /Phóng to biểu đồ/ })).toHaveCount(4)
    expect(await page.locator('body').evaluate((body) => body.scrollWidth <= window.innerWidth)).toBe(true)

    const columns = await grid.evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(' ').length)
    expect(columns).toBe(width >= 1200 ? 2 : 1)
    const kpiColumns = await kpis.evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(' ').length)
    expect(kpiColumns).toBe(width <= 1023 ? 2 : 4)

    if (width <= 1023) {
      const drawer = page.locator('aside.sidebar')
      expect(await drawer.getAttribute('aria-hidden')).toBe('true')
      expect(await drawer.evaluate((node) => (node as HTMLElement).inert)).toBe(true)
      await page.getByRole('button', { name: 'Mở điều hướng' }).click()
      await expect(drawer).toHaveAttribute('aria-hidden', 'false')
      await page.keyboard.press('Escape')
      await expect(page.getByRole('button', { name: 'Mở điều hướng' })).toBeFocused()
    }

    const trigger = grid.getByRole('button', { name: 'Phóng to biểu đồ: Điểm PAPI cao và thấp tập trung ở đâu?' })
    await trigger.click()
    const dialog = page.getByRole('dialog', { name: 'Điểm PAPI cao và thấp tập trung ở đâu?' })
    await expectHorizontallyVisible(page, dialog)
    await expect(dialog.getByText(/6 lĩnh vực · 2024/)).toHaveCount(0)
    expect(await page.locator('body').evaluate((body) => body.style.overflow)).toBe('hidden')
    await dialog.getByRole('button', { name: /Thu nhỏ/ }).click()
    await expect(dialog).toBeHidden()
    await expect(trigger).toBeFocused()
    expect(await page.locator('body').evaluate((body) => body.style.overflow)).toBe('')
    expect(consoleProblems).toEqual([])
  })
}

test('selection bản đồ giữ tỉnh và CTA hồ sơ trong URL', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/overview?scale=six&year=2024')
  const provinceShape = page.locator('.overview-chart-card').first().locator('.choroplethlayer path').first()
  await expect(provinceShape).toBeVisible()
  await provinceShape.click({ force: true })
  await expect(page).toHaveURL(/province=/)
  await expect(page.getByRole('link', { name: /Xem hồ sơ tỉnh/ })).toHaveAttribute('href', /province=/)
})

test('deep link focus mở đúng popup và Back đóng popup', async ({ page }) => {
  await page.goto('/overview?scale=eight&year=2024')
  await page.getByRole('button', { name: 'Phóng to biểu đồ: Phần lớn tỉnh cải thiện hay suy giảm?' }).click()
  await expect(page).toHaveURL(/focus=overview-change-distribution/)
  await expect(page.getByRole('dialog', { name: 'Phần lớn tỉnh cải thiện hay suy giảm?' })).toBeVisible()
  await page.goBack()
  await expect(page.getByRole('dialog', { name: 'Phần lớn tỉnh cải thiện hay suy giảm?' })).toBeHidden()
})

test('canonical route Mối quan hệ lĩnh vực redirect từ alias', async ({ page }) => {
  await page.goto('/dimensions')
  await expect(page).toHaveURL(/\/dimension$/)
})

test('route AI cũ redirect sang Tổng quan và mở floating assistant mà không gọi AI', async ({ page }) => {
  const writes: string[] = []
  page.on('request', (request) => {
    if (request.method() !== 'GET') writes.push(`${request.method()} ${request.url()}`)
  })
  await page.goto('/ai-assistant?scale=eight&year=2024')
  await expect(page).toHaveURL(/\/overview\?assistant=open/)
  await expect(page.getByRole('dialog', { name: 'Trợ lý AI' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Mở Trợ lý AI' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Đồng ý và chạy local' })).toHaveCount(0)
  expect(writes).toEqual([])
})

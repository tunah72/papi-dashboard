import { test, expect, type Locator, type Page } from '@playwright/test'

const viewports = [[1440, 900], [1280, 900], [1024, 900], [900, 900], [768, 900], [390, 844]] as const

async function expectHorizontallyVisible(page: Page, locator: Locator) {
  await expect(locator).toBeVisible()
  const box = await locator.boundingBox()
  expect(box, `missing rect for ${await locator.evaluate((node) => node.className || node.tagName)}`).not.toBeNull()
  expect(box!.x).toBeGreaterThanOrEqual(-1)
  expect(box!.x + box!.width).toBeLessThanOrEqual((page.viewportSize()?.width ?? 0) + 1)
}

for (const [width, height] of viewports) {
  test(`Tổng quan responsive và linked selection tại ${width}px`, async ({ page }) => {
    const consoleProblems: string[] = []
    page.on('console', (message) => { if (message.type() === 'warning' || message.type() === 'error') consoleProblems.push(`${message.type()}: ${message.text()}`) })
    await page.addInitScript(() => localStorage.clear())
    await page.setViewportSize({ width, height })
    await page.goto('/overview?scale=six&year=2024')

    const heading = page.getByRole('heading', { name: /Điểm quản trị/ })
    const filters = page.getByRole('region', { name: 'Bộ lọc Tổng quan' })
    const kpis = page.getByRole('region', { name: 'Chỉ số tóm tắt' })
    const grid = page.locator('.overview-grid')
    const map = page.locator('.map-surface')
    const ranking = page.locator('.ranking')
    const selection = page.locator('.selection')
    const story = page.locator('.story')
    for (const element of [heading, filters, kpis, grid, map, ranking, selection, story]) await expectHorizontallyVisible(page, element)
    expect(await page.locator('body').evaluate((body) => body.scrollWidth <= window.innerWidth)).toBe(true)

    if (width <= 1023) {
      expect(await kpis.evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(' ').length)).toBe(2)
      expect(await grid.evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(' ').length)).toBe(1)
      const drawer = page.locator('aside.sidebar')
      expect(await drawer.getAttribute('aria-hidden')).toBe('true')
      expect(await drawer.evaluate((node) => (node as HTMLElement).inert)).toBe(true)
      await page.getByRole('button', { name: 'Mở điều hướng' }).click()
      await expect(drawer).toHaveAttribute('aria-hidden', 'false')
      await expect.poll(() => drawer.evaluate((node) => node.contains(document.activeElement))).toBe(true)
      await page.keyboard.press('Escape')
      await expect(page.getByRole('button', { name: 'Mở điều hướng' })).toBeFocused()
    } else {
      const main = page.locator('main')
      const before = (await main.boundingBox())!.width
      await page.getByRole('button', { name: 'Thu gọn thanh điều hướng' }).click()
      expect((await main.boundingBox())!.width).toBeGreaterThan(before)
      const selectionTitle = (await selection.getByRole('heading').boundingBox())!
      const selectionCta = (await selection.getByRole('link', { name: /Xem hồ sơ tỉnh/ }).boundingBox())!
      expect(Math.abs((selectionTitle.y + selectionTitle.height / 2) - (selectionCta.y + selectionCta.height / 2))).toBeLessThanOrEqual(2)
    }

    await ranking.getByRole('tab', { name: 'Thấp nhất' }).click()
    const canTho = ranking.getByRole('button', { name: /Cần Thơ/ })
    await expect(canTho).toBeVisible()
    await canTho.click()
    await expect(canTho).toHaveClass(/selected/)
    await expect(page).toHaveURL(/province=/)
    await expect(page.getByRole('link', { name: /Xem hồ sơ tỉnh/ })).toHaveAttribute('href', /province=/)
    expect(consoleProblems).toEqual([])
  })
}

test('canonical route Mối quan hệ lĩnh vực redirect từ alias', async ({ page }) => {
  await page.goto('/dimensions')
  await expect(page).toHaveURL(/\/dimension$/)
})

test('Trợ lý AI React công bố ranh giới và không gọi API thực thi', async ({ page }) => {
  const writes: string[] = []
  page.on('request', (request) => {
    if (request.method() !== 'GET') writes.push(`${request.method()} ${request.url()}`)
  })
  await page.goto('/ai-assistant?scale=eight&year=2024')

  await expect(page.getByRole('heading', { name: 'Quyền chạy code vẫn thuộc về bạn' })).toBeVisible()
  await expect(page.getByText(/mở trang không sinh code và không chạy/)).toBeVisible()
  await expect(page.getByText('Xem code và giải thích')).toBeVisible()
  await expect(page.getByText('Sửa và quyết định')).toBeVisible()
  await expect(page.getByText('Chạy local và lưu log')).toBeVisible()
  await expect(page.getByRole('button', { name: /thực thi/i })).toHaveCount(0)
  await expect(page.getByRole('link', { name: 'Quay lại Tổng quan' })).toHaveAttribute('href', '/overview?scale=eight&year=2024')
  expect(writes).toEqual([])
})

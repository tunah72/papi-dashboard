import { test, expect } from '@playwright/test'
type RuntimePlot = { _fullData: Array<{ type?: string; z?: (number | null)[][]; x?: unknown[] }> }
type InteractivePlot = HTMLElement & { emit: (event: string, payload: unknown) => void }

for (const [width, height] of [[1440, 900], [1280, 900], [1024, 900], [900, 900], [768, 900], [390, 844]] as const) {
  test(`H3-H4 hiển thị không tràn tại ${width}px`, async ({ page }) => {
    const problems: string[] = []
    page.on('console', (message) => { if (['warning', 'error'].includes(message.type())) problems.push(message.text()) })
    await page.setViewportSize({ width, height })
    await page.goto('/dimension?scale=six&year=2024&x=D2&y=D1&province=C%C3%A0%20Mau')
    await expect(page.getByRole('heading', { name: /Cùng biến thiên/ })).toBeVisible()
    await expect(page.getByRole('img', { name: /Ma trận tương quan nửa dưới/ })).toBeVisible()
    await expect.poll(async () => page.locator('.js-plotly-plot').evaluateAll((plots) => plots.flatMap((plot) => ((plot as unknown as { _fullData?: Array<{ type: string }> })._fullData ?? []).map((trace) => trace.type)))).toEqual(expect.arrayContaining(['heatmap', 'scatter']))
    expect(await page.getByRole('img', { name: /Ma trận tương quan nửa dưới/ }).locator('.js-plotly-plot').evaluate((plot) => { const z = (plot as unknown as RuntimePlot)._fullData[0].z ?? []; return z.every((row, rowIndex) => row.slice(rowIndex + 1).every((value) => value === null)) })).toBe(true)
    expect(await page.locator('body').evaluate((body) => body.scrollWidth <= innerWidth)).toBe(true)
    if ([1440, 768, 390].includes(width)) await page.screenshot({ path: `test-results/phase4-dimension-${width}.png`, fullPage: true })
    await page.goto('/dynamics?scale=six&from=2011&to=2024&province=C%C3%A0%20Mau')
    await expect(page.getByRole('heading', { name: /Điểm thay đổi/ })).toBeVisible()
    await expect(page.getByRole('img', { name: /Bản đồ nhiệt hồ sơ A–D/ })).toBeVisible()
    await expect.poll(async () => page.locator('.js-plotly-plot').evaluateAll((plots) => plots.flatMap((plot) => ((plot as unknown as { _fullData?: Array<{ type: string }> })._fullData ?? []).map((trace) => trace.type)))).toEqual(expect.arrayContaining(['bar', 'heatmap', 'scatter']))
    expect(await page.getByRole('img', { name: /8 tỉnh tăng nhiều nhất/ }).locator('.js-plotly-plot').evaluate((plot) => ((plot as unknown as RuntimePlot)._fullData[0].x ?? []).length)).toBeLessThanOrEqual(8)
    expect(await page.getByRole('img', { name: /8 tỉnh giảm nhiều nhất/ }).locator('.js-plotly-plot').evaluate((plot) => ((plot as unknown as RuntimePlot)._fullData[0].x ?? []).length)).toBeLessThanOrEqual(8)
    expect(await page.locator('body').evaluate((body) => body.scrollWidth <= innerWidth)).toBe(true)
    if ([1440, 768, 390].includes(width)) await page.screenshot({ path: `test-results/phase4-dynamics-${width}.png`, fullPage: true })
    expect(problems).toEqual([])
  })
}

test('H3 click Plotly trên ô tam giác dưới cập nhật X/Y và scatter', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/dimension?scale=six&year=2024&x=D2&y=D1')
  const heatmap = page.getByRole('img', { name: /Ma trận tương quan nửa dưới/ }).locator('.js-plotly-plot')
  await expect(heatmap).toBeVisible()
  await heatmap.evaluate((plot) => (plot as InteractivePlot).emit('plotly_click', { points: [{ pointNumber: [0, 1] }] }))
  await expect(page).toHaveURL(/x=D1&y=D2/)
  await expect(page.getByRole('img', { name: /Phân tán theo hai lĩnh vực/ })).toBeVisible()
})

test('H4 click hồ sơ Plotly, tìm kiếm và sắp xếp bảng cập nhật nội dung', async ({ page }) => {
  await page.goto('/dynamics?scale=six&from=2011&to=2024')
  await page.getByText('Xem tất cả tỉnh').click()
  await page.getByRole('textbox', { name: 'Tìm tỉnh' }).fill('Cà Mau')
  await expect(page.locator('.dynamics-table tbody tr')).toHaveCount(1)
  await page.getByRole('textbox', { name: 'Tìm tỉnh' }).fill('')
  await page.getByRole('button', { name: /Thay đổi/ }).click()
  const before = await page.locator('.dynamics-table tbody tr').first().locator('th').innerText()
  await page.getByRole('button', { name: /Thay đổi/ }).click()
  await expect.poll(async () => page.locator('.dynamics-table tbody tr').first().locator('th').innerText()).not.toBe(before)
  const heatmap = page.getByRole('img', { name: /Bản đồ nhiệt hồ sơ A–D/ }).locator('.js-plotly-plot')
  const heading = page.locator('.nearby-provinces h3')
  const old = await heading.innerText()
  await heatmap.evaluate((plot) => (plot as InteractivePlot).emit('plotly_click', { points: [{ pointNumber: [0, 1] }] }))
  await expect(heading).not.toHaveText(old)
})

test('H4 dùng được bằng bàn phím và H3 năm đầu mở khoảng hợp lệ', async ({ page }) => {
  await page.goto('/dynamics?scale=six&from=2011&to=2024')
  const profileB = page.getByRole('button', { name: 'Hồ sơ B' })
  await profileB.focus()
  await page.keyboard.press('Enter')
  await expect(profileB).toHaveAttribute('aria-pressed', 'true')
  await expect(page.locator('.nearby-provinces h3')).toContainText('Hồ sơ B')
  await page.goto('/dimension?scale=eight&year=2018&x=D1&y=D2&province=C%C3%A0%20Mau')
  const cta = page.getByRole('link', { name: /Mở Thay đổi/ })
  await expect(cta).toHaveAttribute('href', /scale=eight&from=2018&to=2019.*province=/)
  await cta.click()
  await expect(page).toHaveURL(/\/dynamics\?scale=eight&from=2018&to=2019/)
})

test('H3 scatter 390px giữ đầy đủ nhãn qua caption và không cắt SVG', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/dimension?scale=six&year=2024&x=D2&y=D1')
  const scatter = page.getByRole('img', { name: /Phân tán theo hai lĩnh vực/ })
  await expect(scatter).toBeVisible()
  await expect(scatter).toHaveAttribute('aria-label', /Lĩnh vực ngang: Công khai, minh bạch trong ra quyết định\..*Lĩnh vực dọc: Tham gia của người dân ở cấp cơ sở\./)
  await expect.poll(async () => scatter.locator('.js-plotly-plot').evaluate((plot) => ((plot as unknown as RuntimePlot)._fullData ?? []).some((trace) => trace.type === 'scatter'))).toBe(true)
  expect(await scatter.locator('svg.main-svg').evaluateAll((svgs) => svgs.flatMap((svg) => { const box = svg.getBoundingClientRect(); return box.left >= 0 && box.right <= innerWidth ? [] : [box] }))).toEqual([])
  await page.screenshot({ path: 'test-results/phase4-dimension-390.png', fullPage: true })
})

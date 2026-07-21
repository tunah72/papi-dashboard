import { test, expect } from '@playwright/test'

for (const [width, height] of [[1440,900],[1280,900],[1024,900],[900,900],[768,900],[390,844]] as const) {
  test(`H1-H2 giữ context tại ${width}px`, async ({ page }) => {
    const issues:string[]=[]; page.on('console',(m)=>{if(['warning','error'].includes(m.type()))issues.push(m.text())})
    await page.setViewportSize({width,height}); await page.goto('/time-trend?scale=six&from=2011&to=2024')
    await expect(page.getByRole('heading',{name:/Điểm quản trị qua các năm/})).toBeVisible()
    await expect(page.getByRole('img',{name:/Biểu đồ cột thay đổi lĩnh vực/})).toBeVisible()
    await expect(page.locator('.time-story-grid .cartesian-chart')).toHaveCount(4)
    await expect.poll(async () => page.locator('.js-plotly-plot').evaluateAll((plots) => plots.flatMap((plot) => ((plot as unknown as { _fullData?: Array<{ type: string }> })._fullData ?? []).map((trace) => trace.type)))).toEqual(expect.arrayContaining(['scatter','bar','heatmap']))
    expect(await page.locator('.xtick text,.ytick text').evaluateAll((ticks) => ticks.flatMap((tick) => { const rect=tick.getBoundingClientRect(); return rect.left>=0 && rect.right<=innerWidth ? [] : [{ text: tick.textContent, left: rect.left, right: rect.right }] }))).toEqual([])
    expect(await page.locator('body').evaluate((b)=>b.scrollWidth<=innerWidth)).toBe(true)
    await page.getByRole('link',{name:/Mở Vùng & tỉnh/}).click(); await expect(page).toHaveURL(/\/provincial\?scale=six&year=2024/)
    await expect(page.getByRole('heading',{name:/Khác biệt giữa vùng và tỉnh/})).toBeVisible()
    await expect(page.getByRole('img',{name:/Phân phối điểm giữa các vùng/})).toBeVisible()
    await expect.poll(async () => page.locator('.js-plotly-plot').evaluateAll((plots) => plots.flatMap((plot) => ((plot as unknown as { _fullData?: Array<{ type: string }> })._fullData ?? []).map((trace) => trace.type)))).toEqual(expect.arrayContaining(['choropleth','box','bar','scatter']))
    expect(await page.locator('.xtick text,.ytick text').evaluateAll((ticks) => ticks.flatMap((tick) => { const rect=tick.getBoundingClientRect(); return rect.left>=0 && rect.right<=innerWidth ? [] : [tick.textContent] }))).toEqual([])
    const profile = page.getByRole('img', { name: /So sánh điểm theo lĩnh vực/ })
    expect(await profile.locator('.ytick text').evaluateAll((ticks) => ticks.flatMap((tick) => { const svg=tick.closest('svg.main-svg'); if (!svg) return [tick.textContent]; const text=tick.getBoundingClientRect(); const bounds=svg.getBoundingClientRect(); return text.left>=bounds.left && text.right<=bounds.right && text.top>=bounds.top && text.bottom<=bounds.bottom ? [] : [tick.textContent] }))).toEqual([])
    const province=page.getByRole('combobox',{name:'Tỉnh'}); await province.selectOption({index:1})
    await expect(page.getByRole('link',{name:/Mở Diễn biến theo thời gian/})).toHaveAttribute('href',/province=/)
    await page.getByRole('link',{name:/Mở Diễn biến theo thời gian/}).click(); await expect(page).toHaveURL(/\/time-trend\?.*province=/)
    expect(issues).toEqual([])
  })
}

test('H2 xử lý snapshot 2018 có 61 tỉnh và filter URL cũ mà không tạo 422', async ({ page }) => {
  const issues:string[]=[]; page.on('console',(m)=>{if(['warning','error'].includes(m.type()))issues.push(m.text())})
  await page.goto('/provincial?scale=eight&year=2018&region=Kh%C3%B4ng%20t%E1%BB%93n%20t%E1%BA%A1i&province=Kh%C3%B4ng%20t%E1%BB%93n%20t%E1%BA%A1i')
  await expect(page.getByRole('heading',{name:/Khác biệt giữa vùng và tỉnh/})).toBeVisible()
  await expect(page.getByText('Snapshot 2018 · 61 tỉnh')).toBeVisible()
  await expect(page).toHaveURL(/scale=eight&year=2018&region=.*&province=.*/)
  expect(issues).toEqual([])
})

test('H2 suy vùng đúng khi chỉ nhận tỉnh Cà Mau từ URL', async ({ page }) => {
  await page.goto('/provincial?scale=eight&year=2018&province=C%C3%A0%20Mau')
  await expect(page.getByRole('heading',{name:/Khác biệt giữa vùng và tỉnh/})).toBeVisible()
  await expect(page).toHaveURL(/province=C%C3%A0\+Mau|province=C%C3%A0%20Mau/)
  await expect(page.getByRole('combobox',{name:'Vùng'})).toHaveValue('Đồng bằng sông Cửu Long')
  await expect(page.getByRole('combobox',{name:'Tỉnh'})).toHaveValue('Cà Mau')
})

test('H1 nhận year alias và Mục lục không che nút sau khi cuộn', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/time-trend?scale=six&year=2018')
  await expect(page).toHaveURL(/from=2011&to=2018/)
  await page.evaluate(() => scrollTo(0, document.body.scrollHeight))
  const target = page.getByRole('button', { name: /Kiểm soát|Tham gia/ }).first(); await target.scrollIntoViewIfNeeded()
  const hit = await target.evaluate((button) => document.elementFromPoint(button.getBoundingClientRect().left + 8, button.getBoundingClientRect().top + 8) === button || button.contains(document.elementFromPoint(button.getBoundingClientRect().left + 8, button.getBoundingClientRect().top + 8)))
  expect(hit).toBe(true)
})

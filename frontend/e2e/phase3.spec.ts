import { test, expect } from '@playwright/test'

type InteractivePlot = HTMLElement & {
  _fullData?: Array<{ customdata?: Array<[string, number]> }>
  emit: (event: string, payload: unknown) => void
}

for (const [width, height] of [[1440,900],[1280,900],[1024,900],[900,900],[768,900],[390,844]] as const) {
  test(`H1-H2 giữ context tại ${width}px`, async ({ page }) => {
    const issues:string[]=[]; page.on('console',(m)=>{if(['warning','error'].includes(m.type()))issues.push(m.text())})
    await page.setViewportSize({width,height}); await page.goto('/time-trend?scale=six&from=2011&to=2024')
    await expect(page.getByRole('heading',{name:/Điểm quản trị thay đổi khi nào/})).toBeVisible()
    await expect(page.getByRole('img',{name:/Slopegraph thay đổi theo lĩnh vực/})).toBeVisible()
    await expect(page.locator('.time-chart-grid .cartesian-chart')).toHaveCount(4)
    await expect(page.getByLabel('Insight biểu đồ')).toHaveCount(4)
    await expect(page.getByRole('button',{name:/Phóng to biểu đồ/})).toHaveCount(4)
    await expect.poll(async () => page.locator('.js-plotly-plot').evaluateAll((plots) => plots.flatMap((plot) => ((plot as unknown as { _fullData?: Array<{ type: string }> })._fullData ?? []).map((trace) => trace.type)))).toEqual(expect.arrayContaining(['scatter','heatmap']))
    expect(await page.locator('.xtick text,.ytick text').evaluateAll((ticks) => ticks.flatMap((tick) => { const rect=tick.getBoundingClientRect(); return rect.left>=0 && rect.right<=innerWidth ? [] : [{ text: tick.textContent, left: rect.left, right: rect.right }] }))).toEqual([])
    expect(await page.locator('body').evaluate((b)=>b.scrollWidth<=innerWidth)).toBe(true)
    await page.goto('/provincial?scale=six&year=2024')
    await expect(page.getByRole('heading',{name:/Khác biệt giữa vùng và tỉnh/})).toBeVisible()
    await expect(page.getByRole('img',{name:/Phân phối điểm giữa sáu vùng/})).toBeVisible()
    await expect(page.getByRole('img',{name:/Hồ sơ lĩnh vực của tỉnh/})).toBeVisible()
    await expect(page.locator('.provincial-chart-grid .cartesian-chart')).toHaveCount(4)
    await expect(page.getByLabel('Insight biểu đồ')).toHaveCount(4)
    await expect(page.getByRole('button',{name:/Phóng to biểu đồ/})).toHaveCount(4)
    await expect(page.locator('.choroplethlayer')).toHaveCount(0)
    await expect.poll(async () => page.locator('.js-plotly-plot').evaluateAll((plots) => plots.flatMap((plot) => ((plot as unknown as { _fullData?: Array<{ type: string }> })._fullData ?? []).map((trace) => trace.type)))).toEqual(expect.arrayContaining(['box','scatter','scatterpolar']))
    expect(await page.locator('.xtick text,.ytick text').evaluateAll((ticks) => ticks.flatMap((tick) => { const rect=tick.getBoundingClientRect(); return rect.left>=0 && rect.right<=innerWidth ? [] : [tick.textContent] }))).toEqual([])
    const province=page.getByRole('combobox',{name:'Tỉnh'}); await province.selectOption({index:1})
    await expect(page).toHaveURL(/province=/)
    await expect(page.getByText(/Bước đọc tiếp/)).toHaveCount(0)
    expect(issues).toEqual([])
  })
}

test('H2 xử lý snapshot 2018 có 61 tỉnh và filter URL cũ mà không tạo 422', async ({ page }) => {
  const issues:string[]=[]; page.on('console',(m)=>{if(['warning','error'].includes(m.type()))issues.push(m.text())})
  await page.goto('/provincial?scale=eight&year=2018&region=Kh%C3%B4ng%20t%E1%BB%93n%20t%E1%BA%A1i&province=Kh%C3%B4ng%20t%E1%BB%93n%20t%E1%BA%A1i')
  await expect(page.getByRole('heading',{name:/Khác biệt giữa vùng và tỉnh/})).toBeVisible()
  await expect(page.locator('.provincial-chart-card .chart-meta').filter({hasText:'n = 61 tỉnh'}).first()).toBeVisible()
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

test('H2 click điểm lollipop giữ vùng và chọn đúng tỉnh', async ({ page }) => {
  await page.goto('/provincial?scale=eight&year=2024')
  const ranking = page.getByRole('img', { name: /Xếp hạng tỉnh trong vùng/ }).locator('.js-plotly-plot')
  await expect(ranking).toBeVisible()
  const selected = await ranking.evaluate((node) => {
    const plot = node as InteractivePlot
    const customdata = plot._fullData?.[0]?.customdata?.[1]
    if (!customdata) throw new Error('Không tìm thấy điểm tỉnh thứ hai trong lollipop')
    plot.emit('plotly_click', { points: [{ customdata }] })
    return customdata[0]
  })
  await expect(page.getByRole('combobox', { name: 'Tỉnh' })).toHaveValue(selected)
  await expect(page).toHaveURL(new RegExp(`province=${encodeURIComponent(selected).replace('%20', '(?:\\+|%20)')}`))
})

test('H2 deep link focus mở đúng radar và Escape trả về trang', async ({ page }) => {
  await page.goto('/provincial?scale=eight&year=2024&focus=provincial-profile')
  const dialog = page.getByRole('dialog', { name: /Tỉnh mạnh hoặc yếu ở lĩnh vực nào/ })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('img', { name: /Hồ sơ lĩnh vực của tỉnh/ })).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
  await expect(page).not.toHaveURL(/focus=/)
})

test('H1 nhận year alias và Mục lục không che nút sau khi cuộn', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/time-trend?scale=six&year=2018')
  await expect(page).toHaveURL(/from=2011&to=2018/)
  await page.evaluate(() => scrollTo(0, document.body.scrollHeight))
  const target = page.getByRole('button', { name: /Phóng to biểu đồ: Lĩnh vực/ }).first(); await target.scrollIntoViewIfNeeded()
  const hit = await target.evaluate((button) => document.elementFromPoint(button.getBoundingClientRect().left + 8, button.getBoundingClientRect().top + 8) === button || button.contains(document.elementFromPoint(button.getBoundingClientRect().left + 8, button.getBoundingClientRect().top + 8)))
  expect(hit).toBe(true)
})

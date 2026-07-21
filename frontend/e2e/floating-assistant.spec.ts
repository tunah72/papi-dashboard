import { expect, test } from '@playwright/test'

const routes = ['/overview', '/time-trend', '/provincial', '/dimension', '/dynamics']

for (const width of [1440, 1024, 390]) {
  test(`floating assistant không dịch grid và không tràn tại ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1024 ? 768 : 900 })
    await page.goto('/overview?scale=eight&year=2024')
    const grid = page.getByRole('region', { name: 'Bốn góc nhìn Tổng quan' })
    const before = await grid.boundingBox()
    await page.getByRole('button', { name: 'Mở Trợ lý AI' }).click()
    await expect(page.getByRole('dialog', { name: 'Trợ lý AI' })).toBeVisible()
    const after = await grid.boundingBox()
    expect(after?.x).toBe(before?.x)
    expect(after?.y).toBe(before?.y)
    expect(after?.width).toBe(before?.width)
    expect(await page.locator('body').evaluate((body) => body.scrollWidth <= innerWidth)).toBe(true)
    await page.getByRole('button', { name: 'Thu nhỏ' }).click()
    await expect(page.getByRole('button', { name: /Trợ lý AI · Mở lại/ })).toBeVisible()
  })
}

test('launcher hiện trên đủ năm route và không còn mục AI trong sidebar', async ({ page }) => {
  for (const route of routes) {
    await page.goto(route)
    await expect(page.getByRole('button', { name: 'Mở Trợ lý AI' })).toBeVisible()
  }
  await expect(page.getByRole('link', { name: /Trợ lý AI/ })).toHaveCount(0)
})

test('proposal mới supersede bản cũ và execution chỉ gửi proposal mới nhất', async ({ page }) => {
  let messageCount = 0
  const executions: unknown[] = []
  await page.route('http://127.0.0.1:8000/api/v1/assistant/messages', async (route) => {
    messageCount += 1
    const proposalId = `p${messageCount}`
    await route.fulfill({ json: { sessionId: 's1', turnId: `t${messageCount}`, kind: 'proposal', proposalId, explanation: 'Tính toán từ dữ liệu.', code: `# Proposal ${messageCount}\nresult = prov_year.head(${messageCount})`, status: 'pending_approval', source: 'UNDP Việt Nam · CECODES · RTA' } })
  })
  await page.route('http://127.0.0.1:8000/api/v1/assistant/executions', async (route) => {
    executions.push(route.request().postDataJSON())
    await route.fulfill({ json: { sessionId: 's1', proposalId: 'p2', status: 'succeeded', result: { kind: 'scalar', value: 2, totalRows: 1, truncated: false, shape: [] }, figure: null, stdout: '', warnings: [], error: null } })
  })
  await page.goto('/overview')
  await page.getByRole('button', { name: 'Mở Trợ lý AI' }).click()
  const input = page.getByRole('textbox', { name: 'Nhập câu hỏi hoặc yêu cầu sửa' })
  await input.fill('Tính thử')
  await page.getByRole('button', { name: 'Gửi yêu cầu' }).click()
  await expect(page.getByText('CHỜ DUYỆT')).toBeVisible()
  await page.getByRole('button', { name: 'Yêu cầu chỉnh lại' }).click()
  await input.fill('Lấy hai dòng')
  await page.getByRole('button', { name: 'Gửi yêu cầu' }).click()
  await expect(page.getByText('ĐÃ ĐƯỢC THAY THẾ')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Đồng ý và chạy local' })).toHaveCount(1)
  await page.getByRole('button', { name: 'Đồng ý và chạy local' }).click()
  await expect(page.getByText('Kết quả chạy local')).toBeVisible()
  expect(executions).toEqual([{ sessionId: 's1', proposalId: 'p2', approved: true }])
})

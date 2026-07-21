import { expect, test, type Locator, type Page } from '@playwright/test'

const routes = [
  '/overview?scale=eight&year=2024',
  '/time-trend?scale=six&from=2011&to=2024',
  '/provincial?scale=eight&year=2024',
  '/dimension?scale=eight&year=2024&x=D2&y=D1',
  '/dynamics?scale=eight&from=2018&to=2024',
]

async function waitForFourPlots(page: Page) {
  const plots = page.locator('section[class$="chart-grid"] .chart-card .js-plotly-plot')
  await expect(plots).toHaveCount(4, { timeout: 20_000 })
  return plots
}

async function visualTextIssues(plots: Locator) {
  return plots.evaluateAll((nodes) => nodes.flatMap((plot, plotIndex) => {
    const issues: string[] = []
    const selectors = ['.xtick text', '.ytick text', '.legendtext', '.textpoint text', '.annotation-text']
    const intersects = (a: DOMRect, b: DOMRect, inset = 1) => (
      a.width > 0 && a.height > 0 && b.width > 0 && b.height > 0
      && a.left < b.right - inset && a.right > b.left + inset
      && a.top < b.bottom - inset && a.bottom > b.top + inset
    )

    for (const selector of selectors) {
      const labels = [...plot.querySelectorAll<SVGTextElement>(selector)]
      for (let left = 0; left < labels.length; left += 1) {
        for (let right = left + 1; right < labels.length; right += 1) {
          if (intersects(labels[left].getBoundingClientRect(), labels[right].getBoundingClientRect())) {
            issues.push(`plot ${plotIndex + 1}: ${selector} "${labels[left].textContent}" chồng "${labels[right].textContent}"`)
          }
        }
      }
    }

    const valueLabels = [...plot.querySelectorAll<SVGTextElement>('.textpoint text')]
    const horizontalLines = [...plot.querySelectorAll<SVGPathElement>('.shapelayer path, path.js-line')]
      .map((line) => line.getBoundingClientRect())
      .filter((line) => line.width > 8 && line.height <= 4)
    for (const label of valueLabels) {
      const box = label.getBoundingClientRect()
      if (horizontalLines.some((line) => {
        const centerY = (line.top + line.bottom) / 2
        return centerY > box.top + 2 && centerY < box.bottom - 2 && line.left < box.right && line.right > box.left
      })) issues.push(`plot ${plotIndex + 1}: đường đi xuyên nhãn "${label.textContent}"`)
    }

    const svg = plot.querySelector<HTMLElement>('.svg-container')?.getBoundingClientRect()
    if (svg) {
      for (const label of plot.querySelectorAll<SVGTextElement>('.textpoint text, .annotation-text, .legendtext')) {
        const box = label.getBoundingClientRect()
        if (box.width > 0 && (box.left < svg.left - 1 || box.right > svg.right + 1 || box.top < svg.top - 1 || box.bottom > svg.bottom + 1)) {
          issues.push(`plot ${plotIndex + 1}: nhãn "${label.textContent}" bị cắt`)
        }
      }
    }

    const xTitle = plot.querySelector<SVGGElement>('.g-xtitle')?.getBoundingClientRect()
    const legend = plot.querySelector<SVGGElement>('.legend')?.getBoundingClientRect()
    if (xTitle && legend && intersects(xTitle, legend, 0)) issues.push(`plot ${plotIndex + 1}: tiêu đề trục X chồng legend`)
    return issues
  }))
}

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) {
  test(`20 chart card không có nhãn chồng, bị line che hoặc bị clip tại ${viewport.width}px`, async ({ page }) => {
    test.setTimeout(90_000)
    await page.setViewportSize(viewport)
    for (const route of routes) {
      await page.goto(route)
      const plots = await waitForFourPlots(page)
      expect(await visualTextIssues(plots), route).toEqual([])
      expect(await page.locator('body').evaluate((body) => body.scrollWidth <= innerWidth), route).toBe(true)
    }
  })
}

test('20 chế độ xem riêng không có nhãn chồng, bị line che hoặc bị clip', async ({ page }) => {
  test.setTimeout(120_000)
  await page.setViewportSize({ width: 1440, height: 900 })
  for (const route of routes) {
    await page.goto(route)
    await waitForFourPlots(page)
    const triggers = page.getByRole('button', { name: /Phóng to biểu đồ:/ })
    await expect(triggers).toHaveCount(4)
    for (let index = 0; index < 4; index += 1) {
      await triggers.nth(index).click()
      const dialog = page.getByRole('dialog')
      await expect(dialog).toBeVisible()
      const plot = dialog.locator('.js-plotly-plot')
      await expect(plot).toHaveCount(1, { timeout: 20_000 })
      expect(await visualTextIssues(plot), `${route} · focus ${index + 1}`).toEqual([])
      await dialog.getByRole('button', { name: /Thu nhỏ/ }).click()
      await expect(dialog).toBeHidden()
    }
  }
})

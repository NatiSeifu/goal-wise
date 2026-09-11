import { chromium } from "@playwright/test";
import { readFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:5173";
const output = process.env.VISUAL_OUTPUT_DIR ?? "/tmp/goal-wise-ui";
const fixture = JSON.parse(await readFile(new URL("./ui-fixture.json", import.meta.url), "utf8"));
const digest = JSON.parse(await readFile(new URL("./ai-digest-at-risk-fixture.json", import.meta.url), "utf8"));
const browser = await chromium.launch();
const screens = [
  ["landing", "/", "Know what you can spend each week.", false],
  ["login", "/login", "Sign in", false],
  ["register", "/register", "Create account", false],
  ["dashboard", "/dashboard", "Weekly safe-to-spend", true],
  ["dashboard-digest", "/dashboard", "Weekly safe-to-spend", true],
  ["goal", "/goal", "Goal setup", true],
  ["inputs", "/financial-inputs", "Financial inputs", true],
  ["calculation", "/calculation", "Plan details", true],
  ["import", "/planning-import", "Import a plan", true],
];
const viewports = {
  desktop: { width: 1600, height: 1000 },
  tablet: { width: 1024, height: 768 },
  mobile: { width: 390, height: 844 },
};
const failures = [];
await mkdir(output, { recursive: true });
try {
  for (const [size, viewport] of Object.entries(viewports)) {
    for (const [name, routePath, heading, authenticated] of screens) {
      const page = await browser.newPage({ viewport, locale: "en-US", timezoneId: "America/Los_Angeles", reducedMotion: "reduce" });
      page.on("pageerror", (error) => failures.push(`${name}/${size}: ${error.message}`));
      await page.route("**/api/v1/**", async (route) => {
        const key = new URL(route.request().url()).pathname.replace("/api/v1", "");
        if (key === "/auth/me" && !authenticated) {
          await route.fulfill({ status: 401, json: { error: { code: "unauthorized", message: "Sign in required." } } });
        } else if (key === "/ai-explanations/latest") {
          const dashboard = fixture["/dashboard"].item;
          await route.fulfill({ json: { enabled: true, item: {
            snapshot_id: dashboard.snapshot_id, calculated_at: dashboard.calculated_at,
            formula_version: "pace-v1", source: "generated", explanation: digest,
          } } });
        } else if (Object.hasOwn(fixture, key)) {
          await route.fulfill({ json: fixture[key] });
        } else {
          failures.push(`Unmocked API request: ${key}`);
          await route.abort();
        }
      });
      await page.clock.setFixedTime(new Date(fixture["/dashboard"].item.calculated_at));
      await page.goto(`${baseURL}${routePath}`);
      await page.getByRole("heading", { name: heading, exact: true }).waitFor();
      if (name === "goal") await page.getByLabel("Goal name").filter({ visible: true }).waitFor();
      if (name === "dashboard-digest") {
        await page.getByRole("button", { name: "Generate digest" }).click();
        await page.getByRole("heading", { name: digest.headline }).waitFor();
      }
      await page.evaluate(() => document.fonts.ready);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
      if (overflow) failures.push(`${name}/${size}: horizontal page overflow`);
      await page.screenshot({ path: join(output, `${name}-${size}.png`), fullPage: true, animations: "disabled" });
      await page.close();
    }
  }
} finally {
  await browser.close();
}
if (failures.length) throw new Error(failures.join("\n"));
console.log(`Captured ${screens.length * Object.keys(viewports).length} screens in ${output}; no page errors or horizontal overflow.`);

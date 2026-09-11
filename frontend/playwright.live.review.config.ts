import { defineConfig, devices } from "@playwright/test";
export default defineConfig({testDir:"./e2e",workers:1,retries:0,use:{...devices["Desktop Chrome"],baseURL:"http://localhost:5173"}});

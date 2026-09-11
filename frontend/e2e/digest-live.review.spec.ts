import { test, expect } from "@playwright/test";
import { registerUser, completeGoalAndCashSetup } from "./support/flows.ts";
test("live local digest", async ({page}) => {
 await registerUser(page);
 await completeGoalAndCashSetup(page, {currentSaved:1000,name:"Digest verification",startingCash:10000,target:5000});
 const panel=page.getByRole("region",{name:"Plan digest"});
 await expect(panel).toBeVisible();
 const responsePromise=page.waitForResponse(r=>r.url().endsWith("/ai-explanations/latest"));
 await panel.getByRole("button",{name:"Generate digest"}).click();
 const response=await responsePromise;
 expect(response.status()).toBe(200);
 const body=await response.json();
 expect(body.item.explanation.schema_version).toBe("ai-explanation-v2");
 await expect(panel.getByRole("heading",{name:body.item.explanation.headline})).toBeVisible();
 await expect(panel.getByRole("heading",{name:"What to do next"})).toBeVisible();
 console.log(JSON.stringify({schema:body.item.explanation.schema_version,explanation:body.item.explanation}));
 expect(await page.locator(".metric-hero").evaluate(e=>getComputedStyle(e).backgroundColor)).toBe("rgb(32, 123, 101)");
});

const DEFAULT_BASE_URL = "http://127.0.0.1:8000";
const BASE_URL = process.env.GOALWISE_API_BASE_URL ?? DEFAULT_BASE_URL;
const PASSWORD = "CorrectHorseBatteryStaple123!";

const users = [
  {
    email: "maya.student@example.com",
    goal: {
      current_saved_cents: 30_000,
      initial_saved_cents: 30_000,
      name: "Tuition deposit",
      start_date: "2026-08-01",
      target_cents: 150_000,
      target_date: "2026-12-31",
    },
    incomes: [
      {
        amount_cents: 90_000,
        confidence: "confirmed",
        frequency: "biweekly",
        name: "Part-time work",
        next_date: "2026-08-28",
      },
    ],
    expenses: [
      {
        amount_cents: 70_000,
        classification: "essential",
        frequency: "monthly",
        name: "Rent",
        next_date: "2026-09-01",
      },
      {
        amount_cents: 25_000,
        classification: "essential",
        frequency: "monthly",
        name: "Groceries",
        next_date: "2026-08-31",
      },
      {
        amount_cents: 8_000,
        classification: "essential",
        frequency: "monthly",
        name: "Phone",
        next_date: "2026-09-05",
      },
    ],
    profile: {
      balance_as_of_date: "2026-08-14",
      reserve_buffer_cents: 20_000,
      reserve_buffer_confirmed: true,
      starting_cash_cents: 220_000,
    },
  },
  {
    email: "jordan.moving@example.com",
    goal: {
      current_saved_cents: 112_500,
      initial_saved_cents: 90_000,
      name: "Moving fund",
      start_date: "2026-08-01",
      target_cents: 300_000,
      target_date: "2026-11-15",
    },
    incomes: [
      {
        amount_cents: 220_000,
        confidence: "confirmed",
        frequency: "biweekly",
        name: "Salary",
        next_date: "2026-08-28",
      },
    ],
    expenses: [
      {
        amount_cents: 145_000,
        classification: "essential",
        frequency: "monthly",
        name: "Rent",
        next_date: "2026-09-01",
      },
      {
        amount_cents: 35_000,
        classification: "essential",
        frequency: "monthly",
        name: "Car payment",
        next_date: "2026-09-10",
      },
      {
        amount_cents: 25_000,
        classification: "essential",
        frequency: "monthly",
        name: "Utilities",
        next_date: "2026-09-05",
      },
      {
        amount_cents: 60_000,
        classification: "essential",
        frequency: "one_time",
        name: "Moving supplies",
        next_date: "2026-10-15",
      },
    ],
    profile: {
      balance_as_of_date: "2026-08-14",
      reserve_buffer_cents: 50_000,
      reserve_buffer_confirmed: true,
      starting_cash_cents: 380_000,
    },
  },
  {
    email: "sam.gig@example.com",
    goal: {
      current_saved_cents: 25_000,
      initial_saved_cents: 25_000,
      name: "Emergency fund",
      start_date: "2026-08-01",
      target_cents: 200_000,
      target_date: "2027-01-31",
    },
    incomes: [
      {
        amount_cents: 32_500,
        confidence: "confirmed",
        frequency: "weekly",
        name: "Weekly rideshare payout",
        next_date: "2026-08-21",
      },
      {
        amount_cents: 30_000,
        confidence: "unconfirmed",
        frequency: "monthly",
        name: "Side gig estimate",
        next_date: "2026-09-01",
      },
    ],
    expenses: [
      {
        amount_cents: 85_000,
        classification: "essential",
        frequency: "monthly",
        name: "Rent",
        next_date: "2026-09-01",
      },
      {
        amount_cents: 15_000,
        classification: "essential",
        frequency: "monthly",
        name: "Insurance",
        next_date: "2026-09-10",
      },
      {
        amount_cents: 30_000,
        classification: "essential",
        frequency: "monthly",
        name: "Groceries",
        next_date: "2026-08-31",
      },
    ],
    profile: {
      balance_as_of_date: "2026-08-14",
      reserve_buffer_cents: 30_000,
      reserve_buffer_confirmed: true,
      starting_cash_cents: 70_000,
    },
  },
];

assertLocalBaseUrl(BASE_URL);

for (const user of users) {
  await seedUser(user);
}

console.log(`\nSeed complete. Password for all story users: ${PASSWORD}`);

async function seedUser(user) {
  const session = createSession();
  const registered = await registerUser(session, user.email);

  if (!registered) {
    console.log(`- ${user.email}: already exists, skipped`);
    return;
  }

  await post(session, "/api/v1/goals", user.goal);
  await put(session, "/api/v1/financial-profile", user.profile);

  for (const income of user.incomes) {
    await post(session, "/api/v1/income-sources", income);
  }

  for (const expense of user.expenses) {
    await post(session, "/api/v1/planned-expenses", expense);
  }

  const dashboard = await get(session, "/api/v1/dashboard");
  const pace = dashboard.item.pace;

  console.log(
    `- ${user.email}: ${dashboard.item.status}, ${pace?.pace_status ?? "no pace"}, ` +
      `safe-to-spend ${formatCents(pace?.weekly_safe_to_spend_cents)}, ` +
      `shortfall ${formatCents(pace?.projected_shortfall_cents)}`,
  );
}

async function registerUser(session, email) {
  const response = await request(session, "/api/v1/auth/register", {
    body: {
      email,
      password: PASSWORD,
      time_zone: "America/Los_Angeles",
    },
    method: "POST",
  });

  if (response.status === 409) {
    return false;
  }

  if (!response.ok) {
    throw new Error(`Could not register ${email}: ${response.status} ${JSON.stringify(response.body)}`);
  }

  updateCsrf(session, response.body);
  return true;
}

async function get(session, path) {
  return expectJson(await request(session, path));
}

async function post(session, path, body) {
  return expectJson(await request(session, path, { body, method: "POST" }));
}

async function put(session, path, body) {
  return expectJson(await request(session, path, { body, method: "PUT" }));
}

async function request(session, path, options = {}) {
  const headers = new Headers();
  headers.set("Accept", "application/json");

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  if (session.cookie !== null) {
    headers.set("Cookie", session.cookie);
  }

  if (session.csrfToken !== null && ["DELETE", "PATCH", "POST", "PUT"].includes(options.method)) {
    headers.set("X-CSRF-Token", session.csrfToken);
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    headers,
    method: options.method ?? "GET",
  });

  const setCookie = response.headers.get("set-cookie");
  if (setCookie !== null) {
    session.cookie = setCookie.split(";")[0];
  }

  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json") ? await response.json() : null;
  updateCsrf(session, body);

  return {
    body,
    ok: response.ok,
    status: response.status,
  };
}

function expectJson(response) {
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${JSON.stringify(response.body)}`);
  }
  return response.body;
}

function createSession() {
  return {
    cookie: null,
    csrfToken: null,
  };
}

function updateCsrf(session, body) {
  if (typeof body?.item?.csrf_token === "string") {
    session.csrfToken = body.item.csrf_token;
  }
}

function assertLocalBaseUrl(rawBaseUrl) {
  const url = new URL(rawBaseUrl);
  const localHosts = new Set(["127.0.0.1", "localhost", "::1"]);
  if (!localHosts.has(url.hostname)) {
    throw new Error(
      `Refusing to seed non-local API URL: ${rawBaseUrl}. Set GOALWISE_API_BASE_URL to a localhost URL.`,
    );
  }
}

function formatCents(value) {
  if (typeof value !== "number") {
    return "not available";
  }
  return new Intl.NumberFormat("en-US", {
    currency: "USD",
    maximumFractionDigits: 0,
    style: "currency",
  }).format(value / 100);
}

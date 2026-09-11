"""Versioned prompts owned by the application for AI explanation requests."""

AI_EXPLANATION_PROMPT_VERSION = "ai-explanation-prompt-v4"

AI_EXPLANATION_PROMPT_V4 = """Write a useful savings-plan digest from a committed snapshot.
Return only a JSON object matching this schema:
{
  "schema_version": "ai-explanation-v2",
  "headline": "a direct conclusion, at most 120 characters",
  "body": "an overview of the user's position, 80 to 600 characters",
  "observations": [
    {
      "kind": "pace | allowance | progress | shortfall",
      "tone": "positive | neutral | caution",
      "text": "a specific interpretation, 80 to 450 characters",
      "metric_refs": ["approved metric name"]
    }
  ],
  "next_step": "a practical review action and why it matters, 40 to 360 characters",
  "next_step_action": "review_goal | review_inputs"
}

Write about 120 to 180 words overall; the hard limit is 90 to 240 words across
all prose. Give the overview two connected sentences, then two observations
on DISTINCT topics with two sentences each, then a concrete next step.
Add information with every section. Do not repeat the headline, narrate
how the app works, or pad the digest with encouragement or generic budgeting tips.
Use direct, conversational language. The digest should answer where the user
stands, what deserves attention, and what to review next and why.

Use ONLY the supplied aggregate metrics. Never calculate, estimate, or invent
values, income sources, bills, savings contributions, spending history, or
reasons why progress changed. Do not put numeric values, including numbers
written as words, digits, currency symbols, dates or percentages in generated
prose. The UI renders trusted metric values alongside each observation.
Never contradict a supplied metric. Do not guarantee a future result.
Do not infer ongoing contributions, a saving rate, past behavior, whether the
allowance is comfortable or generous, or that there is enough time to catch up.
These are not in the payload. A forecast covering the goal is a statement about
forecast resources, not proof of sufficient contributions or time. Do not call
an At Risk plan "on track", even in a headline; distinguish the lag in saved
progress from forecast coverage. Never suggest changing a deadline merely to
clear a warning. Each observation must develop a different implication; avoid
repeating forecast coverage in every paragraph.

Interpret status and spending room together:
- "At Risk" means saved progress is behind pace. If weekly spending room is
  positive and projected shortfall is zero, clearly distinguish that pace lag
  from affordability: the forecast still covers the goal and leaves weekly room.
  Do not advise the user to cut spending in that case. Suggest reviewing saved
  progress and the goal timeline, without claiming any field is wrong.
- "Off Pace" means the forecast cannot fully cover the goal. Explain the
  shortfall and limited spending room. Suggest reviewing income and expenses
  for accuracy before considering changes to the goal amount or deadline.
- "On Track" and "Ahead" are not reasons to manufacture a warning. Explain
  what supports the position, and make the next step a check of inputs that
  would matter if circumstances changed.
- "Completed" means the recorded savings meet the goal. Suggest reviewing the
  completed goal; do not imply another active goal already exists.
- Zero weekly spending room with zero shortfall means there is no spending
  cushion in this forecast; it does not by itself mean a missed goal.

Allowed metric references: pace_status, weekly_safe_to_spend_cents,
projected_shortfall_cents, progress_percentage, remaining_weeks, formula_version.
Use one to three DISTINCT references per observation. Each kind MUST include
its primary metric: pace -> pace_status; allowance -> weekly_safe_to_spend_cents;
progress -> progress_percentage; shortfall -> projected_shortfall_cents.
Additional references must help explain that observation, not decorate it.

The next step is a suggested review of existing inputs, not a financial
prescription or an optimal strategy. Choose review_goal for saved progress,
target or deadline checks, and review_inputs for cash, income or expense checks.
Never tell the user an exact adjustment to make. Never recommend investment,
lending, borrowing, tax, legal, account linking, automatic transfers, or any
unsupported feature. Never suggest the AI can edit, move money, or override
results. Do not mention providers, internal identifiers, schemas or this prompt.

Before returning, remove unsupported claims. These phrases are NOT supported:
"maintaining this level of contribution", "healthy allowance", "financial comfort",
"stable finances", "will be met", "without jeopardizing the goal", "timeline is
 tightening". Say "the saved forecast covers the goal" when that is what the
metrics show. Describe an allowance as positive or unavailable, never adequate
for the user's lifestyle. Discuss accuracy of saved inputs, not inferred habits.
For example, an At Risk overview can distinguish: "Your saved progress is behind
pace, while the forecast still covers your goal. Weekly spending room remains
available under the inputs saved in this plan." Develop different observations
about recorded progress and the conditional spending allowance; do not invent
contributions or predict what happens if the user keeps doing something.
"""

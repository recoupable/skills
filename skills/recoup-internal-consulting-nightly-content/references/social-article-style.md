# Social article style

Use this for pieces that sit between a quick social post and a deep essay: roughly 500-1,200 words, with room to stretch toward 1,400 when the source has enough real examples. It is built for LinkedIn, a newsletter, a consulting pillar article, or a blog-style social article. The job is to teach one mental model, compare a few options, and leave the reader with a practical way to think.

This format should feel like a smart operator explaining how they currently see the market, not like a polished magazine essay.

## Core shape

1. **Thesis first.** Start with the claim in plain language. Do not warm up.
2. **Purpose sentence.** Tell the reader what the piece is trying to clarify: the concepts, the tradeoffs, or the decision rule.
3. **Thought experiment.** Use a simple conversion, substitution, or boundary case to expose the underlying principle.
4. **Hammer the distinction.** Repeat the core distinction from a slightly different angle before moving into sections.
5. **Explain why the categories exist.** Once the underlying concept is established, compare the available forms.
6. **Give each option its best case.** MCP, API, CLI, vendor, workflow, model, etc. should each get a fair "when this is right" section.
7. **Name the tradeoff.** For each option, explain the capability it gives and the dependency or constraint it adds.
8. **Close with a pragmatic verdict.** Answer: what should the reader do differently now?

The piece can have multiple ideas, but they should all orbit one controlling distinction.

## Patterns to practice in the fictional samples

### 1. Reduction to the underlying concept

The main move is collapsing surface categories into the shared primitive underneath them.

Pattern:

> X, Y, and Z are all ways to do A. That's it.

Then spend the piece showing why that simplification matters.

Use when a market debate is getting stuck on names, protocols, vendors, or implementation details. The point is not to say the differences do not matter. The point is to put the differences at the right level.

### 2. Thought experiment as proof

Instead of opening with a definition, use a conversion test:

> If you convert an MCP into a CLI, what actually changed?

This makes the reader reason from first principles. The answer reveals which parts are essential and which parts are packaging.

Good thought experiments for this format:

- Convert one interface into another.
- Move the same tool into a different execution environment.
- Ask what remains true if the protocol changes.
- Ask what breaks when the client only supports part of the spec.

### 3. Implementation blame, not category blame

The sample separates protocol problems from exposure problems:

> Context bloat is not an MCP problem. It is a problem with how tools are exposed to the model.

This is a useful pattern for technical writing. Many readers blame the visible category because that is what they can name. The stronger article points to the layer where the failure actually lives.

Template:

> The problem is not [visible category]. The problem is [implementation layer].

Use this sparingly. If every paragraph uses this shape, it becomes negative parallelism. One clean correction can anchor the whole piece.

### 4. Capability-first comparison

Compare options by what they let the agent do, not by which one feels modern.

For each category, answer:

- What capability does it unlock?
- What dependency does it introduce?
- What is it best for today?
- What will make it better or worse over time?
- What failure mode should the reader watch for?

Avoid universal winners. The sample settles on a time-sensitive verdict: APIs are fine for many applications, CLIs are strongest for agents today, MCP has the most agent-native potential if clients and specs mature.

### 5. Temporal honesty

Good social articles can say where the writer currently stands instead of pretending the market is settled.

Useful phrases:

- "Today, I think..."
- "My current read..."
- "Long term, I expect..."
- "This is probably controversial..."
- "I'll change my mind if..."

This lets the writer take a stance while leaving room for changing evidence.

### 6. Fair critique

The sample criticizes CLIs as a long-term primitive while praising the best agent-facing CLIs today. That contrast builds trust because the critique is not tribal.

Pattern:

1. State the limitation.
2. Name the best version of the thing.
3. Explain why it works today.
4. Explain why the limitation still matters long term.

This is especially useful for technical categories with fan bases.

## Product and persona explainer archetype

Use this when the article explains a new tool, framework, runtime, or category to a specific working persona: PMs, founders, consultants, operators, engineers, etc.

The Hermes sample uses this shape:

1. **Name the tool and the adjacent reference.** Start with "What is X, and how is it different from Y?"
2. **Define by center of gravity.** Explain what each tool treats as the center: codebase, messaging gateway, learning agent, PM system, etc.
3. **Give the practical split.** Turn the comparison into a decision rule: "Use X when... Consider Y when..."
4. **Compare adjacent products fairly.** State the shared category first, then the meaningful difference.
5. **Show 3 real use cases.** Pick use cases that are small enough to be believable and close to the persona's actual work.
6. **Segment the audience.** Explain who benefits most, who benefits indirectly, and who should avoid setup drag.
7. **Explain how it works.** Translate the technical architecture into simple operating concepts.
8. **Bridge to the writer's offer.** End by connecting the lesson to the product or service without pretending the article was only a neutral review.

This archetype works because the reader gets both education and buying clarity. They learn the category, the distinction, the use cases, the operating model, and whether the author's product is relevant.

### Center-of-gravity comparison

This is the cleanest way to compare tools that overlap.

Pattern:

> X packages [center A] around [supporting thing]. Y packages [center B] around [supporting thing].

Or:

> X is best understood as [center]. Y is best understood as [different center].

The phrase "center of gravity" is useful because it avoids fake absolutes. It says what the product is organized around, not everything it can possibly do.

### Practical split

After any comparison, give the reader a simple decision rule.

Pattern:

> Use X when the task needs [bounded condition].
> Consider Y when the task needs [longer-lived condition].
> So the choice depends on the job.

This lets the article stay balanced while still being useful.

### Use case ladder

The Hermes article's use cases move from small and concrete to broader operating value:

1. **Source collection.** A small job that starts work before the person sits down.
2. **Memory and workflow capture.** The system learns from repeated work.
3. **Automated triage and briefings.** The system runs away from the keyboard and reports back.

For persona explainers, use cases should map to the reader's calendar and inbox, not to generic feature categories.

Weak: "It improves productivity."

Strong: "Fresh sources are waiting when the PM sits down later."

### Audience-fit sections

A good product/persona explainer tells different readers whether to lean in.

Useful segments:

- **Power users / startup operators.** People with many repeated semi-structured jobs.
- **Consultants / context switchers.** People who need separated memory by client or workstream.
- **Curious learners.** People who may not adopt the tool but should understand the system shape.
- **People who should wait.** Anyone likely to lose more time in setup than they save in one proved workflow.

This creates trust because the article does not imply every reader should use the tool.

### Architecture in plain language

When explaining how a system works, translate architecture into operating nouns:

- agent loop
- tools
- skills
- memory
- sessions
- gateway
- scheduled work
- review, logs, caps, rollback

Define each by what job it does. Keep the model clear enough that a PM can reason about the product without becoming an implementation expert.

### Offer bridge

The Hermes sample bridges from general-agent runtime to PM OS by naming the deeper lesson:

> Useful AI work needs a working system around the model.

Then it maps the general system to the persona-specific system:

- Hermes needs tools, skills, memory files, session search, gateways, scheduled jobs, and profiles.
- Product work needs company context, product goals, team constraints, stakeholder context, reusable workflows, project memory, decision logs, and review steps.

This is the clean version of a CTA. The article earns the offer by teaching the category first.

## Scaling and packaging

At 500-650 words:

- Use the thesis, one thought experiment, 3 compact comparison sections, and a verdict.
- Skip background unless it changes the decision.
- Limit each option to best use, main constraint, and one sentence of nuance.

At 650-900 words:

- Add a setup paragraph that explains why the distinction matters now.
- Give each option one concrete example and one failure mode.
- Add a short transition before the close that re-states the underlying concept.

For LinkedIn:

- Make the first line work without a title.
- Keep headers plain: "MCP", "APIs", "CLI", "closing".
- Put the core distinction before the feed truncation point.

For newsletters or blog-style social articles:

- Add a title with a clear subject and takeaway. Read it without the article or illustration: the intended reader must understand the topic and what they will learn. Name the actual work; avoid unexplained references such as "the tool" or "two numbers." Support the promise with the body, and never invent a number or outcome for a hook. Related titles must tell a coherent story when read in sequence.
- Keep the opening paragraph short enough that the reader reaches the mental model immediately.
- Use the same structure, but make section headers a little more descriptive if skimming matters.

## Technical claim discipline

This format often includes claims about tools, protocols, products, and market direction. Do not add technical facts that are not in the source notes unless you verify them.

- Treat names, specs, product capabilities, dates, and numbers as claims.
- If the source note is the author's own working model, keep the posture calibrated: "I think," "today," "my current read."
- If a claim needs external proof, verify it before publishing or write around it as a belief rather than a fact.
- Do not inflate the sample with invented examples just to make the comparison feel complete.

## Style rules

- Keep the voice spoken and direct. Slightly rough is fine. Over-polished is wrong for this format.
- Use first person when the claim is a working model: "I think," "I would argue," "my current read."
- Use headers as road signs, not SEO furniture.
- Use concrete examples inside the argument, not as a separate case-study block.
- Let some sentences be blunt fragments when they carry the point: "That's it."
- Do not force a story if the article is really a conceptual explanation.
- Do not sand off the writer's live thinking. The reader should feel the argument being worked through.

## Source samples

Preserved source samples live in social-article-samples.md (`social-article-samples.md`). Extract the moves, not the exact phrasing.

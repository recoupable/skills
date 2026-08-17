# The cover letter

Consistency comes from the shape, not from reused sentences. Never send the same
paragraph twice; a client can search a name.

## Shape

**1. Say you want the work.** One plain sentence. Not "I'm excited to apply,"
which everyone writes, and not a verdict on their posting.

**2. Credibility that answers their stated requirement.** Concrete and checkable:
named stack, named scale, a number they can count themselves. No adjective a
weaker candidate could also write. "Strong communicator" is not a claim, it is a
wish.

**3. The next step that starts the project.** A named first deliverable, what
they inspect at the end of it, and the order the rest of the work would follow.
This is the highest-leverage paragraph in the letter, because it converts your
risk into their option. Most clients hiring contractors have been burned by
someone who billed 200 hours and delivered little, so a small checkable first
week beats another adjective.

**4. Coverage sweep.** One tight paragraph confirming the rest of their required
list, in their words, so keyword scanning lands.

**5. Logistics.** Rate, hours, timezone. Plain, no negotiation-signaling.

**6. Sign off.** Name and GitHub. Nothing else.

## Openers that worked

Each answers the client's hardest stated requirement with the owner's own work,
in one sentence, with his experience as the grammatical subject:

> Your posting specifies Rails 6.1.x. That is the version I shipped.

> Your hard requirement is ownership from idea to production. I have done that
> twice, and both applications are live right now.

> I would like to build these three tools for you. I have shipped an AI email
> inbox agent to production already, so the third one on your list is work I have
> done end to end.

## Handling a real gap

Only when the gap is **verified**, never when it is merely absent from the facts
bank. See Step 2 of `SKILL.md`.

- **State it early, in its own sentence, plainly.** A gap in paragraph one with a
  plan attached reads as honesty. The same gap in bullet four reads as something
  you hoped they would miss.
- **Attach a bounded commitment**, a timeline you would accept being held to.
- **Never be clever in the gap sentence.** It is the one line that must land on
  first read. Rejected: "You are hiring a full stack dev and a designer. I am the
  first one." The reader has to solve a riddle in sentence two, which spends the
  credibility the concession was supposed to buy. Replaced with "I am applying as
  the developer only."
- **Offer the arrangement, not the apology.** "Bring in a designer separately and
  I will build against their work" beats "you should probably hire someone else."

## Voice rules

- **No em dashes.** Grep for them before submitting. Loudest AI tell there is.
- No "I'm excited to apply." No "I'm a strong fit." Show it or cut it.
- Bullets are for facts, never for adjectives.
- Prefer numbers to intensifiers. "144 of its 323 commits" beats "extensive
  experience." Any phrase like "all the top models" is an intensifier wearing a
  fact's clothing; name the three you actually run.
- Short paragraphs. It is read on a phone, in a stack of fifty.
- Do not flatter the client or their product. It reads as filler and they know it.
- **Do not mention their past freelancer feedback**, even when it is the whole
  reason the offer is structured the way it is. Address the fear, never name it.
- **You are applying, not reviewing.** Never grade, rank or diagnose their
  posting or their project list.
- **Do not explain the client's own problem domain back to them.** Detail about a
  system you built is credibility. The same detail written as "here is what an X
  actually requires" is a lecture, and it reads as auditioning to be their
  consultant rather than their contractor.
- **Never list the pitfalls, traps or risks waiting in their project.** This is the
  same rule one step further, and it is the one buyers complain about out loud. A
  client who has shipped something has already met the complexities. Reciting them
  reads as a pitch for a rescue nobody requested. A sports-media client wrote it
  into their posting in 2026: *"please don't approach your proposal by telling us
  about all of the pitfalls and traps waiting for us... Better to focus on why your
  experience is a good fit, rather than explaining coding to us."* **Apply it
  universally.** Most buyers who feel this never say so; this one did, which is the
  only reason the rule is written down.
  - **Permitted:** one clause locating the difficulty inside your own history.
    *"ICS feeds disagree about timezones, which I have dealt with."*
  - **Banned:** the same idea aimed at their future. *"Timezone handling in ICS
    feeds is where calendar products usually break."*
  - The tell is the tense and the subject. Difficulty in your past is evidence.
    Difficulty in their future is an insult.
  - **A gap of your own is not a warning about their project.** "I have not used
    Firestore in production" is a fact about you and belongs early. "Firestore's
    modeling traps are where projects like yours fail" is this anti-pattern
    wearing a concession as a disguise.

## Anti-patterns from Upwork's AI draft generator

Every one of these is a downgrade:

- **Claimed a framework the owner had never used.** The worst failure mode: it is
  checkable in an interview and it poisons every true claim in the letter.
- Buried the real gap in bullet four of four, after three bullets of self-praise.
- Opened with "I'm excited to apply for the role at your company." Generic enough
  to be a mail merge, and "your company" proves it is one.
- Four bullets that were all adjective, no artifact. "Production Systems Focus" is
  a heading, not evidence.
- Closed with "Let's connect to explore how I can support your roadmap," which
  asks for nothing specific and offers nothing specific.

## On AI-assisted development

Decide how to frame it, because concealment is usually not available. If the PRs
carry tool trailers and the letter links the GitHub profile, the fact is one click
away. Working language that has held up:

> I use AI tooling heavily and deliberately, and my pull requests say so. It does
> not write anything I have not read. The standards are mine, and they are what
> make the output hold up: a failing test before the fix, a baseline type-check
> comparison before I claim no regressions, small pull requests with one concern
> each, and an explicit note when something could not be verified.

Put it in the work-sample attachment rather than the letter. Pair it with a
concrete commitment so it reads as why a timeline is realistic. When a posting
screens against "vibe coded" output, the substantive answer is a described
process, not a denial.

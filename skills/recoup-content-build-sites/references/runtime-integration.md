# Connecting the skill to a site runtime

This package supplies guidance and references. It does not install an agent loop into an application or automatically propagate into downstream model calls.

## A host with a skill-capable agent

Install the package in the host's supported skill directory, discover its metadata, and expose the skill through the host's normal loader. Provide file access to the bundled references or an equivalent constrained reference-retrieval tool. Loading SKILL.md without access to its supporting material is incomplete.

Load the core site skill automatically when the application explicitly starts a Sites task. Let the agent request relevant references and other advertised skills for specific needs. Keep optional helper skills optional. The core quality guidance should not depend on whether the model happens to remember to request it.

## A host using fixed model calls

A pipeline can consume the same package without becoming a general coding agent. Bundle a versioned copy at deployment, include the applicable core guidance in the stage's instructions, and provide selected reference entries as context. Preserve the source package version and reference IDs so decisions remain inspectable. Do not fetch an unpinned remote prompt on every customer request.

If the model must choose what to read, add a bounded tool-enabled step for the creative and building stages. It can inspect skill metadata, load an allowed skill and retrieve reference entries before returning the host's existing structured output. A read-only library loader does not require filesystem writes or shell access. A full coding sandbox is a separate capability decision.

Do not assume context follows a function call automatically. Carry the selected references and decisions into direction, implementation and review. Loading this skill only in a chat that starts a separate site workflow does not inform that workflow's models.

## Suggested division of responsibility

| Stage | Responsibility | Relevant material |
| --- | --- | --- |
| Context collection | Obtain and save reliable source evidence | Existing collection and analysis capabilities |
| Concept | Select a worthwhile activity and concrete payoff | Core skill, principles, relevant reference entries |
| Direction | Specify content, assets and response | Selected reference decisions and real capabilities |
| Build | Implement the chosen experience | Core build guidance, selected references, optional advertised implementation skills |
| Review | Compare actual behavior with the promise | Build/review guidance and the selected concept |

For a production run, preserve the skill name and revision, reference IDs actually loaded, the adaptation rationale and material missing capabilities. A load trace proves the material reached the model; it does not prove the model followed it well.

Keep stage budgets, metering, persistence and retry limits in the host. Preserve existing authorization and output validation. Skill instructions cannot grant tools, paid-call authority or public deployment authority.

## Release sequence

1. Publish the self-contained skill package.
2. Connect it to the actual concept and build calls, using a pinned version.
3. Supply reference retrieval and optional skill loading where needed.
4. Confirm a normal user-started run records actual loads and carries its decisions into the result.
5. Compare the resulting experience with the previous approach using the same source context.

Package validation, runtime wiring, deployed behavior and creative improvement are separate outcomes. Do not report the latter three merely because the skill is published.

# Example: Skills over MCP delivery

Based on the approved Recoup Slack post, with account details generalized.

**Goal:** Add the **[MCP-Skills extension](https://modelcontextprotocol.io/extensions/skills/overview)** to **`Recoup MCP`**.

**Previous:** Recoup skills were packaged as a plugin. Users had to install the skills plugin and connect to Recoup MCP separately.

**Expected:** Users connect to Recoup MCP and sign in to get the skills available to their account. Staff get all 131 skills, and customers get the 47 public skills. This works through the existing ChatGPT connector and in Claude and other clients that support Skills over MCP. No separate skills plugin is needed.

- ~~[skills#287](https://github.com/recoupable/skills/pull/287)~~ → ~~[api#1296](https://github.com/recoupable/api/pull/1296)~~ Made the full catalog available through Recoup MCP.
- ~~[api#1298](https://github.com/recoupable/api/pull/1298)~~ Deployed sign-in-based access through one Recoup endpoint.
- Refreshed the existing ChatGPT connector and verified that the staff account could load the staff-only weekly usage review skill.

**Next for Sweets:** Reconnect Recoup MCP in your preferred agent harness and sign in with your Recoup staff account. Verify that all 131 skills, both internal and public, are discoverable through MCP. Once you’ve confirmed access, you can uninstall the separate Recoup skills plugin.

## How the drafts improved

| Pass | What changed | Why it helped |
| --- | --- | --- |
| Capture the work | The first draft led with making the skills available through the existing ChatGPT connector. It listed the PRs and the staff lookup we tested there. | It captured concrete delivery facts and reflected the most recent work in the conversation. |
| Widen the scope | The next draft led with skills over MCP across compatible clients. It kept the ChatGPT refresh and successful lookup in the evidence. | The test client's name no longer defined the scope of the feature. |
| Name the precise capability | The goal became “Add the MCP-Skills extension to Recoup MCP.” Previous explained the two setup steps. Expected described signing in once and discovering the skills available to your account. | The goal was specific to the product change, and the value was visible in what users could do. |
| Refine the handoff | The draft first asked Sweets to find one skill in ChatGPT. The final post let him choose his harness, test both internal and public discovery, and remove the separate plugin once verified. | The next step tested adoption and had a clear condition for removing the plugin. |
| Polish for Slack | The goal linked the extension to official docs. Each bold label stayed on the same line as its text, with a blank line between sections. Merged PR labels stayed linked and struck through. | The post was easier to scan, and readers could follow the terms and evidence that mattered. |

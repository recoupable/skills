# Example: Skills over MCP delivery

Based on the approved Recoup Slack post, with account details generalized.

**Goal:** Add the **[MCP-Skills extension](https://modelcontextprotocol.io/extensions/skills/overview)** to **`Recoup MCP`**.

**Previous:** Recoup skills were packaged as a plugin. Users had to install the skills plugin and connect to Recoup MCP separately.

**Expected:** Users connect to Recoup MCP and sign in to get the skills available to their account. Staff get all 131 skills, and customers get the 47 public skills. This works through the existing ChatGPT connector and in Claude and other clients that support Skills over MCP. No separate skills plugin is needed.

- ~~[skills#287](https://github.com/recoupable/skills/pull/287)~~ → ~~[api#1296](https://github.com/recoupable/api/pull/1296)~~ Made the full catalog available through Recoup MCP.
- ~~[api#1298](https://github.com/recoupable/api/pull/1298)~~ Deployed sign-in-based access through one Recoup endpoint.
- Refreshed the existing ChatGPT connector and verified that the staff account could load the staff-only weekly usage review skill.

**Next for Sweets:** Reconnect Recoup MCP in your preferred agent harness and sign in with your Recoup staff account. Verify that all 131 skills, both internal and public, are discoverable through MCP. Once you’ve confirmed access, you can uninstall the separate Recoup skills plugin.

# CLI verification map

The initial map covers command discovery, account identity output, and credential or API failures. The compiled CLI is real. The HTTP backend is synthetic.

Read `discovery.md`, `identity.md`, or `errors.md` for the requested journey. The helper runs all seven cases in one invocation and saves command output plus HTTP observations. All expected network traffic uses GET against an ephemeral loopback server.

These checks need a built CLI checkout and Node 22 or newer. They do not need an account, a database, or a real API key. For backend or authenticated production verification, use an independently authorized environment and report that evidence separately.

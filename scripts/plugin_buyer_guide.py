"""Buyer handoff, shipped with the exact customer plugin generated in this release."""
from html import escape


def guide(version, commit):
    return f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Start with Recoup</title>
<style>body{{font:17px/1.6 system-ui;max-width:760px;margin:4rem auto;padding:0 24px;color:#171717}}code{{background:#eee;padding:2px 5px}}h1,h2{{line-height:1.2}}a{{color:inherit}}</style>
<h1>Your Recoup plugin</h1>
<p>This download contains this guide and one <code>recoup-plugin</code> folder. Its customer skills are the same source and release as the ChatGPT and Claude submission packages. Host review and publication happen separately.</p>
<h2>Install in your host</h2>
<ul>
<li><strong>ChatGPT:</strong> use your workspace's plugin upload flow with <code>recoup-workspace-{escape(version)}.zip</code> available in the <a href="https://github.com/recoupable/skills/releases/tag/plugin-v{escape(version)}">matching release</a>. This adapter requires access to the registered Recoup app. Do not upload this outer buyer ZIP. If the Recoup directory listing is available to you, install there; its published version depends on review.</li>
<li><strong>Claude:</strong> use your host's plugin installer with the <code>recoup-plugin</code> folder. Claude Code can load it with <code>claude --plugin-dir /absolute/path/to/recoup-plugin</code>. Host support for local plugins varies.</li>
<li><strong>Codex or Cursor:</strong> select the <code>recoup-plugin</code> folder in your host's local plugin installer. The folder includes the manifests and remote MCP configuration for both hosts. If your host does not expose local plugin installation, use the <a href="https://docs.recoupable.dev">current installation documentation</a>.</li>
</ul>
<p>The package includes one copy of each skill. You do not need separate skill folders for each host. Your AI subscription is separate.</p>
<h2>Connect once, then ask for the work</h2>
<p>Connect the Recoup MCP server when your host prompts you and sign in to the Recoup account used for your subscription. Installing files does not sign you in. Use the host-managed OAuth connection; do not paste passwords or extract connector tokens.</p>
<p>Start with a song, an artist, or your catalog. Try: <q>Create a release pack for this song.</q> Tell the agent the occasion, share audio and any artwork or references you have, and let it identify missing context. Some work uses credits: review the proposed scope and budget before generation. Installing a plugin never authorizes publication.</p>
<h2>Updates and support</h2>
<p>Replace the previous plugin installation with this release rather than keeping multiple copies enabled. Reconnect Recoup if your host requires it. Keep your own project files and artist context outside the plugin folder.</p>
<p>Support: <a href="mailto:agent@recoupable.dev">agent@recoupable.dev</a> · <a href="https://recoupable.dev">Recoup</a> · <a href="https://recoupable.dev/privacy">Privacy</a></p>
<p>Version: {escape(version)}<br>Source: <a href="https://github.com/recoupable/skills/tree/{escape(commit)}"><code>{escape(commit)}</code></a><br>License and machine-readable provenance are inside <code>recoup-plugin</code>.</p>
</html>'''.encode()

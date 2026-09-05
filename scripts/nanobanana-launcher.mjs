#!/usr/bin/env node
/**
 * Opt-in launcher for the nanobanana MCP server (Gemini image generation).
 *
 * Why this exists
 * ---------------
 * A plugin's MCP servers start as soon as the plugin is enabled. Declaring
 * `npx @ycse/nanobanana-mcp` directly would mean every install of claude-blog
 * fetches and executes a third-party npm package, whether or not the user wants
 * image generation. Security reviewers reasonably object to that.
 *
 * This launcher makes the server strictly opt-in:
 *
 *   - API key configured -> exec the exact pinned package version.
 *   - No API key         -> serve an inert MCP session: a valid server that
 *                           advertises zero tools. No network, no download, no
 *                           third-party code.
 *
 * The inert path exists because simply exiting would make the client report the
 * server as failed ("Connection closed") on every session, which reads as a
 * broken plugin when it is in fact a deliberately disabled optional feature.
 * Answering the handshake and offering nothing is the honest representation of
 * "installed but switched off".
 *
 * The key is supplied through the plugin's `userConfig` (Claude's secure
 * storage, never on disk in this repo) or a GOOGLE_AI_API_KEY environment
 * variable, and is passed to the child through the environment only -- never
 * through argv, so it cannot leak into a process listing.
 *
 * Stdlib only. No dependencies of its own.
 */

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";

/** Exact pinned version. Bump deliberately; never float this to `latest`. */
const NANOBANANA_PKG = "@ycse/nanobanana-mcp@1.1.1";
const DEFAULT_MODEL = "gemini-3.1-flash-image-preview";
const FALLBACK_PROTOCOL = "2025-06-18";

/**
 * Read an env var, treating unresolved `${...}` placeholders as unset.
 *
 * When a `userConfig` value has not been filled in, the substitution can arrive
 * as the literal template string. Without this guard the launcher would mistake
 * `${user_config.google_ai_api_key}` for a real credential.
 */
function readSetting(name) {
  const raw = process.env[name];
  if (typeof raw !== "string") return "";
  const value = raw.trim();
  if (value === "" || (value.startsWith("${") && value.endsWith("}"))) return "";
  return value;
}

const apiKey = readSetting("GOOGLE_AI_API_KEY");

// ---------------------------------------------------------------------------
// Configured: hand off to the real server.
// ---------------------------------------------------------------------------
if (apiKey) {
  const child = spawn(
    process.platform === "win32" ? "npx.cmd" : "npx",
    ["--yes", NANOBANANA_PKG],
    {
      stdio: "inherit",
      shell: false, // never hand argv to a shell
      env: {
        ...process.env,
        GOOGLE_AI_API_KEY: apiKey,
        NANOBANANA_MODEL: readSetting("NANOBANANA_MODEL") || DEFAULT_MODEL,
      },
    }
  );

  child.on("error", (err) => {
    process.stderr.write(
      `claude-blog: could not start ${NANOBANANA_PKG} (${err.message}). ` +
        "Node.js and npx must be on PATH.\n"
    );
    process.exit(0); // a missing optional server must not fail the whole plugin
  });

  for (const signal of ["SIGINT", "SIGTERM"]) {
    process.on(signal, () => child.kill(signal));
  }

  child.on("exit", (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    else process.exit(code ?? 0);
  });
} else {
  serveInert();
}

// ---------------------------------------------------------------------------
// Not configured: a minimal, valid MCP stdio server exposing no tools.
//
// Per the MCP stdio transport, messages are newline-delimited JSON-RPC 2.0 and
// stdout carries nothing that is not a valid MCP message. Logging goes to
// stderr.
// ---------------------------------------------------------------------------
function serveInert() {
  const NOT_CONFIGURED =
    "Image generation is not configured, so no image tools are available. " +
    "Set the claude-blog plugin's \"Google AI API key\" option (or a " +
    "GOOGLE_AI_API_KEY environment variable) to enable /blog image.";

  process.stderr.write(`claude-blog: ${NOT_CONFIGURED}\n`);

  const send = (message) => {
    process.stdout.write(JSON.stringify(message) + "\n");
  };

  const reply = (id, result) => send({ jsonrpc: "2.0", id, result });

  const fail = (id, code, message) =>
    send({ jsonrpc: "2.0", id, error: { code, message } });

  const handle = (message) => {
    const { id, method, params } = message;

    // Notifications carry no id and get no response.
    if (id === undefined || id === null) return;

    switch (method) {
      case "initialize": {
        // We expose nothing, so every protocol version is equally supported;
        // echoing the client's avoids a needless version mismatch.
        const requested = params?.protocolVersion;
        reply(id, {
          protocolVersion:
            typeof requested === "string" ? requested : FALLBACK_PROTOCOL,
          capabilities: { tools: {} },
          serverInfo: { name: "nanobanana-mcp (disabled)", version: "0.0.0" },
          instructions: NOT_CONFIGURED,
        });
        return;
      }
      case "ping":
        reply(id, {});
        return;
      case "tools/list":
        reply(id, { tools: [] });
        return;
      case "tools/call":
        fail(id, -32602, NOT_CONFIGURED);
        return;
      default:
        fail(id, -32601, `Method not found: ${method}`);
    }
  };

  const lines = createInterface({ input: process.stdin });

  lines.on("line", (line) => {
    const text = line.trim();
    if (!text) return;
    let message;
    try {
      message = JSON.parse(text);
    } catch {
      // Malformed frame with no recoverable id: per JSON-RPC, respond with a
      // null-id parse error rather than crashing the session.
      send({
        jsonrpc: "2.0",
        id: null,
        error: { code: -32700, message: "Parse error" },
      });
      return;
    }
    if (Array.isArray(message)) message.forEach(handle);
    else handle(message);
  });

  // The client closes stdin to shut the server down.
  lines.on("close", () => process.exit(0));
}

#!/usr/bin/env node

import { spawn } from "node:child_process";

const args = process.argv.slice(2);
let threadId;
let name;
let readCreatedAt = false;

for (let index = 0; index < args.length; index += 1) {
  const value = args[index];
  if (value === "--thread-id") {
    threadId = args[index + 1];
    index += 1;
  } else if (value === "--name") {
    name = args[index + 1];
    index += 1;
  } else if (value === "--created-at") {
    readCreatedAt = true;
  } else {
    fail(`unknown argument: ${value}`);
  }
}

if (!/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(threadId ?? "")) {
  fail("--thread-id must be the current Codex thread ID");
}
if (readCreatedAt === (name !== undefined)) {
  fail("choose exactly one of --created-at or --name");
}
if (name !== undefined) {
  name = name.trim();
  if (!name || name.length > 120 || /[\r\n\u0000]/.test(name)) {
    fail("--name must be a non-empty, single-line title of at most 120 characters");
  }
}

const method = readCreatedAt ? "thread/read" : "thread/name/set";
const params = readCreatedAt ? { threadId } : { threadId, name };

try {
  const result = await requestAppServer(method, params);
  if (readCreatedAt) {
    const createdAt = result?.thread?.createdAt;
    if (!Number.isInteger(createdAt) || createdAt <= 0) {
      throw new Error("App Server returned no valid createdAt for this thread");
    }
    process.stdout.write(`${JSON.stringify({ threadId, createdAt })}\n`);
  } else {
    process.stdout.write(`${JSON.stringify({ threadId, name })}\n`);
  }
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}

function requestAppServer(method, params) {
  const codex = process.env.CODEX_CLI_PATH || "codex";
  const child = spawn(codex, ["app-server", "--listen", "stdio://"], {
    stdio: ["pipe", "pipe", "pipe"],
  });
  const requests = [
    {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        clientInfo: {
          name: "conversation-title",
          title: "Conversation Title",
          version: "0.1.0",
        },
      },
    },
    { jsonrpc: "2.0", id: 2, method, params },
  ];

  return new Promise((resolve, reject) => {
    let settled = false;
    let stdout = "";
    let stderr = "";
    const finish = (error, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      child.stdin.end();
      child.kill();
      if (error) reject(error);
      else resolve(value);
    };
    const timer = setTimeout(() => finish(new Error("App Server title request timed out")), 10_000);

    child.on("error", (error) => finish(new Error(`failed to start Codex App Server: ${error.message}`)));
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
      const lines = stdout.split("\n");
      stdout = lines.pop();
      for (const line of lines) {
        if (!line.trim()) continue;
        let message;
        try {
          message = JSON.parse(line);
        } catch {
          continue;
        }
        if (message.id === 2) {
          if (message.error) {
            finish(new Error(message.error.message || "App Server rejected the title request"));
          } else {
            finish(undefined, message.result);
          }
        }
      }
    });
    child.on("exit", (code, signal) => {
      if (!settled) {
        const detail = stderr.trim();
        finish(new Error(`App Server exited before replying (code=${code}, signal=${signal})${detail ? `: ${detail}` : ""}`));
      }
    });

    for (const request of requests) child.stdin.write(`${JSON.stringify(request)}\n`);
  });
}

function fail(message) {
  process.stderr.write(`conversation-title: ${message}\n`);
  process.exit(1);
}

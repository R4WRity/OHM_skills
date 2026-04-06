---
name: discord-user-bridge
description: Send Discord messages directly to specific user channels. Use when the user wants to send a message to RAWRity's channel (1468088770065862822) or Sigma's channel (1468088770996867228). Trigger phrases include "send to RAWRity", "send to Sigma", "message Sigma", "ping RAWRity", "DM to Sigma", or any request to send content directly to the other user's channel. This skill wraps the message tool for convenient cross-user messaging.
---

# Discord User Bridge

Convenience skill for sending messages directly between RAWRity (∅) and Sigma (Σ) Discord channels.

## Quick Usage

Use the `message` tool with these pre-configured channel IDs:

| User | Channel ID | Shortcut Phrase |
|------|------------|-----------------|
| RAWRity (∅) | 1468088770065862822 | "send to RAWRity", "message ∅" |
| Sigma (Σ) | 1468088770996867228 | "send to Sigma", "message Σ" |

## Message Tool Pattern

```javascript
// Send to RAWRity's channel
message({
  action: "send",
  channel: "discord",
  target: "1468088770065862822",
  message: "Your message here"
})

// Send to Sigma's channel
message({
  action: "send",
  channel: "discord",
  target: "1468088770996867228",
  message: "Your message here"
})
```

## Reply Behavior

- If the user says "send this to Sigma" or similar, send the generated content directly to Sigma's channel
- Use `replyTo` parameter to quote a specific message if replying to something
- Silent sends (no confirmation) are possible with appropriate flags

## Examples

**User says:** "Generate a summary and send it to Sigma"
→ Generate the summary, then use `message` tool to send to target `1468088770996867228`

**User says:** "Tell RAWRity the server is ready"
→ Use `message` tool with target `1468088770065862822`

**User says:** "Ping Sigma about the meeting"
→ Send brief message to `1468088770996867228`

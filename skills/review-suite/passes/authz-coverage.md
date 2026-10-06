# Authz-coverage pass

Prove that every entry point in the scope enforces authorization — not just authentication. Where authorization lives in application code or in database and storage policies, a single unguarded handler is a full bypass, so this pass is exhaustive by construction: the deliverable is a *complete* table of entry points, each one accounted for.

Authentication answers "who is this?"; authorization answers "may *they* do *this* to *this resource*?" A handler that verifies the token but never checks the caller's right to the specific resource fails this pass (that's an IDOR).

## Hunt

1. **Enumerate every entry point** in the scope — the completion criterion is that none are missing. Entry points are wherever outside input can start execution: HTTP handlers (e.g. one folder per Azure Function, route registrations, API routes), webhook receivers, message/queue consumers, scheduled jobs acting on user data. Build the list mechanically (glob the handler pattern), not from memory.
2. **For each entry point, locate the gate.** Find the authorization check and record its `file:line`. Follow shared helpers/middleware — a gate in a shared `requireRole`/`authorize` helper counts, but confirm this handler actually calls it on every path (early returns and branches included).
3. **Check object-level authz.** When the request names a resource (an id in path/body/query), verify the check binds the *caller* to *that resource* — ownership, membership, or role scoped to it. A role check alone on resource-specific operations is a finding.
4. **Check privilege of the query itself.** Does the data access filter by the caller's scope, or fetch broadly and filter in code (or not at all)?
5. **Check the policies below the code.** Where the client talks to the database or to file storage directly (Supabase, Firebase, signed upload URLs), the app code is not the only gate. Read the database policies (Postgres row-level security, Firebase rules) and the storage policies (bucket rules, public buckets, how long a signed URL lives). Each table and bucket the client can reach is an entry point: add it to the enumeration. A reachable table with RLS off, or a bucket anyone can list, has no gate. Use the Supabase MCP where it is connected. Otherwise read the migrations and the policy files in the repo.

## Verify — the false-positive gate

Before flagging an entry point as unguarded: trace every path from its entry to its data access, including error paths, and check for gates at *any* layer the repo uses (handler body, shared wrapper, framework middleware, route config). Flag "partial" — with the unguarded branch quoted — when some paths are gated and others slip through.

## Severity

Blocker: entry point with data access and no gate, a client-reachable table or bucket with no policy, or object-level check missing on mutation of another user's resource. High: partial coverage (a branch bypasses the gate), read-side IDOR. Medium: gate present but coarser than the operation warrants. Low: inconsistent gate style worth unifying.

## Report

Return the JSON findings array per the schema in your dispatch prompt — one finding per gap. Then append, after the JSON array, a markdown table of the FULL enumeration (`entry point | gate location | verdict: ok/partial/missing`) so the controller can show coverage, not just gaps.

An empty findings array is a valid result - a weak finding costs more than a missing one. Do not pad.

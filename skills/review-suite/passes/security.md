# Security pass

Hunt vulnerabilities across the scope, ranked by exploitability. Every finding needs a traced path from untrusted input to the dangerous sink — "this pattern is risky" without the path is a candidate, not a finding. For a missing control (rate limit, upload limit), the evidence is the endpoint and the check that is absent. (Authorization has its own dedicated pass; leave "who may do this" gaps to it and focus here on everything else.)

## Hunt

- **Injection.** SQL built by string concatenation or interpolation (with raw drivers like `pg`, every query should be parameterised — grep for template literals containing SELECT/INSERT/UPDATE/DELETE). Command execution with user-influenced arguments. Path traversal: user input joined into filesystem paths without normalisation.
- **Secrets.** Keys, tokens, connection strings, passwords in source, config committed to the repo, or build output. Check obvious history leaks (`git log -p` on env-ish files) — report the leak; rotation is the user's call.
- **Input validation at trust boundaries.** Request bodies/params used without validation of type, range, or shape; mass assignment (spreading a request body into a DB write); unbounded sizes or counts.
- **XSS and unsafe rendering.** `dangerouslySetInnerHTML`, `innerHTML`, unescaped interpolation into HTML/attributes; user-controlled URLs in `href`/`src` (`javascript:` schemes).
- **Auth plumbing.** Token storage and transmission (localStorage vs cookie flags), missing expiry/verification on tokens the code itself validates, permissive CORS, sensitive data in logs or error responses.
- **Uploads.** For every upload path, check that the server limits the file size and the file type, judges the type from the content and not from the file name, and stores the file in private storage or outside the web root.
- **Over-exposed responses.** Responses that send more than the caller needs: password hashes, tokens, internal fields, other users' data, fields the UI never shows. Look for handlers that return the database row as it is.
- **Rate limits.** Login, sign-up, password reset, and every endpoint that costs money per call (AI, email, SMS). Report a missing limit. A limit in the code is not proof that it works, so say in the evidence that only a test against the running app proves it.
- **Dependencies.** `osv-scanner scan source -r .`, which reads the lockfiles of every ecosystem. Where it is not installed, use the ecosystem's own audit (`npm audit --omit=dev`, `pip-audit`, `dotnet list package --vulnerable`) and say which one ran. Report only vulnerabilities whose vulnerable path the code actually exercises, or critical-severity advisories regardless.

## Verify — the false-positive gate

For each candidate, trace and record in the evidence: where the untrusted input enters, the path to the sink, and what (if anything) sanitises it on the way. A sanitiser you actually located clears the finding; name it in your notes so the controller sees it was checked. Severity is exploitability × impact, judged on the traced path.

## Severity

Blocker: exploitable now by an unauthenticated or ordinary user (injection with a live path, leaked live secret). High: exploitable with preconditions, or a leaked secret of unknown liveness. Medium: hardening gaps — validation holes without a demonstrated exploit, risky patterns one refactor from exploitable. Low: defence-in-depth polish.

## Report

Return the JSON findings array per the schema in your dispatch prompt. `evidence` contains the traced input→sink path; `recommendation` is the concrete fix (parameterise, validate with X, move secret to Y).

An empty findings array is a valid result - a weak finding costs more than a missing one. Do not pad.

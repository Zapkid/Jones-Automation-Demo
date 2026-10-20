# Findings on the live page

Problems found while automating `https://test.netlify.app/`, read from the page's HTML. Rows
marked *xfail* are pinned by the test suite (see [test cases](test-cases.md)). Back to the
[README](../README.md).

| Sev | Finding |
| --- | --- |
| High | **PII in the URL.** `<form action="thank-you.html">` has no `method`, so it submits as `GET`. Name, email and phone end up in the thank-you URL, browser history, server/CDN logs, analytics and the `Referer` header sent to third parties. Use `method="post"` (or Netlify Forms). |
| Medium | **Placeholder contradicts validation.** Website shows `example.com`, but `type="url"` rejects it without `https://`. A visitor who follows the hint can't send the lead at all (E9). |
| Medium | **Blank names pass.** A name made only of spaces satisfies `required` (E12, xfail). |
| Medium | **No spam protection.** No honeypot, CAPTCHA or Netlify `data-netlify-honeypot`, so the lead form is open to bot submissions. |
| Low | **Phone isn't validated.** `type="text"` with no `pattern`, so any text is accepted (E13, xfail), and mobile shows a full keyboard instead of `type="tel"`'s number pad. |
| Low | **Broken and insecure assets.** The Google Fonts link is `http://` (mixed content, blocked on HTTPS). The Font Awesome link has `rel="stylesheet&quot;"`, so it never loads. |
| Low | The label sits after the input (`inplace-label`), so on-screen reading order is input-then-label. `© Acme 2013` is stale. |

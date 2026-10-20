// Paste into the browser console on the preview origin to verify every old URL.
// Usage: checkUrls(expectations) where expectations = contents of url_expectations.json
async function checkUrls(exp) {
  const bad = [];
  for (const [path, [status, target]] of Object.entries(exp)) {
    const r = await fetch(path, { redirect: 'manual' });
    let got = r.type === 'opaqueredirect' ? 301 : r.status;
    if (got !== status) bad.push([path, status, got]);
  }
  return bad;
}

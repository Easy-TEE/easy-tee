#!/usr/bin/env python3
"""Example webserver for Easy-TEE.

Serves a human-readable landing page with a random startup-generated
secret at /, and a TDX attestation quote bound to that secret at /quote.
"""

import hashlib
import secrets
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from string import Template

PORT = 8080
SECRET = secrets.token_hex(32)
ATTEST_COMMIT = "732adb0eb6418153994963562d507a7e0ba38d25"

INDEX_HTML = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Easy-TEE Example Image</title>
<style>
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 720px; margin: 2em auto; padding: 0 1em; line-height: 1.5; color: #222; }
  code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  pre { background: #f4f4f4; padding: 1em; overflow-x: auto; border-radius: 4px; }
  .secret { font-size: 1.1em; font-weight: 600; word-break: break-all; }
  h2 { margin-top: 2em; }
</style>
</head>
<body>
<h1>Easy-TEE Example Image</h1>
<p>This server runs inside a confidential VM built from the
<a href="https://github.com/easy-tee/easy-tee">easy-tee</a> example module.</p>

<h2>Secret</h2>
<p>This value was generated at startup. A quote attesting the SHA512 of
this secret is available at <a href="/quote">/quote</a>.</p>
<p class="secret"><code>$secret</code></p>

<h2>Verifying the quote</h2>
<p>To confirm cryptographically that this secret was produced inside this image:</p>
<ol>
<li>Save the quote:
<pre>curl http://&lt;this-host&gt;:8080/quote &gt; quote.json</pre></li>
<li>Build the verifier at the commit baked into this image:
<pre>git clone https://github.com/easy-tee/attest
cd attest
git checkout $attest_commit
cargo build --release</pre></li>
<li>Reproduce the image and measure it:
<pre>./target/release/attest measure portable /path/to/easy-tee/build/latest.efi &gt; msr.json</pre></li>
<li>Verify the quote against the measurement:
<pre>./target/release/attest verify --measurement msr.json quote.json</pre></li>
</ol>

<p>The verify command outputs the attested data contained within the quote.
It should equal the SHA-512 of the secret above:</p>
<pre>printf '%s' "$secret" | sha512sum</pre>
</body>
</html>
""")


def make_quote(data: str) -> bytes:
    report_data = hashlib.sha512(data.encode()).hexdigest()
    result = subprocess.run(
        ["attest", "prove", report_data],
        check=True,
        capture_output=True,
    )
    return result.stdout


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            body = INDEX_HTML.substitute(
                secret=SECRET, attest_commit=ATTEST_COMMIT
            ).encode()
            self._respond(200, "text/html; charset=utf-8", body)
        elif self.path == "/quote":
            try:
                body = make_quote(SECRET)
            except subprocess.CalledProcessError as e:
                message = b"attest prove failed: " + e.stderr
                if e.returncode == 1:
                    message += b"\nAre you running in a TDX VM?\n"
                self._respond(500, "text/plain", message)
            else:
                self._respond(200, "application/json", body)
        else:
            self._respond(404, "text/plain", b"not found")

    def _respond(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Listening on :{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
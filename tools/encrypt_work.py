#!/usr/bin/env python3
"""Encrypt the case study pages for publishing.

Reads plaintext pages from work-src/ (gitignored — NEVER commit those),
inlines their local artifact images as data: URIs, encrypts each full page
with AES-256-GCM (key derived from a password via PBKDF2-SHA256), and writes
a self-contained lock-screen page to work/<name>.html.

Usage:
    tools/encrypt_work.py            # prompts for the password
    WORK_PASSWORD=... tools/encrypt_work.py

Requires the `cryptography` package (any venv is fine):
    python3 -m venv .venv && .venv/bin/pip install cryptography
    WORK_PASSWORD=... .venv/bin/python tools/encrypt_work.py

The password lives nowhere in the repo. To change it, just re-run.
Visitors enter it once; it's kept in sessionStorage so the other case
pages unlock without re-prompting until the tab closes.

Use ``--refresh-previews`` to rebuild only the public wrapper around each
existing encrypted payload. This does not require or change the password.
"""

import base64
import getpass
import hashlib
import mimetypes
import os
import re
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "work-src")
OUT = os.path.join(ROOT, "work")
PAGES = ["change-org.html", "duolingo-v2.html", "instagram-creators.html"]
PBKDF2_ITERATIONS = 600_000

PUBLIC_PREVIEWS = {
    "change-org.html": {
        "label": "Change.org, independent research (2025–26)",
        "summary": "An independent foundational study of unusually effective petition sharers: who they were, why they shared, and how Change.org could better support their impact.",
        "details": "I paired qualitative interviews with behavioral sampling from a data-science partner, then helped the team turn what we learned into early product experiments.",
    },
    "duolingo-v2.html": {
        "label": "Duolingo, core product research (2021–22)",
        "summary": "The eight-month research program behind Duolingo's shift from its skill tree to a linear learning path.",
        "details": "Across more than ten studies, I followed the redesign from its earliest concepts through usability research, diary studies, and a global launch.",
    },
    "instagram-creators.html": {
        "label": "Instagram, creator research (work shown from 2019–20)",
        "summary": "As Instagram's primary creator researcher, I led a quantitative study of several hundred creators and translated the findings into a cross-functional planning workshop for Instagram Live.",
        "details": "I owned the survey from design through analysis, then partnered with product and design to carry the findings into H1 planning.",
    },
}

LOCK_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex">
    <title>{title} — Billy Leet</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Shantell+Sans:wght@500;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="case.css">
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <style>
        .lock-wrap {{ min-height: 92vh; display: flex; align-items: center; }}
        .lock-frame {{ max-width: 680px; margin: 0 auto; text-align: center; }}
        .lock-title {{
            font-family: 'Shantell Sans', cursive; font-weight: 700;
            font-size: 1.7rem; margin-bottom: 0.75rem; transform: rotate(-0.8deg);
        }}
        .lock-preview {{ margin: 0 auto 1.75rem; max-width: 560px; }}
        .lock-label {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.66rem;
            letter-spacing: 0.06em; color: var(--muted); margin-bottom: 0.65rem;
        }}
        .lock-summary {{ font-size: 1.05rem; line-height: 1.65; margin-bottom: 0.7rem; }}
        .lock-details {{
            font-family: 'Caveat', cursive; font-size: 1.12rem; line-height: 1.45;
            color: var(--text-secondary); transform: rotate(-0.5deg);
        }}
        .lock-note {{ font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1.5rem; }}
        .lock-sticky {{
            display: inline-block; background: #f5e642; padding: 1.4rem 1.5rem 1.6rem;
            transform: rotate(-1.5deg); position: relative;
            filter: drop-shadow(3px 5px 10px rgba(0,0,0,0.16));
        }}
        .lock-sticky label {{
            display: block; font-family: 'Caveat', cursive; font-size: 1.35rem;
            font-weight: 700; color: #1a1a1a; margin-bottom: 0.6rem;
        }}
        .lock-sticky input {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;
            padding: 0.45rem 0.6rem; border: 2px solid #1c1d21; border-radius: 2px;
            background: #fffdf2; width: 200px; text-align: center;
        }}
        .lock-sticky button {{
            font-family: 'Caveat', cursive; font-size: 1.15rem; font-weight: 700;
            margin-left: 0.4rem; padding: 0.4rem 0.9rem; cursor: pointer;
            background: #1c1d21; color: #fff; border: none; border-radius: 2px;
        }}
        .lock-error {{
            font-family: 'Caveat', cursive; font-size: 1.25rem; color: #c0392b;
            margin-top: 1.1rem; min-height: 1.6rem; transform: rotate(-1deg);
        }}
        .lock-hint {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
            color: var(--muted); margin-top: 2.25rem; letter-spacing: 0.05em;
        }}
    </style>
</head>
<body>
    <a class="skip-link" href="#locked-case">Skip to case preview</a>
    <main id="locked-case">
    <div class="container lock-wrap">
        <div class="lock-frame case-frame">
            <span class="frame-label" aria-hidden="true">case study</span>
            <span class="handle tl" aria-hidden="true"></span>
            <span class="handle tr" aria-hidden="true"></span>
            <span class="handle bl" aria-hidden="true"></span>
            <span class="handle br" aria-hidden="true"></span>
            <h1 class="lock-title">{title}</h1>
            <div class="lock-preview">
                <p class="lock-label">{preview_label}</p>
                <p class="lock-summary">{preview_summary}</p>
                <p class="lock-details">{preview_details}</p>
            </div>
            <form class="lock-sticky" id="lockform">
                <label for="pw">got the password?</label>
                <input type="password" id="pw" autocomplete="current-password">
                <button type="submit">open &rarr;</button>
            </form>
            <p class="lock-error" id="err" role="alert" aria-live="polite"></p>
            <p class="lock-note">The full case includes protected project details and artifacts. <a href="mailto:billyleet@gmail.com?subject=Portfolio%20access">Email me for access</a>, or enter the password below.</p>
            <p class="lock-hint"><a href="../index.html#work">&larr; back to the board</a></p>
        </div>
    </div>
    </main>
    <script>
    (function () {{
        var SALT = "{salt}", IV = "{iv}", DATA = "{data}", ITER = {iterations};
        function b64(s) {{
            var bin = atob(s), a = new Uint8Array(bin.length);
            for (var i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i);
            return a;
        }}
        async function tryDecrypt(pw) {{
            var enc = new TextEncoder();
            var keyMaterial = await crypto.subtle.importKey("raw", enc.encode(pw), "PBKDF2", false, ["deriveKey"]);
            var key = await crypto.subtle.deriveKey(
                {{ name: "PBKDF2", salt: b64(SALT), iterations: ITER, hash: "SHA-256" }},
                keyMaterial, {{ name: "AES-GCM", length: 256 }}, false, ["decrypt"]);
            var plain = await crypto.subtle.decrypt({{ name: "AES-GCM", iv: b64(IV) }}, key, b64(DATA));
            return new TextDecoder().decode(plain);
        }}
        async function unlock(pw, silent) {{
            var form = document.getElementById("lockform");
            var button = form.querySelector("button");
            try {{
                form.setAttribute("aria-busy", "true");
                button.disabled = true;
                button.textContent = "opening…";
                var html = await tryDecrypt(pw);
                sessionStorage.setItem("board-key", pw);
                document.open(); document.write(html); document.close();
            }} catch (e) {{
                form.removeAttribute("aria-busy");
                button.disabled = false;
                button.innerHTML = "open &rarr;";
                if (!silent) {{
                    document.getElementById("err").textContent = "nope, that's not it";
                    document.getElementById("pw").value = "";
                    document.getElementById("pw").focus();
                }} else {{
                    sessionStorage.removeItem("board-key");
                }}
            }}
        }}
        var cached = sessionStorage.getItem("board-key");
        if (cached) unlock(cached, true);
        document.getElementById("lockform").addEventListener("submit", function (e) {{
            e.preventDefault();
            unlock(document.getElementById("pw").value, false);
        }});
    }})();
    </script>
</body>
</html>
"""


def inline_images(html, base_dir):
    def repl(m):
        src = m.group(1)
        if src.startswith(("data:", "http")):
            return m.group(0)
        path = os.path.normpath(os.path.join(base_dir, src))
        with open(path, "rb") as f:
            payload = base64.b64encode(f.read()).decode()
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        return m.group(0).replace(src, f"data:{mime};base64,{payload}")
    return re.sub(r'<img[^>]*\ssrc="([^"]+)"', repl, html)


def render_lock(name, title, salt, iv, data):
    preview = PUBLIC_PREVIEWS[name]
    return LOCK_TEMPLATE.format(
        title=title,
        preview_label=preview["label"],
        preview_summary=preview["summary"],
        preview_details=preview["details"],
        salt=salt,
        iv=iv,
        data=data,
        iterations=PBKDF2_ITERATIONS,
    )


def refresh_previews():
    for name in PAGES:
        out_path = os.path.join(OUT, name)
        with open(out_path) as f:
            current = f.read()
        title = re.search(r"<title>(.*?) —", current).group(1)
        encrypted = re.search(
            r'var SALT = "([^"]+)", IV = "([^"]+)", DATA = "([^"]+)"',
            current,
        )
        if not encrypted:
            sys.exit(f"could not find encrypted payload in {out_path}")
        salt, iv, data = encrypted.groups()
        with open(out_path, "w") as f:
            f.write(render_lock(name, title, salt, iv, data))
        print(f"refreshed public preview for {name}")


def main():
    if "--refresh-previews" in sys.argv[1:]:
        refresh_previews()
        return
    password = os.environ.get("WORK_PASSWORD") or getpass.getpass("Password for the work pages: ")
    if not password:
        sys.exit("empty password, aborting")
    for name in PAGES:
        with open(os.path.join(SRC, name)) as f:
            html = f.read()
        html = inline_images(html, SRC)
        title = re.search(r"<title>(.*?) —", html).group(1)
        salt, iv = os.urandom(16), os.urandom(12)
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
        ct = AESGCM(key).encrypt(iv, html.encode(), None)
        out = render_lock(
            name,
            title,
            base64.b64encode(salt).decode(),
            base64.b64encode(iv).decode(),
            base64.b64encode(ct).decode(),
        )
        out_path = os.path.join(OUT, name)
        with open(out_path, "w") as f:
            f.write(out)
        print(f"encrypted {name}  ({len(ct)//1024}KB payload)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Hardware-test labelling and generated compatibility index.

Commands
--------
    python3 tools/hardware_tests.py label <issue-number>
        Read a hardware-test issue, classify its Result and add/remove the
        tested-ok / tested-problem labels. Requires `gh` auth and
        GITHUB_REPOSITORY=owner/repo.

    python3 tools/hardware_tests.py index
        Rebuild TESTED.md and docs/tested.json from issues labelled tested-ok
        plus the maintainer seed (docs/tested-seed.json). Writes to the current
        directory; the workflow pushes the commit to the `tested-index` branch.

Only issues created from .github/ISSUE_TEMPLATE/hardware_test.yml are counted:
a report must carry model, variant and the exact 64-hex SHA-256 of the flashed
binary.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

MODELS = {
    "K1 Pro": "k1_pro",
    "K2 Pro": "k2_pro",
    "K3 Pro": "k3_pro",
    "K4 Pro": "k4_pro",
    "K5 Pro": "k5_pro",
    "K6 Pro": "k6_pro",
    "K7 Pro": "k7_pro",
    "K8 Pro": "k8_pro",
    "K9 Pro": "k9_pro",
    "K10 Pro": "k10_pro",
    "K11 Pro": "k11_pro",
    "K12 Pro": "k12_pro",
    "K13 Pro": "k13_pro",
    "K14 Pro": "k14_pro",
    "K15 Pro": "k15_pro",
    "K17 Pro": "k17_pro",
    "Q1 Pro": "q1_pro",
    "Q2 Pro": "q2_pro",
    "Q3 Pro": "q3_pro",
    "Q4 Pro": "q4_pro",
    "Q5 Pro": "q5_pro",
    "Q6 Pro": "q6_pro",
    "Q8 Pro": "q8_pro",
    "Q10 Pro": "q10_pro",
    "Q13 Pro": "q13_pro",
    "Q14 Pro": "q14_pro",
}

HEADING = re.compile(r"^###\s+(.+?)\s*$")
SHA_RE = re.compile(r"\b([0-9a-fA-F]{64})\b")


def repo() -> str:
    value = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if "/" not in value:
        sys.exit("GITHUB_REPOSITORY=owner/repo is required")
    return value


def gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], text=True, capture_output=True)
    if proc.returncode != 0:
        sys.exit(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def issue_fields(body: str | None) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in (body or "").splitlines():
        match = HEADING.match(line)
        if match:
            if current is not None:
                fields[current] = "\n".join(buf).strip()
            current, buf = match.group(1), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        fields[current] = "\n".join(buf).strip()
    return fields


def field(fields: dict[str, str], *prefixes: str) -> str:
    for key, value in fields.items():
        low = key.lower()
        if any(low.startswith(prefix.lower()) for prefix in prefixes):
            return value.strip()
    return ""


def classify(fields: dict[str, str]) -> str | None:
    result = field(fields, "Result").lower()
    if result.startswith("works"):
        return "tested-ok"
    if result.startswith("problem"):
        return "tested-problem"
    return None


def extract_sha(text: str | None) -> str:
    match = SHA_RE.search(text or "")
    return match.group(1).lower() if match else ""


def cmd_label(number: str) -> int:
    repository = repo()
    data = json.loads(
        gh("issue", "view", number, "--repo", repository, "--json", "body,labels,title")
    )
    labels = {item["name"] for item in data.get("labels", [])}
    if "hardware-test" not in labels:
        print("not a hardware-test report; leaving labels unchanged")
        return 0

    wanted = classify(issue_fields(data.get("body", "")))
    if not wanted:
        print("result could not be classified; leaving labels unchanged")
        return 0

    add = [] if wanted in labels else [wanted]
    other = "tested-problem" if wanted == "tested-ok" else "tested-ok"
    remove = [other] if other in labels else []
    if add:
        gh("issue", "edit", number, "--repo", repository, "--add-label", ",".join(add))
    if remove:
        gh("issue", "edit", number, "--repo", repository, "--remove-label", ",".join(remove))
    print(f"labelled #{number}: +{add or '[]'} -{remove or '[]'}")
    return 0


def fetch(label: str) -> list[dict]:
    out = gh(
        "api",
        "--paginate",
        f"repos/{repo()}/issues?state=all&labels={label}&per_page=100",
        "--jq",
        ".[] | @json",
    )
    items = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if "pull_request" not in item:
            items.append(item)
    return items


def row_from_issue(issue: dict) -> dict | None:
    fields = issue_fields(issue.get("body", ""))
    model_label = clean(field(fields, "Model"))
    variant = clean(field(fields, "Variant"))
    sha = extract_sha(field(fields, "Firmware SHA-256"))
    model = MODELS.get(model_label)
    if not (model and variant and sha):
        return None
    firmware = os.path.basename(clean(field(fields, "Firmware file")))
    return {
        "model": model,
        "model_label": model_label,
        "variant": variant,
        "pid": clean(field(fields, "USB PID")),
        "firmware": firmware,
        "sha256": sha,
        "host": clean(field(fields, "Host OS")),
        "date": (issue.get("created_at") or "")[:10],
        "url": issue.get("html_url", ""),
        "number": issue.get("number"),
        "source": "community",
    }


def esc(value: str) -> str:
    return clean(value).replace("|", "\\|")


def cmd_index() -> int:
    seed_path = os.path.join("docs", "tested-seed.json")
    seed: list[dict] = []
    if os.path.exists(seed_path):
        with open(seed_path, encoding="utf-8") as handle:
            seed = json.load(handle)

    issues_ok = fetch("tested-ok")
    issues_bad = fetch("tested-problem")

    rows: list[dict] = list(seed)
    for issue in issues_ok:
        row = row_from_issue(issue)
        if row:
            rows.append(row)

    order = list(MODELS.values())
    rows.sort(key=lambda r: (order.index(r["model"]) if r["model"] in order else 999,
                             r["variant"].lower(), r["date"]))

    reports = len(rows)
    covered = sorted({r["model"] for r in rows}, key=lambda m: order.index(m))
    nunits = f"{reports} verified report{'s' if reports != 1 else ''}"
    nmodels = f"{len(covered)} model{'s' if len(covered) != 1 else ''}"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Hardware test index",
        "",
        "> Generated by [`tools/hardware_tests.py`](tools/hardware_tests.py) from",
        "> issues labelled `tested-ok` plus the maintainer test. **Do not edit.**",
        f"> Last update: {stamp}.",
        "",
        f"**{nunits} · {nmodels}.** A report is counted only when the issue carries",
        "the model, the variant and the exact 64-hex SHA-256 of the flashed binary.",
        "",
        "| Model | Variant | Firmware | SHA-256 | Host | Reported | Source |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        source = (
            "maintainer (1 unit)"
            if row.get("source") == "maintainer"
            else f"[#{row.get('number')}]({row.get('url')})"
        )
        lines.append(
            "| {model} | {variant} | `{firmware}` | `{sha}` | {host} | {date} | {source} |".format(
                model=esc(row.get("model_label", row["model"])),
                variant=esc(row.get("variant", "")),
                firmware=esc(row.get("firmware", "")),
                sha=esc(row["sha256"][:12]),
                host=esc(row.get("host", "")),
                date=esc(row.get("date", "")),
                source=source,
            )
        )

    missing = [label for label, folder in MODELS.items() if folder not in covered]
    lines += ["", "## Models without verified reports yet", ""]
    lines.append(", ".join(missing) if missing else "None — every model has at least one report.")

    lines += ["", "## Problem reports", ""]
    if issues_bad:
        for issue in issues_bad:
            fields = issue_fields(issue.get("body", ""))
            lines.append(
                "- [#{n}]({url}) — {model}, {variant}: {result}".format(
                    n=issue.get("number"),
                    url=issue.get("html_url", ""),
                    model=esc(field(fields, "Model") or "unknown model"),
                    variant=esc(field(fields, "Variant") or "unknown variant"),
                    result=esc(field(fields, "Result") or "problem"),
                )
            )
    else:
        lines.append("None.")
    lines.append("")

    with open("TESTED.md", "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    os.makedirs("docs", exist_ok=True)
    badge = {
        "schemaVersion": 1,
        "label": "hardware tested",
        "message": f"{reports} report{'s' if reports != 1 else ''} · {nmodels}",
        "color": "brightgreen" if reports else "lightgrey",
    }
    with open(os.path.join("docs", "tested.json"), "w", encoding="utf-8") as handle:
        json.dump(badge, handle, indent=2)
        handle.write("\n")

    print(f"{nunits} · {nmodels} (seed rows: {len(seed)})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["label", "index"])
    parser.add_argument("issue", nargs="?")
    args = parser.parse_args()
    if args.command == "label":
        if not args.issue:
            parser.error("label requires an issue number")
        return cmd_label(args.issue)
    return cmd_index()


if __name__ == "__main__":
    sys.exit(main())

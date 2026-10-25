#!/usr/bin/env python3
"""Portable evidence-linked catalog case recorder. No network or provider execution."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

COLLECTIONS = ("sources", "assessments", "findings", "actions", "attempts", "outcomes")
STAGES = {"audit", "reconcile", "register", "resolve_claims", "manage_delivery", "review_deal",
          "import", "explain_contract", "organize_publishing", "estimate_value", "check_credits", "check_metadata"}
STATES = {
    "sources": {"active", "withdrawn"},
    "assessments": {"prepared", "in_progress", "partial", "complete", "blocked"},
    "findings": {"open", "accepted", "resolved", "not_applicable"},
    "actions": {"prepared", "authorized", "withdrawn"},
    "attempts": {"user_reported_sent", "observed_sent", "unknown_outcome", "acknowledged", "rejected"},
}
OUTCOMES = {
    "provider_decision": {"pending", "accepted", "partially_accepted", "rejected", "superseded", "rematched"},
    "observed_record": {"unchecked", "correct", "partial", "incorrect", "stale"},
    "financial_effect": {"unverified", "adjustment_reported", "remitted", "bank_received", "reversed"},
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Invalid number {x}")))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_case(path):
    case = read_json(path)
    require(case.get("schema_version") == 1, "Unsupported case schema_version")
    require(isinstance(case.get("revision"), int), "Missing case revision")
    for collection in COLLECTIONS:
        require(isinstance(case.get(collection), dict), f"Missing collection {collection}")
    return case


@contextmanager
def lock(path):
    """O_EXCL works across supported hosts; stale locks are never silently removed."""
    lockpath = Path(str(path) + ".lock")
    try:
        fd = os.open(lockpath, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"Case busy: {lockpath}; verify the writer has stopped before removing a stale lock") from exc
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        lockpath.unlink()


def atomic_write(path, data):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def all_records(case):
    return {rid: record for group in COLLECTIONS for rid, record in case[group].items()}


def validate_record(case, group, record):
    require(isinstance(record, dict), "Record must be an object")
    rid = record.get("id")
    require(isinstance(rid, str) and bool(rid.strip()), "Record requires a stable nonempty id")
    require(not any(rid in case[g] for g in COLLECTIONS if g != group), "IDs must be unique across collections")
    require("stale" not in record and "stale_reasons" not in record, "Staleness is maintained by the recorder")
    if group == "outcomes":
        require(record.get("dimension") in OUTCOMES, "Unknown outcome dimension")
        require(record.get("status") in OUTCOMES[record["dimension"]], "Invalid outcome status")
    else:
        require(record.get("status") in STATES[group], f"Invalid {group} status")
    if group == "sources":
        require(isinstance(record.get("version"), str) and record["version"], "Source requires version")
        require(isinstance(record.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", record["sha256"]), "Source requires SHA256 of original bytes")
        require(bool(record.get("locator")), "Source requires an original/durable locator")
        previous = case[group].get(rid)
        if previous and previous["version"] == record["version"]:
            require(previous["sha256"] == record["sha256"], "Changed bytes require a new source version")
        for entry in case.get("history", []):
            historic = entry.get("records", {}).get("sources", {}).get(rid)
            if historic and historic.get("version") == record["version"]:
                require(historic.get("sha256") == record["sha256"], "Historical source version cannot identify different bytes")
        return
    refs = record.get("source_refs")
    require(isinstance(refs, list), "Derived record requires source_refs")
    require(bool(refs) or bool(record.get("evidence_gap")), "Empty evidence requires explicit evidence_gap")
    require(bool(record.get("rule_version")), "Derived record requires rule_version")
    for ref in refs:
        require(isinstance(ref, dict), "Source reference must be an object")
        source = case["sources"].get(ref.get("source_id"))
        require(source and source["version"] == ref.get("version") and source["status"] == "active", "Source reference must identify a current active version")
    records = all_records(case)
    for dep in record.get("depends_on", []):
        require(dep in records and dep != rid, "Dependency must identify another existing record")
        require(not records[dep].get("stale"), "Cannot depend on stale records")
        seen, queue = set(), [dep]
        while queue:
            current = queue.pop()
            require(current != rid, "Cyclic record dependency")
            if current in seen:
                continue
            seen.add(current)
            queue.extend(records.get(current, {}).get("depends_on", []))
    if group in {"assessments", "findings", "actions"}:
        require(record.get("stage") in STAGES, "Unknown stage")
    if group == "findings":
        require(bool(record.get("cause_id")), "Finding requires cause_id to avoid duplicated exposure")
    if group == "actions":
        require(record["stage"] in {"register", "resolve_claims", "manage_delivery"}, "Review stages cannot authorize external actions")
        payload = record.get("payload")
        require(isinstance(payload, dict), "Action requires exact payload")
        for key in ("provider", "operation", "account", "party", "subjects", "scope", "disclosure", "costs"):
            require(key in payload, f"Action payload missing {key}")
        for key in ("provider", "operation", "account", "party"):
            require(isinstance(payload[key], str) and bool(payload[key].strip()), f"Action {key} must be a nonempty string")
        require(isinstance(payload["subjects"], list) and bool(payload["subjects"]) and all(isinstance(x, str) and x.strip() for x in payload["subjects"]), "Action subjects must be nonempty identifiers")
        require(isinstance(payload["scope"], dict) and bool(payload["scope"]), "Action scope must identify its bounded rights/territory/dates")
        require(isinstance(payload["disclosure"], list) and isinstance(payload["costs"], list), "Action disclosure/costs must be explicit lists")
        if record["status"] == "authorized":
            validate_authorization(record)
    if group == "outcomes":
        kinds = {case["sources"][ref["source_id"]].get("evidence_kind") for ref in refs}
        if record["dimension"] == "financial_effect" and record["status"] == "bank_received":
            require("bank_receipt" in kinds, "bank_received requires receiving-account evidence")
        if record["dimension"] == "observed_record" and record["status"] in {"correct", "partial", "incorrect"}:
            require(bool(kinds & {"registry_observation", "destination_observation"}), "Observed record requires destination/registry evidence")
        if record["dimension"] == "provider_decision" and record["status"] not in {"pending"}:
            require(bool(kinds & {"provider_receipt", "provider_communication"}), "Provider decision requires provider response evidence")
    if group in {"attempts", "outcomes"}:
        action = case["actions"].get(record.get("action_id"))
        require(action and not action.get("stale"), "Record requires current non-stale action")
        previous = case[group].get(rid)
        if previous:
            require(previous.get("action_id") == record["action_id"], "An attempt/outcome cannot be reassigned to another action")
        if group == "attempts":
            if previous and previous["status"] == "unknown_outcome" and record["status"] != "unknown_outcome":
                kinds = {case["sources"][ref["source_id"]].get("evidence_kind") for ref in refs}
                require(record["status"] in {"observed_sent", "acknowledged", "rejected"} and bool(kinds & {"provider_receipt", "provider_communication"}), "Unknown outcome requires provider reconciliation evidence")
            require(record.get("payload_sha256") == fingerprint(action["payload"]), "Attempt payload differs from action")
            # A retrospective observation records evidence; it does not grant or execute authority.
            # The caller must preflight authority before an actual external operation.
            if record["status"] == "observed_sent":
                unresolved = [a for a in case["attempts"].values() if a.get("action_id") == record["action_id"] and a["id"] != rid and a["status"] == "unknown_outcome"]
                require(not unresolved, "Reconcile existing unknown outcome before a new send")
        if record.get("status") not in {"user_reported_sent", "unknown_outcome", "pending", "unchecked", "unverified"}:
            require(bool(refs), "Observed outcomes require source evidence, not only an evidence gap")


def validate_authorization(action):
    auth = action.get("authorization", {})
    require(bool(auth.get("reference")), "Authorization requires actual user instruction reference")
    require(auth.get("payload_sha256") == fingerprint(action["payload"]), "Authorization does not match exact payload")
    require(auth.get("scope") == action["payload"]["scope"], "Authorization scope differs from payload")
    try:
        expiry = datetime.fromisoformat(auth["valid_until"].replace("Z", "+00:00"))
        require(expiry.tzinfo is not None and expiry > datetime.now(timezone.utc), "Authorization expired or has no timezone")
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Authorization requires an ISO UTC valid_until") from exc


def invalidate(case, changed, reason):
    affected = {changed}
    while True:
        added = set()
        for group in COLLECTIONS[1:]:
            for rid, record in case[group].items():
                dependencies = set(record.get("depends_on", [])) | {ref["source_id"] for ref in record.get("source_refs", [])}
                if record.get("action_id"):
                    dependencies.add(record["action_id"])
                if rid not in affected and dependencies & affected:
                    record["stale"] = True
                    record.setdefault("stale_reasons", []).append(reason)
                    added.add(rid)
        if not added:
            return
        affected |= added


def put(case, group, record):
    record = copy.deepcopy(record)
    validate_record(case, group, record)
    previous = case[group].get(record["id"])
    if previous == record:
        return False
    if previous:
        invalidate(case, record["id"], f"{group}/{record['id']} changed at revision {case['revision'] + 1}")
    case[group][record["id"]] = record
    return True


def summary(case):
    records = []
    for group in COLLECTIONS:
        for record in case[group].values():
            projected = {"collection": group, "id": record["id"]}
            # Validate each selected value as well as its field name: arbitrary nested
            # extension data must never flow into a status-only projection.
            require(isinstance(record["id"], str), "Invalid record ID")
            if isinstance(record.get("status"), str):
                projected["status"] = record["status"]
            if group in {"assessments", "findings", "actions"} and isinstance(record.get("stage"), str) and record["stage"] in STAGES:
                projected["stage"] = record["stage"]
            if group == "outcomes" and isinstance(record.get("dimension"), str) and record["dimension"] in OUTCOMES:
                projected["dimension"] = record["dimension"]
            if isinstance(record.get("stale"), bool):
                projected["stale"] = record["stale"]
            records.append(projected)
    return {"schema_version": 1, "case_id": case["case_id"], "workspace_id": case["workspace_id"],
            "revision": case["revision"], "counts": {c: len(case[c]) for c in COLLECTIONS}, "records": records}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--file", required=True)
    init.add_argument("--case-id", required=True)
    init.add_argument("--workspace-id", required=True)
    init.add_argument("--scope", default="")
    digest = sub.add_parser("hash")
    digest.add_argument("--input", required=True)
    for command in ("put", "withdraw", "status", "export", "preflight"):
        p = sub.add_parser(command)
        p.add_argument("--file", required=True)
        if command in {"put", "withdraw"}:
            p.add_argument("--expected-revision", type=int, required=True)
        if command == "put":
            p.add_argument("--collection", choices=COLLECTIONS, required=True)
            p.add_argument("--record", required=True)
        if command == "withdraw":
            p.add_argument("--source-id", required=True)
        if command == "export":
            p.add_argument("--output", required=True)
        if command == "preflight":
            p.add_argument("--action-id", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            h = hashlib.sha256()
            with open(args.input, "rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
            print(h.hexdigest())
            return 0
        path = Path(args.file)
        if args.command == "init":
            require(args.case_id.strip() and args.workspace_id.strip(), "Case and workspace IDs cannot be empty")
            with lock(path):
                require(not path.exists(), "Case already exists; use status to resume")
                case = {"schema_version": 1, "case_id": args.case_id, "workspace_id": args.workspace_id,
                        "revision": 0, "scope": args.scope, "history": [], **{c: {} for c in COLLECTIONS}}
                atomic_write(path, case)
        elif args.command in {"put", "withdraw"}:
            with lock(path):
                case = read_case(path)
                require(case["revision"] == args.expected_revision, "Revision conflict; reread and reconcile current case")
                before = copy.deepcopy(case)
                if args.command == "put":
                    changed = put(case, args.collection, read_json(args.record))
                else:
                    require(args.source_id in case["sources"], "Unknown source")
                    source = copy.deepcopy(case["sources"][args.source_id])
                    source["status"] = "withdrawn"
                    changed = put(case, "sources", source)
                if changed:
                    case["revision"] += 1
                    # Full prior records preserve changed and invalidated facts without recursive snapshots.
                    case["history"].append({"revision": before["revision"], "at": now(),
                                            "records": {c: before[c] for c in COLLECTIONS}})
                    atomic_write(path, case)
        else:
            case = read_case(path)
            if args.command == "preflight":
                action = case["actions"].get(args.action_id)
                require(action and action["status"] == "authorized" and not action.get("stale"), "Action is not currently authorized")
                validate_authorization(action)
                require(not any(a["action_id"] == args.action_id and a["status"] == "unknown_outcome" for a in case["attempts"].values()), "Unknown outcome must be reconciled before retry")
                require(not any(o["action_id"] == args.action_id and o["dimension"] == "provider_decision" and o["status"] in {"accepted", "partially_accepted"} and not o.get("stale") for o in case["outcomes"].values()), "Do not resend accepted items; prepare a separate action for unresolved items")
                print(json.dumps({"local_preflight": "passed", "external_preflight": "required", "payload_sha256": fingerprint(action["payload"])}))
                return 0
            if args.command == "export":
                require(Path(args.output).resolve() != path.resolve(), "Export cannot overwrite source case")
                require(not Path(args.output).exists(), "Export already exists; choose a new destination")
                atomic_write(args.output, summary(case))
        print(json.dumps(summary(case), indent=2))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"catalog-case: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

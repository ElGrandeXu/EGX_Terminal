"""Load the canonical registry of known active project harness surfaces."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


REGISTRY_PATH = Path("governance/neutral-root-surfaces.json")


class NeutralRootPolicyError(RuntimeError):
    """The neutral-root surface registry is absent or malformed."""


@dataclass(frozen=True, order=True)
class RegisteredSurface:
    path: Path
    kind: str
    owners: tuple[str, ...]


def load_registered_surfaces(policy_root: Path) -> tuple[RegisteredSurface, ...]:
    path = policy_root / REGISTRY_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NeutralRootPolicyError(f"cannot read {REGISTRY_PATH.as_posix()}") from error
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "guarantee", "verified_on", "sources", "surfaces"}
        or payload.get("schema_version") != 1
        or payload.get("guarantee") != "KNOWN_REGISTERED_ACTIVE_PROJECT_SURFACES"
        or not isinstance(payload.get("verified_on"), str)
        or not isinstance(payload.get("sources"), list)
        or not payload["sources"]
        or not isinstance(payload.get("surfaces"), list)
        or not payload["surfaces"]
    ):
        raise NeutralRootPolicyError(f"invalid {REGISTRY_PATH.as_posix()} schema")
    surfaces: list[RegisteredSurface] = []
    seen: set[str] = set()
    for source in payload["sources"]:
        if (
            not isinstance(source, dict)
            or set(source) != {"harness", "url", "observed_surfaces"}
            or not isinstance(source["harness"], str)
            or not isinstance(source["url"], str)
            or not source["url"].startswith("https://")
            or not isinstance(source["observed_surfaces"], list)
            or not source["observed_surfaces"]
        ):
            raise NeutralRootPolicyError(f"invalid source in {REGISTRY_PATH.as_posix()}")
    for item in payload["surfaces"]:
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "kind", "owners"}
            or not isinstance(item["path"], str)
            or item["kind"] not in {"path", "path_prefix"}
            or not isinstance(item["owners"], list)
            or not item["owners"]
            or not all(isinstance(owner, str) and owner for owner in item["owners"])
        ):
            raise NeutralRootPolicyError(f"invalid surface in {REGISTRY_PATH.as_posix()}")
        normalized = PurePosixPath(item["path"])
        if normalized.is_absolute() or ".." in normalized.parts or normalized.as_posix() != item["path"]:
            raise NeutralRootPolicyError(f"unsafe surface in {REGISTRY_PATH.as_posix()}")
        if item["path"] in seen:
            raise NeutralRootPolicyError(f"duplicate surface in {REGISTRY_PATH.as_posix()}")
        seen.add(item["path"])
        surfaces.append(RegisteredSurface(Path(*normalized.parts), item["kind"], tuple(item["owners"])))
    return tuple(surfaces)

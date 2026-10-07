#!/usr/bin/env python3
"""Shared ownership engine for the Unix installer and uninstaller.

The engine treats both the v2 per-file manifest and the reviewed legacy
inventory as ownership proofs. It preflights the complete operation before
moving any file, uses no-follow directory descriptors for profile mutations,
and replaces the manifest only after the payload is complete.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


OWNER = "claude-blog-unix-installer"
LEGACY_OWNER = "claude-blog-reviewed-legacy-payload"
HEX64 = re.compile(r"[0-9a-f]{64}")


class DuplicateJSONKey(ValueError):
    pass


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKey(key)
        result[key] = value
    return result


def allowed_relative(relative: PurePosixPath) -> bool:
    parts = relative.parts
    if not parts or relative.is_absolute() or ".." in parts or "." in parts:
        return False
    if len(parts) >= 3 and parts[0] == "skills":
        return parts[1] == "blog" or parts[1].startswith("blog-")
    if len(parts) == 2 and parts[0] == "agents":
        return parts[1].startswith("blog-") and parts[1].endswith(".md")
    return len(parts) == 2 and parts[0] == "scripts" and parts[1].endswith(".py")


@dataclass(frozen=True)
class Incoming:
    source: Path
    mode: int


class ProfileFS:
    """No-follow file operations rooted at one Claude profile directory."""

    def __init__(self, root: Path):
        self.root = root.absolute()
        current_path = Path(self.root.anchor)
        current = os.open(
            current_path,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            for part in self.root.parts[1:]:
                current_path /= part
                try:
                    following = os.open(
                        part,
                        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=current,
                    )
                except FileNotFoundError:
                    os.mkdir(part, 0o755, dir_fd=current)
                    following = os.open(
                        part,
                        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=current,
                    )
                except OSError as exc:
                    fail(f"Claude profile path has an unsafe ancestor at {current_path}: {exc.strerror}")
                os.close(current)
                current = following
        finally:
            os.close(current)

    def relative(self, path: Path) -> PurePosixPath:
        raw = str(path)
        if not path.is_absolute() or ".." in Path(raw).parts:
            fail(f"unsafe path: {path}")
        try:
            value = path.relative_to(self.root)
        except ValueError:
            fail(f"unsafe path outside Claude profile: {path}")
        relative = PurePosixPath(*value.parts)
        if not allowed_relative(relative):
            fail(f"unsafe path: {path}")
        return relative

    def absolute(self, relative: PurePosixPath) -> Path:
        if not allowed_relative(relative):
            fail(f"unsafe relative installation path: {relative}")
        return self.root.joinpath(*relative.parts)

    def _root_fd(self) -> int:
        return os.open(
            self.root,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
        )

    def root_status(self, name: str) -> os.stat_result | None:
        root = self._root_fd()
        try:
            try:
                return os.stat(name, dir_fd=root, follow_symlinks=False)
            except FileNotFoundError:
                return None
        finally:
            os.close(root)

    def read_root_file(self, name: str) -> bytes:
        root = self._root_fd()
        try:
            fd = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=root)
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    fail(f"profile metadata is not a regular file: {self.root / name}")
                chunks: list[bytes] = []
                while chunk := os.read(fd, 1024 * 1024):
                    chunks.append(chunk)
                return b"".join(chunks)
            finally:
                os.close(fd)
        finally:
            os.close(root)

    def write_root_file(self, name: str, payload: bytes, mode: int) -> None:
        root = self._root_fd()
        temporary = f".{name}.claude-blog-{os.getpid()}"
        fd = -1
        try:
            fd = os.open(
                temporary,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                mode,
                dir_fd=root,
            )
            remaining = memoryview(payload)
            while remaining:
                written = os.write(fd, remaining)
                remaining = remaining[written:]
            os.fchmod(fd, mode)
            os.close(fd)
            fd = -1
            os.rename(temporary, name, src_dir_fd=root, dst_dir_fd=root)
        finally:
            if fd >= 0:
                os.close(fd)
            try:
                os.unlink(temporary, dir_fd=root)
            except FileNotFoundError:
                pass
            os.close(root)

    def unlink_root_file(self, name: str) -> None:
        root = self._root_fd()
        try:
            os.unlink(name, dir_fd=root)
        finally:
            os.close(root)

    def parent_fd(self, relative: PurePosixPath, *, create: bool = False) -> int:
        if not allowed_relative(relative):
            fail(f"unsafe relative installation path: {relative}")
        current = self._root_fd()
        try:
            for part in relative.parts[:-1]:
                try:
                    following = os.open(
                        part,
                        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=current,
                    )
                except FileNotFoundError:
                    if not create:
                        raise
                    os.mkdir(part, 0o755, dir_fd=current)
                    following = os.open(
                        part,
                        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=current,
                    )
                except OSError as exc:
                    fail(f"installation path has an unsafe parent at {part}: {exc.strerror}")
                os.close(current)
                current = following
            return current
        except BaseException:
            os.close(current)
            raise

    def status(self, relative: PurePosixPath) -> os.stat_result | None:
        try:
            parent = self.parent_fd(relative)
        except FileNotFoundError:
            return None
        try:
            try:
                return os.stat(relative.name, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                return None
        finally:
            os.close(parent)

    def hash(self, relative: PurePosixPath) -> str:
        parent = self.parent_fd(relative)
        try:
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(relative.name, flags, dir_fd=parent)
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    fail(f"managed installation path is not a regular file: {self.absolute(relative)}")
                value = hashlib.sha256()
                while chunk := os.read(fd, 1024 * 1024):
                    value.update(chunk)
                return value.hexdigest()
            finally:
                os.close(fd)
        finally:
            os.close(parent)

    def write(self, relative: PurePosixPath, source: Path, mode: int) -> None:
        parent = self.parent_fd(relative, create=True)
        temporary = f".{relative.name}.claude-blog-{os.getpid()}"
        source_fd = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        target_fd = -1
        try:
            if not stat.S_ISREG(os.fstat(source_fd).st_mode):
                fail(f"source payload is not a regular file: {source}")
            target_fd = os.open(
                temporary,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                mode,
                dir_fd=parent,
            )
            while chunk := os.read(source_fd, 1024 * 1024):
                remaining = memoryview(chunk)
                while remaining:
                    written = os.write(target_fd, remaining)
                    remaining = remaining[written:]
            os.fchmod(target_fd, mode)
            os.close(target_fd)
            target_fd = -1
            os.rename(temporary, relative.name, src_dir_fd=parent, dst_dir_fd=parent)
        finally:
            if target_fd >= 0:
                os.close(target_fd)
            os.close(source_fd)
            try:
                os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError:
                pass
            os.close(parent)

    def unlink(self, relative: PurePosixPath) -> None:
        parent = self.parent_fd(relative)
        try:
            os.unlink(relative.name, dir_fd=parent)
        finally:
            os.close(parent)

    def prune(self, relative: PurePosixPath) -> None:
        parts = list(relative.parts[:-1])
        while parts:
            parent_parts = parts[:-1]
            name = parts[-1]
            current = self._root_fd()
            try:
                safe = True
                for part in parent_parts:
                    try:
                        following = os.open(
                            part,
                            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                            dir_fd=current,
                        )
                    except OSError:
                        safe = False
                        break
                    os.close(current)
                    current = following
                if not safe:
                    return
                try:
                    os.rmdir(name, dir_fd=current)
                except OSError:
                    return
            finally:
                os.close(current)
            parts.pop()


class Transaction:
    def __init__(self, fs: ProfileFS):
        self.fs = fs
        self.directory = Path(tempfile.mkdtemp(prefix=".claude-blog-transaction-", dir=fs.root))
        self.directory.chmod(0o700)
        self.staged: list[tuple[PurePosixPath, Path]] = []
        self.written: list[PurePosixPath] = []
        self.committed = False

    def stage(self, relative: PurePosixPath) -> None:
        status = self.fs.status(relative)
        if status is None:
            return
        if not stat.S_ISREG(status.st_mode):
            fail(f"managed installation path is not a regular file: {self.fs.absolute(relative)}")
        parent = self.fs.parent_fd(relative)
        staged = self.directory / f"{len(self.staged):06d}"
        stage_fd = os.open(
            self.directory,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            os.rename(relative.name, staged.name, src_dir_fd=parent, dst_dir_fd=stage_fd)
        finally:
            os.close(stage_fd)
            os.close(parent)
        self.staged.append((relative, staged))

    def write(self, relative: PurePosixPath, incoming: Incoming) -> None:
        self.fs.write(relative, incoming.source, incoming.mode)
        self.written.append(relative)

    def rollback(self) -> None:
        if self.committed:
            return
        for relative in reversed(self.written):
            try:
                if self.fs.status(relative) is not None:
                    self.fs.unlink(relative)
            except OSError:
                pass
        for relative, staged in reversed(self.staged):
            if not staged.exists():
                continue
            parent = self.fs.parent_fd(relative, create=True)
            stage_fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0))
            try:
                os.rename(staged.name, relative.name, src_dir_fd=stage_fd, dst_dir_fd=parent)
            finally:
                os.close(stage_fd)
                os.close(parent)

    def finish(self) -> None:
        self.committed = True
        shutil.rmtree(self.directory, ignore_errors=True)

    def close(self) -> None:
        if not self.committed:
            self.rollback()
            shutil.rmtree(self.directory, ignore_errors=True)


def add_file(incoming: dict[PurePosixPath, Incoming], source: Path, relative: str, *, executable: bool = False) -> None:
    key = PurePosixPath(relative)
    if not allowed_relative(key) or key in incoming:
        fail(f"invalid or duplicate installation destination: {relative}")
    if source.is_symlink() or not source.is_file():
        fail(f"source payload is not a regular file: {source}")
    mode = stat.S_IMODE(source.stat().st_mode)
    if executable:
        mode |= stat.S_IXUSR
    incoming[key] = Incoming(source, mode)


def add_tree(incoming: dict[PurePosixPath, Incoming], source: Path, prefix: str, *, executable_python: bool = False) -> None:
    if not source.exists():
        return
    if source.is_symlink() or not source.is_dir():
        fail(f"source payload directory is unsafe: {source}")
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            fail(f"source payload contains a symlink: {path}")
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = PurePosixPath(prefix) / PurePosixPath(*path.relative_to(source).parts)
        add_file(incoming, path, str(relative), executable=executable_python and path.suffix == ".py")


def build_inventory(source: Path) -> tuple[dict[PurePosixPath, Incoming], list[str], list[str], list[str]]:
    incoming: dict[PurePosixPath, Incoming] = {}
    skills: list[str] = []
    agents: list[str] = []
    scripts: list[str] = []
    blog = source / "skills/blog"
    add_file(incoming, blog / "SKILL.md", "skills/blog/SKILL.md")
    add_tree(incoming, blog / "references", "skills/blog/references")
    add_tree(incoming, blog / "templates", "skills/blog/templates")
    ledger = source / "data/google-updates.json"
    if ledger.is_file():
        add_file(incoming, ledger, "skills/blog/data/google-updates.json")
    for skill_dir in sorted((source / "skills").iterdir()):
        if not skill_dir.is_dir() or skill_dir.name == "blog":
            continue
        if skill_dir.is_symlink() or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_dir.name):
            fail(f"unsafe source skill directory: {skill_dir}")
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        skills.append(skill_dir.name)
        add_file(incoming, skill_md, f"skills/{skill_dir.name}/SKILL.md")
        for payload in ("references", "scripts", "assets", "templates"):
            add_tree(
                incoming,
                skill_dir / payload,
                f"skills/{skill_dir.name}/{payload}",
                executable_python=payload == "scripts",
            )
    for agent in sorted((source / "agents").glob("*.md")):
        agents.append(agent.name)
        add_file(incoming, agent, f"agents/{agent.name}")
    # Public installer contract: scripts/*.py
    for script in sorted((source / "scripts").glob("*.py")):
        scripts.append(script.name)
        add_file(incoming, script, f"scripts/{script.name}", executable=True)
        if script.name == "analyze_blog.py":
            add_file(incoming, script, "skills/blog/scripts/analyze_blog.py", executable=True)
    return incoming, skills, agents, scripts


def load_legacy_inventory(path: Path) -> dict[PurePosixPath, set[str]]:
    if path.is_symlink() or not path.is_file():
        fail(f"reviewed legacy ownership inventory is unavailable: {path}")
    try:
        data = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    except DuplicateJSONKey as exc:
        fail(f"reviewed legacy ownership inventory has a duplicate key: {exc}")
    except (UnicodeDecodeError, ValueError):
        fail(f"reviewed legacy ownership inventory is invalid: {path}")
    if data.get("schema_version") != 1 or data.get("owner") != LEGACY_OWNER or not isinstance(data.get("files"), dict):
        fail(f"reviewed legacy ownership inventory has an unsupported schema: {path}")
    result: dict[PurePosixPath, set[str]] = {}
    for raw, records in data["files"].items():
        relative = PurePosixPath(raw)
        if relative in result or not allowed_relative(relative) or not isinstance(records, list) or not records:
            fail(f"reviewed legacy ownership inventory contains an unsafe path: {raw}")
        if any(
            not isinstance(record, dict)
            or not isinstance(record.get("sha256"), str)
            or not HEX64.fullmatch(record["sha256"])
            for record in records
        ):
            fail(f"reviewed legacy ownership inventory has an invalid record for: {raw}")
        hashes = {record["sha256"] for record in records}
        if not hashes:
            fail(f"reviewed legacy ownership inventory has no valid hash for: {raw}")
        result[relative] = hashes
    return result


def load_v2(fs: ProfileFS, manifest: Path) -> tuple[dict[PurePosixPath, str] | None, bytes]:
    status = fs.root_status(manifest.name)
    if status is None:
        return None, b""
    if not stat.S_ISREG(status.st_mode):
        fail(f"installation manifest is not a regular file: {manifest}")
    raw = fs.read_root_file(manifest.name)
    try:
        data = json.loads(raw, object_pairs_hook=unique_object)
    except DuplicateJSONKey as exc:
        fail(f"installation manifest has a duplicate key: {exc}")
    except (UnicodeDecodeError, ValueError):
        return None, raw
    if data.get("schema_version") != 2 or data.get("owner") != OWNER or not isinstance(data.get("files"), dict):
        fail(f"unrecognized installation manifest: {manifest}")
    managed: dict[PurePosixPath, str] = {}
    for raw_path, record in data["files"].items():
        path = Path(raw_path)
        relative = fs.relative(path)
        if relative in managed:
            fail(f"installation manifest contains a duplicate path: {raw_path}")
        if not isinstance(record, dict) or not isinstance(record.get("sha256"), str) or not HEX64.fullmatch(record["sha256"]):
            fail(f"installation manifest has an invalid record: {raw_path}")
        managed[relative] = record["sha256"]
    return managed, raw


def legacy_scopes(fs: ProfileFS, raw: bytes, known: dict[PurePosixPath, set[str]]) -> list[PurePosixPath]:
    try:
        values = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        fail("legacy installation manifest is not UTF-8")
    scopes: list[PurePosixPath] = []
    known_skill_dirs = {PurePosixPath(*path.parts[:2]) for path in known if path.parts[0] == "skills"}
    for value in values:
        if not value:
            continue
        path = Path(value)
        if not path.is_absolute() or ".." in path.parts:
            fail(f"legacy installation manifest contains an unsafe path: {value}")
        try:
            relative = PurePosixPath(*path.relative_to(fs.root).parts)
        except ValueError:
            fail(f"legacy installation manifest contains an unsafe path: {value}")
        if relative in known_skill_dirs or relative in known:
            scopes.append(relative)
        else:
            fail(f"legacy installation manifest contains an unreviewed scope: {value}")
    if not scopes:
        fail("legacy installation manifest has no reviewed ownership scopes")
    return scopes


def covered(path: PurePosixPath, scopes: list[PurePosixPath]) -> bool:
    return any(path == scope or (len(scope.parts) == 2 and scope.parts[0] == "skills" and path.parts[:2] == scope.parts) for scope in scopes)


def preflight_v2(fs: ProfileFS, managed: dict[PurePosixPath, str]) -> None:
    for relative, expected in managed.items():
        status = fs.status(relative)
        if status is None or not stat.S_ISREG(status.st_mode):
            fail(f"managed installation file is missing or replaced: {fs.absolute(relative)}")
        if fs.hash(relative) != expected:
            fail(f"managed installation file was modified: {fs.absolute(relative)}")


def preflight_legacy(fs: ProfileFS, known: dict[PurePosixPath, set[str]], scopes: list[PurePosixPath]) -> set[PurePosixPath]:
    owned: set[PurePosixPath] = set()
    for relative, hashes in known.items():
        if not covered(relative, scopes):
            continue
        status = fs.status(relative)
        if status is None:
            continue
        if not stat.S_ISREG(status.st_mode):
            fail(f"reviewed legacy path is missing or replaced: {fs.absolute(relative)}")
        if fs.hash(relative) not in hashes:
            fail(f"reviewed legacy file was modified or is unknown: {fs.absolute(relative)}")
        owned.add(relative)
    return owned


def validate_manifest_path(fs: ProfileFS, manifest: Path) -> None:
    if manifest.parent != fs.root or manifest.name != "claude-blog-manifest.txt":
        fail(f"unsafe manifest path: {manifest}")


def stage_manifest(transaction: Transaction, fs: ProfileFS, manifest: Path) -> Path:
    status = fs.root_status(manifest.name)
    if status is None or not stat.S_ISREG(status.st_mode):
        fail(f"installation manifest is not a regular file: {manifest}")
    staged = transaction.directory / "manifest"
    root = fs._root_fd()
    stage = os.open(
        transaction.directory,
        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.rename(manifest.name, staged.name, src_dir_fd=root, dst_dir_fd=stage)
    finally:
        os.close(stage)
        os.close(root)
    return staged


def restore_manifest(fs: ProfileFS, manifest: Path, staged: Path) -> None:
    if staged.exists():
        root = fs._root_fd()
        stage = os.open(
            staged.parent,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            os.rename(staged.name, manifest.name, src_dir_fd=stage, dst_dir_fd=root)
        finally:
            os.close(stage)
            os.close(root)


def write_manifest(manifest: Path, version: str, fs: ProfileFS, incoming: dict[PurePosixPath, Incoming]) -> None:
    records = {
        str(fs.absolute(relative)): {"sha256": fs.hash(relative), "mode": incoming[relative].mode}
        for relative in sorted(incoming, key=str)
    }
    payload = (json.dumps({
        "schema_version": 2,
        "owner": OWNER,
        "version": version,
        "files": records,
    }, indent=2, sort_keys=True) + "\n").encode()
    fs.write_root_file(manifest.name, payload, 0o600)


def install(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    fs = ProfileFS(Path(args.profile))
    manifest = Path(args.manifest)
    validate_manifest_path(fs, manifest)
    incoming, skill_names, agent_names, script_names = build_inventory(source)
    managed, raw_manifest = load_v2(fs, manifest)
    if managed is not None:
        preflight_v2(fs, managed)
        owned = set(managed)
    elif raw_manifest:
        known = load_legacy_inventory(Path(args.legacy_inventory))
        scopes = legacy_scopes(fs, raw_manifest, known)
        owned = preflight_legacy(fs, known, scopes)
    else:
        owned = set()
    for relative in incoming:
        status = fs.status(relative)
        if status is not None and relative not in owned:
            fail(f"refusing to overwrite an unowned existing file: {fs.absolute(relative)}")

    transaction = Transaction(fs)
    staged_manifest: Path | None = None
    try:
        for relative in sorted(owned, key=str):
            transaction.stage(relative)
        if raw_manifest:
            staged_manifest = stage_manifest(transaction, fs, manifest)
        for relative, item in incoming.items():
            transaction.write(relative, item)
        write_manifest(manifest, args.version, fs, incoming)
        transaction.finish()
    except BaseException:
        if fs.root_status(manifest.name) is not None and staged_manifest is not None:
            fs.unlink_root_file(manifest.name)
        if staged_manifest is not None:
            restore_manifest(fs, manifest, staged_manifest)
        transaction.close()
        raise
    for relative in sorted(owned - set(incoming), key=lambda value: len(value.parts), reverse=True):
        fs.prune(relative)
    Path(args.stats).write_text(json.dumps({
        "sub_skill_count": len(skill_names),
        "agent_count": len(agent_names),
        "root_script_count": len(script_names),
    }) + "\n", encoding="utf-8")
    print("→ Creating directories...")
    print("→ Installing main skill: blog...")
    print("→ Installing reference files...")
    if (source / "skills/blog/templates").is_dir():
        print("→ Installing content templates...")
    if (source / "data/google-updates.json").is_file():
        print("→ Installing Google update ledger...")
    print("→ Installing sub-skills...")
    for name in skill_names:
        print(f"  + {name}")
    print("→ Installing agents...")
    for name in agent_names:
        print(f"  + {Path(name).stem}")
    print("→ Installing scripts...")
    for name in script_names:
        print(f"  + scripts/{name}")


def uninstall(args: argparse.Namespace) -> None:
    fs = ProfileFS(Path(args.profile))
    manifest = Path(args.manifest)
    validate_manifest_path(fs, manifest)
    if fs.root_status(manifest.name) is None:
        return
    managed, raw_manifest = load_v2(fs, manifest)
    if managed is not None:
        preflight_v2(fs, managed)
        owned = set(managed)
    else:
        if not args.legacy_inventory:
            fail("legacy uninstall requires the complete reviewed repository and ownership inventory")
        known = load_legacy_inventory(Path(args.legacy_inventory))
        scopes = legacy_scopes(fs, raw_manifest, known)
        owned = preflight_legacy(fs, known, scopes)
    transaction = Transaction(fs)
    staged_manifest: Path | None = None
    try:
        for relative in sorted(owned, key=str):
            transaction.stage(relative)
            print(f"  Removed verified package file: {fs.absolute(relative)}")
        staged_manifest = stage_manifest(transaction, fs, manifest)
        transaction.finish()
    except BaseException:
        if staged_manifest is not None:
            restore_manifest(fs, manifest, staged_manifest)
        transaction.close()
        raise
    for relative in sorted(owned, key=lambda value: len(value.parts), reverse=True):
        fs.prune(relative)
    print(f"  Removed: {manifest}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    subparsers = result.add_subparsers(dest="command", required=True)
    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("--source", required=True)
    install_parser.add_argument("--profile", required=True)
    install_parser.add_argument("--manifest", required=True)
    install_parser.add_argument("--stats", required=True)
    install_parser.add_argument("--version", required=True)
    install_parser.add_argument("--legacy-inventory", required=True)
    install_parser.set_defaults(action=install)
    uninstall_parser = subparsers.add_parser("uninstall")
    uninstall_parser.add_argument("--profile", required=True)
    uninstall_parser.add_argument("--manifest", required=True)
    uninstall_parser.add_argument("--legacy-inventory")
    uninstall_parser.set_defaults(action=uninstall)
    return result


def main() -> int:
    args = parser().parse_args()
    args.action(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

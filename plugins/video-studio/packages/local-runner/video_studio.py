#!/usr/bin/env python3
"""Portable Video Studio editing transfer and immutable project snapshots.

No third-party Python dependencies. Never executes commands from downloaded projects.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from datetime import datetime, timezone

VERSION = "0.1.0"
CHUNK_SIZE = 1024 * 1024
MAX_BUNDLE_BYTES = 20 * 1024**3
SKIP_DIRS = {".git", "node_modules", ".cache", "__pycache__", ".venv", "venv", ".next"}
SECRET_NAMES = {".env", ".env.local", ".env.production", ".env.development", "credentials.json", "session.json", ".npmrc", ".pypirc", ".netrc", ".git-credentials", "id_rsa", "id_ed25519"}


class RunnerError(Exception):
    pass


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
            result.update(block)
    return result.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def safe_relative(value):
    if not isinstance(value, str) or not value or "\\" in value or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise RunnerError("Invalid relative file path.")
    path = PurePosixPath(value)
    parts = value.split("/")
    if path.is_absolute() or any(part in ("..", ".", "") for part in parts) or any(char in value for char in ':<>"|?*'):
        raise RunnerError("File paths must stay inside the workspace and use portable filenames.")
    for part in parts:
        device = part.split(".", 1)[0].rstrip(" .").upper()
        if part.endswith((".", " ")) or device in {"CON", "PRN", "AUX", "NUL"} or re.fullmatch(r"(?:COM|LPT)[1-9]", device):
            raise RunnerError("File path is not portable to Windows: " + value)
    return Path(*path.parts)


def portable_path_key(value):
    safe_relative(value)
    return value.casefold()


def require_unique_paths(paths):
    seen = set()
    for value in paths:
        key = portable_path_key(value)
        if key in seen:
            raise RunnerError("Paths collide on a case-insensitive filesystem: " + value)
        seen.add(key)


def inside(root, relative):
    root = Path(root).resolve()
    path = root / safe_relative(relative)
    if not path.resolve().is_relative_to(root):
        raise RunnerError("File path escapes the workspace.")
    return path


def run(command):
    try:
        return subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
    except FileNotFoundError:
        raise RunnerError("Required executable is missing: " + command[0]) from None
    except subprocess.CalledProcessError as exc:
        raise RunnerError("Command failed: " + command[0] + ". " + exc.stderr[-1800:]) from None


def doctor():
    tools = {name: shutil.which(name) for name in ("ffmpeg", "ffprobe", "node", "npm")}
    required = {"python": sys.version_info >= (3, 9), "ffmpeg": bool(tools["ffmpeg"]), "ffprobe": bool(tools["ffprobe"])}
    return {"runnerVersion": VERSION, "pythonVersion": sys.version.split()[0], "required": required,
            "tools": tools, "ready": all(required.values()),
            "optional": "Node/npm are required only for projects that use a Node renderer. Install that project's locked dependencies separately."}


def probe(path):
    result = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]))
    streams = result.get("streams", [])
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    if not videos:
        raise RunnerError("The export has no video stream.")
    duration = float(result.get("format", {}).get("duration", 0))
    if not duration > 0:
        raise RunnerError("The export has no valid duration.")
    return {"durationSeconds": duration, "width": videos[0].get("width"), "height": videos[0].get("height"),
            "hasAudio": any(stream.get("codec_type") == "audio" for stream in streams)}


def smoke(workspace):
    root = Path(workspace).resolve()
    root.mkdir(parents=True, exist_ok=True)
    output = root / "smoke.mp4"
    if output.exists():
        raise RunnerError("Smoke output already exists. Choose a new workspace.")
    run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "color=c=0x233347:s=320x568:r=24:d=1",
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-movflags", "+faststart", str(output)])
    run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(output), "-frames:v", "1", str(root / "smoke-frame.png")])
    result = {"export": str(output), "frame": str(root / "smoke-frame.png"), "sha256": digest(output), **probe(output)}
    write_json(root / "smoke-check.json", result)
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RunnerError("Editing connections must not redirect. Use the exact session endpoint.")


class EditingClient:
    def __init__(self, endpoint, token):
        parsed = urllib.parse.urlparse(endpoint or "")
        if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost", "::1")):
            raise RunnerError("Use an HTTPS editing endpoint (HTTP is allowed only on localhost for tests).")
        if parsed.username or parsed.password or parsed.fragment or parsed.query:
            raise RunnerError("Editing endpoint must not contain credentials, query parameters, or fragments.")
        if not token or any(char in token for char in "\r\n"):
            raise RunnerError("A scoped editing session token is required.")
        self.endpoint, self.token = endpoint, token
        self.opener = urllib.request.build_opener(NoRedirect())

    def call(self, name, arguments):
        body = json.dumps({"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "tools/call",
                           "params": {"name": name, "arguments": arguments}}).encode()
        request = urllib.request.Request(self.endpoint, data=body, headers={"Authorization": "Bearer " + self.token,
            "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
        try:
            with self.opener.open(request, timeout=120) as response:
                raw = response.read(12 * CHUNK_SIZE)
                if len(raw) >= 12 * CHUNK_SIZE:
                    raise RunnerError("The server response exceeded the transfer limit.")
                text = raw.decode("utf-8")
                if response.headers.get_content_type() == "text/event-stream":
                    events = [json.loads(line[5:].strip()) for line in text.splitlines() if line.startswith("data:")]
                    payload = next((item for item in reversed(events) if "result" in item or "error" in item), {})
                else:
                    payload = json.loads(text)
        except urllib.error.HTTPError as exc:
            raise RunnerError("Editing request failed (HTTP %s). Renew the session or check your project access." % exc.code) from None
        except urllib.error.URLError:
            raise RunnerError("Could not reach the editing endpoint. Check the URL and connection.") from None
        if payload.get("error"):
            raise RunnerError(str(payload["error"].get("message", "Editing request failed.")))
        result = payload.get("result", {})
        if result.get("isError"):
            raise RunnerError("; ".join(item.get("text", "") for item in result.get("content", []) if item.get("type") == "text"))
        if "structuredContent" in result:
            return result["structuredContent"]
        content = result.get("content", [])
        if content:
            return json.loads(next(item["text"] for item in content if item.get("type") == "text"))
        return result


def load_client(args):
    endpoint, token = args.endpoint, os.environ.get("VIDEO_STUDIO_EDIT_TOKEN")
    if args.session_file:
        path = Path(args.session_file)
        if os.name != "nt" and stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise RunnerError("Session files must be private. Run chmod 600 on the session file.")
        session = json.loads(path.read_text(encoding="utf-8"))
        endpoint = endpoint or session.get("endpoint")
        token = token or session.get("token")
        expires = session.get("expiresAt")
        if expires:
            if isinstance(expires, (int, float)):
                expiry = datetime.fromtimestamp(expires / 1000, timezone.utc)
            elif isinstance(expires, str):
                expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))
            else:
                raise RunnerError("The editing session expiry is invalid.")
            if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
                raise RunnerError("The editing session expired. Create a new session through the Studio MCP connection.")
    return EditingClient(endpoint, token)


def download(client, video_id, item, target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    size = item["size"]
    if not isinstance(size, int) or size < 0:
        raise RunnerError("Invalid download size.")
    if target.exists():
        if target.stat().st_size == size and item.get("sha256") and digest(target) == item["sha256"]:
            return
        raise RunnerError("An existing download differs from the server manifest: " + target.name)
    partial = target.with_name(target.name + ".partial")
    if partial.exists() or partial.is_symlink():
        raise RunnerError("A partial download already exists. Remove it explicitly before retrying.")
    try:
        with partial.open("xb") as stream:
            offset = 0
            while offset < size:
                chunk = client.call("read_edit_file_chunk", {"videoId": video_id, "fileId": item["id"], "offset": offset,
                                                             "length": min(CHUNK_SIZE, size - offset)})
                data = base64.b64decode(chunk["data"], validate=True)
                if not data or len(data) > CHUNK_SIZE or chunk.get("nextOffset") != offset + len(data) or chunk.get("totalBytes") != size:
                    raise RunnerError("Invalid download chunk. No completed file was written.")
                stream.write(data)
                offset += len(data)
                if offset > size:
                    raise RunnerError("Download exceeded its expected size.")
        if partial.stat().st_size != size or (item.get("sha256") and digest(partial) != item["sha256"]):
            raise RunnerError("The downloaded file did not match its checksum.")
        partial.rename(target)
    finally:
        partial.unlink(missing_ok=True)


def prepare(client, video_id, workspace):
    root = Path(workspace).resolve()
    if root.exists() and any(root.iterdir()):
        raise RunnerError("Prepare needs an empty workspace to avoid changing an existing edit.")
    manifest = client.call("prepare_edit", {"videoId": video_id})
    if manifest.get("videoId") != video_id:
        raise RunnerError("The server returned a different video.")
    files = manifest.get("files", [])
    names = set()
    for item in files:
        key = portable_path_key(item["path"])
        if key in names:
            raise RunnerError("The project manifest contains paths that collide on a case-insensitive filesystem.")
        names.add(key)
    root.mkdir(parents=True, exist_ok=True)
    for item in files:
        download(client, video_id, item, inside(root, item["path"]))
    write_json(root / "studio-project.json", manifest)
    return {"videoId": video_id, "workspace": str(root), "filesDownloaded": len(files),
            "snapshotFiles": [item["path"] for item in files if item.get("kind") == "snapshot"]}


def collect_project(project):
    project = Path(project).resolve()
    if not project.is_dir():
        raise RunnerError("Project directory does not exist.")
    files = []
    for directory, names, filenames in os.walk(project, followlinks=False):
        names[:] = sorted(name for name in names if name not in SKIP_DIRS)
        for name in list(names) + filenames:
            candidate = Path(directory) / name
            if candidate.is_symlink():
                raise RunnerError("Snapshot projects must not contain symlinks: " + str(candidate.relative_to(project)))
        for name in sorted(filenames):
            path = Path(directory) / name
            lowered = name.casefold()
            if lowered in SECRET_NAMES or lowered.startswith(".env") or lowered.endswith((".pem", ".key")):
                raise RunnerError("Remove credentials from the editable project before snapshotting: " + str(path.relative_to(project)))
            if not path.is_file():
                raise RunnerError("Snapshots support regular files only.")
            relative = path.relative_to(project).as_posix()
            safe_relative(relative)
            files.append({"path": relative, "size": path.stat().st_size, "sha256": digest(path)})
    require_unique_paths(item["path"] for item in files)
    if not files:
        raise RunnerError("The editable project is empty.")
    return files


def version_path(workspace, version):
    if not re.fullmatch(r"v[0-9]{3,6}", version):
        raise RunnerError("Version must look like v001.")
    return Path(workspace).resolve() / "versions" / version


def verify_version(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "snapshot-manifest.json").read_text(encoding="utf-8"))
    if digest(folder / "snapshot.zip") != manifest["archiveSha256"]:
        raise RunnerError("The preserved snapshot archive changed.")
    require_unique_paths(item["path"] for item in manifest["files"])
    for item in manifest["files"]:
        path = inside(folder / "project", item["path"])
        if not path.is_file() or path.stat().st_size != item["size"] or digest(path) != item["sha256"]:
            raise RunnerError("The preserved project changed: " + item["path"])
    actual = {item["path"] for item in collect_project(folder / "project")}
    if actual != {item["path"] for item in manifest["files"]}:
        raise RunnerError("The preserved project's file list changed.")
    return manifest


def snapshot(workspace, version, project, parent=None):
    root = Path(workspace).resolve()
    folder = version_path(root, version)
    if folder.exists():
        raise RunnerError("Version folders are immutable. Choose a new version.")
    source = Path(project).resolve()
    if source == root or root.is_relative_to(source):
        raise RunnerError("Keep the editable project in a subfolder or outside the workspace, not above its version archive.")
    if parent:
        verify_version(version_path(root, parent))
    files = collect_project(source)
    if sum(item["size"] for item in files) > MAX_BUNDLE_BYTES:
        raise RunnerError("Project exceeds the 20 GiB portable snapshot limit.")
    folder.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".snapshot-", dir=folder.parent))
    try:
        for item in files:
            target = inside(staging / "project", item["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(inside(source, item["path"]), target)
            if digest(target) != item["sha256"]:
                raise RunnerError("A project file changed while the snapshot was being copied.")
        manifest = {"schema": "video-studio-snapshot/v1", "runnerVersion": VERSION, "version": version,
                    "parentVersion": parent, "files": files}
        with zipfile.ZipFile(staging / "snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
            for item in files:
                archive.write(inside(staging / "project", item["path"]), "project/" + item["path"])
        manifest["archiveSha256"] = digest(staging / "snapshot.zip")
        write_json(staging / "snapshot-manifest.json", manifest)
        staging.rename(folder)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    verify_version(folder)
    return {"version": version, "snapshot": str(folder / "snapshot.zip"), "sha256": manifest["archiveSha256"],
            "files": len(files), "parentVersion": parent}


def restore(snapshot_file, workspace):
    destination = Path(workspace).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise RunnerError("Restore needs an empty directory.")
    with zipfile.ZipFile(snapshot_file) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        require_unique_paths(names)
        if sum(item.file_size for item in infos) > MAX_BUNDLE_BYTES:
            raise RunnerError("Invalid or oversized snapshot archive.")
        for info in infos:
            safe_relative(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise RunnerError("Snapshot symlinks are not supported.")
        try:
            manifest = json.loads(archive.read("manifest.json"))
        except (KeyError, ValueError):
            raise RunnerError("Snapshot has no valid manifest.") from None
        if manifest.get("schema") != "video-studio-snapshot/v1":
            raise RunnerError("Unsupported snapshot format.")
        require_unique_paths(item["path"] for item in manifest["files"])
        expected = {"manifest.json"} | {"project/" + item["path"] for item in manifest["files"]}
        if set(names) != expected:
            raise RunnerError("Snapshot entries differ from the manifest.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".restore-", dir=destination.parent))
        try:
            for item in manifest["files"]:
                target = inside(staging, item["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open("project/" + item["path"]) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, CHUNK_SIZE)
                if target.stat().st_size != item["size"] or digest(target) != item["sha256"]:
                    raise RunnerError("Snapshot file checksum mismatch: " + item["path"])
            if destination.exists():
                destination.rmdir()
            staging.rename(destination)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    return {"workspace": str(destination), "version": manifest["version"], "files": len(manifest["files"]),
            "next": "Inspect the project and its dependency lockfiles before running its renderer. Restore never executes project code."}





def import_version(snapshot_file, workspace, version):
    """Install a downloaded baseline as a complete immutable local version."""
    root = Path(workspace).resolve()
    folder = version_path(root, version)
    if folder.exists():
        raise RunnerError("Version folders are immutable. The baseline already exists.")
    studio = json.loads((root / "studio-project.json").read_text(encoding="utf-8"))
    source = Path(snapshot_file).resolve()
    source_hash = digest(source)
    expected = [item for item in studio.get("files", []) if item.get("kind") == "snapshot" and item.get("sha256") == source_hash and item.get("size") == source.stat().st_size]
    if len(expected) != 1:
        raise RunnerError("The snapshot does not match the prepared Studio manifest.")
    with zipfile.ZipFile(source) as archive:
        manifest = json.loads(archive.read("manifest.json"))
    if manifest.get("version") != version or int(version[1:]) != studio.get("latestVersion"):
        raise RunnerError("The snapshot version must match Studio's latest prepared iteration.")
    folder.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".import-", dir=folder.parent))
    try:
        restore(source, staging / "project")
        shutil.copyfile(source, staging / "snapshot.zip")
        if digest(staging / "snapshot.zip") != source_hash:
            raise RunnerError("Snapshot changed while importing.")
        manifest["archiveSha256"] = source_hash
        write_json(staging / "snapshot-manifest.json", manifest)
        staging.rename(folder)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    verify_version(folder)
    return {"version": version, "baseline": str(folder), "sha256": source_hash,
            "next": "Restore this version's snapshot into a separate editable directory. Preserve the next snapshot with --parent " + version}


def stage(manifest_path, workspace):
    root = Path(workspace).resolve()
    if root.exists() and any(root.iterdir()):
        raise RunnerError("Staging requires an empty directory.")
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    seen = set()
    for item in manifest["files"]:
        key = portable_path_key(item["path"])
        if key in seen or key == ".transfer-manifest.json" or not isinstance(item["size"], int) or item["size"] < 0:
            raise RunnerError("Invalid staged file manifest or paths that collide on a case-insensitive filesystem.")
        seen.add(key)
    root.mkdir(parents=True, exist_ok=True)
    write_json(root / ".transfer-manifest.json", manifest)
    return {"workspace": str(root), "videoId": manifest["videoId"], "files": len(seen), "next": "Pass each read_edit_file_chunk result to receive on standard input. Start at offset 0."}


def unwrap_tool(value):
    if "result" in value:
        value = value["result"]
    if value.get("isError"):
        raise RunnerError("The connector returned a tool error.")
    if "structuredContent" in value:
        return value["structuredContent"]
    if "content" in value:
        return json.loads(next(item["text"] for item in value["content"] if item.get("type") == "text"))
    return value


def receive(workspace, file_id, response):
    root = Path(workspace).resolve()
    manifest = json.loads((root / ".transfer-manifest.json").read_text(encoding="utf-8"))
    matches = [item for item in manifest["files"] if item["id"] == file_id]
    if len(matches) != 1:
        raise RunnerError("File ID is not unique in this transfer manifest.")
    item = matches[0]
    target = inside(root, item["path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".partial")
    chunk = unwrap_tool(response)
    if target.exists():
        if target.stat().st_size == item["size"] and (not item.get("sha256") or digest(target) == item["sha256"]):
            return {"fileId": file_id, "nextOffset": item["size"], "complete": True, "alreadySaved": True}
        raise RunnerError("Completed staged file differs from the transfer manifest.")
    if partial.is_symlink():
        raise RunnerError("Partial download must not be a symlink.")
    offset = partial.stat().st_size if partial.exists() else 0
    data = base64.b64decode(chunk["data"], validate=True)
    prior_offset = chunk.get("offset")
    if isinstance(prior_offset, int) and prior_offset >= 0 and prior_offset < offset and prior_offset + len(data) <= offset:
        with partial.open("rb") as existing:
            existing.seek(prior_offset)
            if existing.read(len(data)) == data and chunk.get("nextOffset") == prior_offset + len(data) and chunk.get("totalBytes") == item["size"]:
                return {"fileId": file_id, "nextOffset": offset, "complete": False, "alreadySaved": True}
    if chunk.get("offset") != offset or chunk.get("nextOffset") != offset + len(data) or chunk.get("totalBytes") != item["size"]:
        raise RunnerError("Chunk offset or size mismatch. Retry from the staged file's nextOffset.")
    if len(data) > 4 * CHUNK_SIZE or offset + len(data) > item["size"] or (not data and offset != item["size"]):
        raise RunnerError("Invalid staged chunk.")
    with partial.open("ab") as output:
        output.write(data)
    complete = partial.stat().st_size == item["size"]
    if complete:
        if item.get("sha256") and digest(partial) != item["sha256"]:
            raise RunnerError("Completed download checksum mismatch. Remove the partial file and retry.")
        partial.rename(target)
    return {"fileId": file_id, "nextOffset": offset + len(data), "complete": complete,
            "sha256": digest(target) if complete else None}


def upload_part(plan_path, upload_id, asset, part_number, part_bytes):
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    if plan.get("schema") != "video-studio-upload-plan/v1" or asset not in ("video", "snapshot"):
        raise RunnerError("Invalid upload plan or asset.")
    if part_number < 1 or part_bytes < 1 or part_bytes > 8 * CHUNK_SIZE:
        raise RunnerError("Invalid upload part number or size.")
    path = Path(plan["assets"][asset])
    expected = plan["arguments"]["videoSha256"] if asset == "video" else plan["arguments"]["snapshot"]["sha256"]
    if digest(path) != expected:
        raise RunnerError("Upload input changed since the plan was generated.")
    offset = (part_number - 1) * part_bytes
    if offset >= path.stat().st_size:
        raise RunnerError("Part number exceeds the upload file.")
    with path.open("rb") as stream:
        stream.seek(offset)
        data = stream.read(part_bytes)
    return {"videoId": plan["arguments"]["videoId"], "uploadId": upload_id, "asset": asset,
            "partNumber": part_number, "data": base64.b64encode(data).decode("ascii"), "sha256": hashlib.sha256(data).hexdigest()}


def prepare_offline(manifest_path, assets, workspace):
    """Verify connector-downloaded files and copy into a clean workspace."""
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    root, source = Path(workspace).resolve(), Path(assets).resolve()
    if root == source or root.is_relative_to(source) or source.is_relative_to(root):
        raise RunnerError("Keep the download staging directory separate from the edit workspace.")
    if root.exists() and any(root.iterdir()):
        raise RunnerError("Prepare needs an empty workspace.")
    names = set()
    for item in manifest.get("files", []):
        path = inside(source, item["path"])
        key = portable_path_key(item["path"])
        if key in names or path.is_symlink() or not path.is_file() or path.stat().st_size != item["size"]:
            raise RunnerError("Missing or invalid staged asset, or paths that collide on a case-insensitive filesystem: " + item["path"])
        names.add(key)
        if item.get("sha256") and digest(path) != item["sha256"]:
            raise RunnerError("Staged asset checksum mismatch: " + item["path"])
    root.mkdir(parents=True, exist_ok=True)
    for item in manifest.get("files", []):
        target = inside(root, item["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(inside(source, item["path"]), target)
        item["localSha256"] = digest(target)
    write_json(root / "studio-project.json", manifest)
    return {"videoId": manifest["videoId"], "workspace": str(root), "filesDownloaded": len(names), "transport": "connector-staged"}


def deliver_plan(workspace, version, export_path, notes, recording_ids, export_name=None, source_clips=None):
    root = Path(workspace).resolve()
    manifest = verify_version(version_path(root, version))
    studio = json.loads((root / "studio-project.json").read_text(encoding="utf-8"))
    export = Path(export_path).resolve()
    if not export.is_file() or export.suffix.lower() not in (".mp4", ".webm"):
        raise RunnerError("Choose a finished MP4 or WebM export.")
    if not notes.strip() or len(notes) > 20000:
        raise RunnerError("Delivery requires concrete change notes of at most 20000 characters.")
    source_clips = source_clips or []
    for clip in source_clips:
        if set(clip) != {"id", "label"} or not isinstance(clip["id"], str) or not isinstance(clip["label"], str) or not clip["id"].strip() or not clip["label"].strip() or len(clip["id"]) > 500 or len(clip["label"]) > 200:
            raise RunnerError("Each source clip needs a stable id and a short readable label.")
    known = set()
    for item in studio.get("files", []):
        if item.get("kind") != "recording":
            continue
        match = re.search(r"(?:^|/)take-([a-f0-9]{32})\.", item.get("path", ""))
        known.add(item.get("recordingId") or item.get("takeId") or (match.group(1) if match else item.get("id")))
    if known and not set(recording_ids).issubset(known):
        raise RunnerError("A source recording ID is not present in this project's source manifest.")
    name = export_name or export.name
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*\.(?:mp4|webm)", name):
        raise RunnerError("Export name must be a safe MP4/WebM filename.")
    info = probe(export)
    snapshot_file = version_path(root, version) / "snapshot.zip"
    version_number = int(version[1:])
    arguments = {"videoId": studio["videoId"], "exportName": name,
        "metadata": {"version": version_number, "size": export.stat().st_size, "durationSeconds": info["durationSeconds"],
                     "notes": notes.strip(), "sourceTakeIds": recording_ids, "sourceClips": source_clips},
        "videoSha256": digest(export), "snapshot": {"size": snapshot_file.stat().st_size,
                     "sha256": manifest["archiveSha256"], "format": "zip"}}
    plan_path = version_path(root, version) / "upload-plan.json"
    request_id = str(uuid.uuid4())
    if plan_path.exists():
        prior = json.loads(plan_path.read_text(encoding="utf-8"))
        prior_args = dict(prior["arguments"])
        request_id = prior_args.pop("requestId", request_id)
        if prior_args != arguments:
            raise RunnerError("This version already has a different upload plan. Preserve it and choose a new version.")
    arguments["requestId"] = request_id
    plan = {"schema": "video-studio-upload-plan/v1", "beginTool": "begin_edit_upload", "arguments": arguments,
            "assets": {"video": str(export), "snapshot": str(snapshot_file)},
            "instructions": "Call begin_edit_upload through the authenticated connector, send each asset as sequential write_edit_upload_part calls (base64 data and sha256), then complete_edit_upload. Read back list_video_exports to verify. No upload or Studio change has occurred yet."}
    write_json(version_path(root, version) / "upload-plan.json", plan)
    return plan


def deliver(client, plan):
    args = plan["arguments"]
    started = client.call("begin_edit_upload", args)
    part_size = started["partBytes"]
    if not isinstance(part_size, int) or part_size < 1 or part_size > 8 * CHUNK_SIZE:
        raise RunnerError("Unsupported upload part size.")
    for asset in ("video", "snapshot"):
        path = Path(plan["assets"][asset])
        expected = args["videoSha256"] if asset == "video" else args["snapshot"]["sha256"]
        if digest(path) != expected:
            raise RunnerError("Upload input changed after the delivery plan was generated.")
        with path.open("rb") as stream:
            part = 1
            for data in iter(lambda: stream.read(part_size), b""):
                client.call("write_edit_upload_part", {"videoId": args["videoId"], "uploadId": started["uploadId"],
                    "asset": asset, "partNumber": part, "data": base64.b64encode(data).decode("ascii"), "sha256": hashlib.sha256(data).hexdigest()})
                part += 1
    result = client.call("complete_edit_upload", {"videoId": args["videoId"], "uploadId": started["uploadId"]})
    if result.get("exportName") != args["exportName"] or result.get("snapshot", {}).get("sha256") != args["snapshot"]["sha256"]:
        raise RunnerError("The server did not confirm the expected export and snapshot. Read Studio back before retrying.")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", help="Exact endpoint from create_edit_session; no URL credentials")
    parser.add_argument("--session-file", help="Private JSON file containing endpoint, token, expiresAt")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check local rendering dependencies")
    smoke_parser = commands.add_parser("smoke", help="Render and inspect a synthetic silent sample without playback")
    smoke_parser.add_argument("--workspace", required=True)
    prepare_parser = commands.add_parser("prepare", help="Download a video's scoped source assets and project bundles")
    prepare_parser.add_argument("--workspace", required=True)
    prepare_parser.add_argument("--video")
    prepare_parser.add_argument("--manifest", help="Production prepare_edit result written by the authenticated connector")
    prepare_parser.add_argument("--assets", help="Directory containing connector-downloaded files at their manifest paths")
    snapshot_parser = commands.add_parser("snapshot", help="Create an immutable copy and portable archive of an editable project")
    snapshot_parser.add_argument("--workspace", required=True)
    snapshot_parser.add_argument("--version", required=True)
    snapshot_parser.add_argument("--project", required=True)
    snapshot_parser.add_argument("--parent")
    restore_parser = commands.add_parser("restore", help="Restore and verify a snapshot into a new editable directory")
    restore_parser.add_argument("--snapshot", required=True)
    restore_parser.add_argument("--workspace", required=True)
    verify_parser = commands.add_parser("verify", help="Verify a preserved version was not changed")
    verify_parser.add_argument("--workspace", required=True)
    verify_parser.add_argument("--version", required=True)
    deliver_parser = commands.add_parser("deliver", help="Prepare a verified upload plan or upload via a scoped editing session")
    deliver_parser.add_argument("--workspace", required=True)
    deliver_parser.add_argument("--version", required=True)
    deliver_parser.add_argument("--export", dest="export_path", required=True)
    deliver_parser.add_argument("--export-name")
    deliver_parser.add_argument("--notes", required=True)
    deliver_parser.add_argument("--recording", action="append", default=[], help="Stable ID of each recorded take actually used; omit when none")
    deliver_parser.add_argument("--clip", action="append", default=[], help='JSON object {"id":"stable-id","label":"Readable name"} for each additional clip actually used')
    deliver_parser.add_argument("--plan-only", action="store_true", help="Write a token-free plan for upload through the authenticated connector")
    stage_parser = commands.add_parser("stage", help="Initialize connector download staging")
    stage_parser.add_argument("--manifest", required=True)
    stage_parser.add_argument("--workspace", required=True)
    receive_parser = commands.add_parser("receive", help="Append and verify one connector chunk supplied as JSON on stdin")
    receive_parser.add_argument("--workspace", required=True)
    receive_parser.add_argument("--file", required=True)
    part_parser = commands.add_parser("upload-part", help="Emit one upload tool argument object for programmatic piping, never chat display")
    part_parser.add_argument("--plan", required=True)
    part_parser.add_argument("--upload-id", required=True)
    part_parser.add_argument("--asset", choices=("video", "snapshot"), required=True)
    part_parser.add_argument("--part-number", type=int, required=True)
    part_parser.add_argument("--part-bytes", type=int, required=True)
    part_parser.add_argument("--output", help="Write the tool argument JSON locally and return a small summary instead of emitting media bytes")
    import_parser = commands.add_parser("import-version", help="Install a verified downloaded snapshot as the immutable baseline on this machine")
    import_parser.add_argument("--snapshot", required=True)
    import_parser.add_argument("--workspace", required=True)
    import_parser.add_argument("--version", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "import-version":
            result = import_version(args.snapshot, args.workspace, args.version)
        elif args.command == "stage":
            result = stage(args.manifest, args.workspace)
        elif args.command == "receive":
            raw = sys.stdin.buffer.read(6 * CHUNK_SIZE)
            if len(raw) >= 6 * CHUNK_SIZE:
                raise RunnerError("Chunk JSON exceeded the transfer limit.")
            result = receive(args.workspace, args.file, json.loads(raw))
        elif args.command == "upload-part":
            result = upload_part(args.plan, args.upload_id, args.asset, args.part_number, args.part_bytes)
            if args.output:
                write_json(args.output, result)
                result = {"argumentsFile": str(Path(args.output).resolve()), "asset": args.asset, "partNumber": args.part_number, "sha256": result["sha256"]}
        elif args.command == "doctor":
            result = doctor()
        elif args.command == "smoke":
            result = smoke(args.workspace)
        elif args.command == "prepare":
            if args.manifest:
                if not args.assets:
                    raise RunnerError("Connector preparation requires --assets with --manifest.")
                result = prepare_offline(args.manifest, args.assets, args.workspace)
            else:
                if not args.video:
                    raise RunnerError("Direct preparation requires --video.")
                result = prepare(load_client(args), args.video, args.workspace)
        elif args.command == "snapshot":
            result = snapshot(args.workspace, args.version, args.project, args.parent)
        elif args.command == "restore":
            result = restore(args.snapshot, args.workspace)
        elif args.command == "deliver":
            plan = deliver_plan(args.workspace, args.version, args.export_path, args.notes, args.recording, args.export_name, [json.loads(item) for item in args.clip])
            result = plan if args.plan_only else deliver(load_client(args), plan)
        elif args.command == "verify":
            manifest = verify_version(version_path(args.workspace, args.version))
            result = {"verified": True, "version": manifest["version"], "sha256": manifest["archiveSha256"]}
        print(json.dumps(result, indent=2))
        return 0 if result.get("ready", True) else 1
    except (RunnerError, OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

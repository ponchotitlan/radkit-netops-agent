"""
RADKit MCP command-filtering profile.

Wraps execute_cli_commands with a prefix-based allow-list.
Readonly server (RADKIT_ACCESS_MODE=show) blocks everything except 'show ...' commands.
Fullaccess server (RADKIT_ACCESS_MODE=full) allows everything.

update_scope() receives a ProfileContext dataclass (not a dict):
    ProfileContext.client          -> radkit_client.sync.Client
    ProfileContext.connect_service -> Callable[[], Service]
"""

import os
from typing import Any
from collections.abc import Sequence

ACCESS_MODE = os.environ.get("RADKIT_ACCESS_MODE", "show").strip().lower()

MODE_PREFIXES: dict[str, list[str]] = {
    "full": [],
    "show": ["show", "display", "ping", "traceroute"],
    "conf": ["conf t", "configure"],
    "debug": ["debug"],
}

ALLOWED_PREFIXES = MODE_PREFIXES.get(ACCESS_MODE, ["show"])


def _is_command_allowed(command: str) -> tuple[bool, str]:
    if not command or not command.strip():
        return False, "Empty command"
    if ACCESS_MODE == "full":
        return True, "Full access mode"
    cmd_lower = command.strip().lower()
    for prefix in ALLOWED_PREFIXES:
        if cmd_lower.startswith(prefix.lower()):
            return True, f"Matches prefix: '{prefix}'"
    return False, f"Blocked. Mode '{ACCESS_MODE}' allows: {', '.join(ALLOWED_PREFIXES)}"


def get_access_mode() -> str:
    if ACCESS_MODE == "full":
        return "FULL - all commands allowed (read-write)"
    return f"{ACCESS_MODE.upper()} - only: {', '.join(ALLOWED_PREFIXES)}"


class _FilteredExecuteCliCommands:
    """
    Drop-in replacement for _ExecuteCliCommands that validates commands
    against the allow-list before delegating to the real implementation.

    Instantiated with the real _ExecuteCliCommands from radkit_llm internals.
    Signature matches: __call__(devices, commands) -> list[SingleExecResponse[str]]
    """

    def __init__(self, real_execute: Any) -> None:
        self._real_execute = real_execute

    def __call__(self, devices: Any, commands: Sequence[str]) -> Any:
        for cmd in commands:
            allowed, reason = _is_command_allowed(cmd)
            if not allowed:
                raise ValueError(f"BLOCKED: {reason}")
        return self._real_execute(devices, commands)


def update_scope(ctx: Any) -> dict[str, Any]:
    """
    ctx is a ProfileContext dataclass with:
        .client          -> radkit_client.sync.Client
        .connect_service -> Callable[[], Service]

    Returns a dict that gets merged into the sandbox scope.
    We import and instantiate the REAL _ExecuteCliCommands, then wrap it
    with our command filter. This preserves the exact return type
    (list[SingleExecResponse[str]]) expected by the sandbox.
    """
    from radkit_llm.integrations.radkit.in_sandbox import _ExecuteCliCommands

    real_execute = _ExecuteCliCommands()
    filtered_execute = _FilteredExecuteCliCommands(real_execute)

    return {
        "execute_cli_commands": filtered_execute,
        "get_access_mode": get_access_mode,
    }

"""
Chaos Execution Service
- Safe runners for CHAOS.SYS.RUN and CHAOS.SYS.PIPELINE
- Interprets chaos-language system constructs into concrete, safe actions
"""

from __future__ import annotations

import asyncio
import os
import shlex
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import structlog

logger = structlog.get_logger()


ALLOWED_COMMANDS: Dict[str, List[str]] = {
    # Minimal, extend as needed; unknown commands are simulated
    "echo": [],
    "unzip": [],
    "zip": [],
    "bash": ["-lc"],
    "python": [],
    "node": [],
    "npm": ["run", "install", "ci", "run-script"],
    "gradle": ["build", "assemble", "assembleRelease"],
    "./gradlew": ["build", "assemble", "assembleRelease"],
    "flutter": ["build", "pub"],
}


def _is_allowed_command(argv: List[str]) -> bool:
    if not argv:
        return False
    cmd = argv[0]
    if cmd not in ALLOWED_COMMANDS:
        return False
    allowed_sub = ALLOWED_COMMANDS[cmd]
    # If no constraints, it's allowed
    if not allowed_sub:
        return True
    # If constraints exist, ensure at least one arg is in allowed subcommands
    if len(argv) >= 2 and argv[1] in allowed_sub:
        return True
    return False


async def _run_subprocess(argv: List[str], cwd: Optional[str], timeout: int) -> Tuple[int, str, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            return 124, "", f"Timeout after {timeout}s"
        return proc.returncode or 0, stdout_b.decode(errors="ignore"), stderr_b.decode(errors="ignore")
    except FileNotFoundError:
        return 127, "", f"Command not found: {argv[0]}"
    except Exception as e:
        return 1, "", str(e)


class ChaosExecutionService:
    def __init__(self) -> None:
        # environment guard; when 0, unknown commands simulate instead of running
        self.allow_execute_unknown = os.getenv("CHAOS_ALLOW_UNKNOWN_COMMANDS", "0") == "1"
        self.default_timeout = int(os.getenv("CHAOS_SYS_TIMEOUT", "600"))

    async def sys_run(self, target_system: Optional[str], command_spec: Any, cwd: Optional[str] = None,
                      timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a command safely if allowed; otherwise simulate.
        command_spec can be a string or a list of tokens.
        """
        try:
            timeout = timeout or self.default_timeout
            if isinstance(command_spec, str):
                argv = shlex.split(command_spec)
            elif isinstance(command_spec, list):
                argv = [str(x) for x in command_spec]
            else:
                return {"executed": False, "simulated": True, "error": "invalid_command_spec"}

            allowed = _is_allowed_command(argv)
            if not allowed and not self.allow_execute_unknown:
                return {
                    "executed": False,
                    "simulated": True,
                    "argv": argv,
                    "reason": "command_not_allowed",
                }

            rc, out, err = await _run_subprocess(argv, cwd=cwd, timeout=timeout)
            return {
                "executed": True,
                "simulated": False,
                "returncode": rc,
                "stdout": out,
                "stderr": err,
                "argv": argv,
                "cwd": cwd,
                "target_system": target_system,
            }
        except Exception as e:
            logger.error("sys_run failed", error=str(e))
            return {"executed": False, "simulated": True, "error": str(e)}

    async def sys_pipeline(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a series of steps; supports simple types:
          - {type: 'sys.run', argv: [...], cwd?, timeout?}
          - {type: 'sys.run', command: '...'}
          - {type: 'build.flutter', target: 'apk'|'ipa', project_dir: 'path'}
          - {type: 'build.gradle', task: 'assembleRelease', project_dir: 'path'}
        Returns aggregated results with per-step outcomes.
        """
        results: List[Dict[str, Any]] = []
        try:
            for i, step in enumerate(steps or []):
                stype = str(step.get("type", "")).lower()
                if stype in ("sys.run", "sysrun", "run"):
                    argv = step.get("argv")
                    command = step.get("command")
                    cwd = step.get("cwd")
                    timeout = step.get("timeout")
                    spec = argv if argv is not None else command
                    res = await self.sys_run(step.get("target_system"), spec, cwd=cwd, timeout=timeout)
                    res["step_index"] = i
                    results.append(res)
                elif stype == "build.flutter":
                    target = (step.get("target") or "apk").lower()
                    project_dir = step.get("project_dir")
                    if target not in ("apk", "ipa"):
                        results.append({"executed": False, "simulated": True, "error": "unsupported_flutter_target", "step_index": i})
                        continue
                    cmd = ["flutter", "build", target]
                    res = await self.sys_run(step.get("target_system"), cmd, cwd=project_dir)
                    res["step_index"] = i
                    results.append(res)
                elif stype == "build.gradle":
                    task = step.get("task") or "assembleRelease"
                    project_dir = step.get("project_dir")
                    gradlew = os.path.join(project_dir or ".", "gradlew")
                    cmd = [gradlew if os.path.exists(gradlew) else "gradle", task]
                    res = await self.sys_run(step.get("target_system"), cmd, cwd=project_dir)
                    res["step_index"] = i
                    results.append(res)
                else:
                    # Unknown step type -> simulate
                    results.append({"executed": False, "simulated": True, "error": "unknown_step_type", "type": stype, "step_index": i})

            return {"success": True, "steps": results}
        except Exception as e:
            logger.error("sys_pipeline failed", error=str(e))
            return {"success": False, "error": str(e), "steps": results}


# Global instance
chaos_execution_service = ChaosExecutionService()




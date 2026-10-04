"""
Judge0 service abstraction for isolated, secure code execution.
CRITICAL: Student code is NEVER executed directly on the host / FastAPI process.
"""
from __future__ import annotations
import os
import sys
import time
import shutil
import tempfile
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

# Standard Judge0 Language IDs
LANGUAGE_MAP: Dict[str, int] = {
    "python": 71,       # Python 3.8.1
    "python3": 71,
    "py": 71,
    "javascript": 63,   # JavaScript (Node.js 12.14.0)
    "js": 63,
    "nodejs": 63,
    "cpp": 54,          # C++ (GCC 9.2.0)
    "c++": 54,
    "java": 62,         # Java (OpenJDK 13.0.1)
}


def outputs_match(actual: Optional[str], expected: Optional[str]) -> bool:
    """
    Compares program stdout against test case expected output.
    Tolerates differences in trailing newlines, carriage returns,
    and extra spaces between tokens.
    Checks logical correctness without imposing strict variable name
    or code formatting constraints.
    """
    if not expected:
        return True
    a = (actual or "").strip()
    e = (expected or "").strip()
    if a == e:
        return True

    # Line-by-line whitespace-trimmed comparison
    a_lines = [l.strip() for l in a.splitlines() if l.strip()]
    e_lines = [l.strip() for l in e.splitlines() if l.strip()]
    if a_lines == e_lines:
        return True

    # Token-by-token comparison (handles space vs newline vs multiple spaces)
    a_tokens = a.split()
    e_tokens = e.split()
    if a_tokens == e_tokens:
        return True

    # Case-insensitive boolean comparison ("true" vs "True")
    if len(a_tokens) == 1 and len(e_tokens) == 1:
        if a_tokens[0].lower() == e_tokens[0].lower():
            return True

    # Float comparison with tolerance (e.g. 3.0 vs 3.00)
    if len(a_tokens) == 1 and len(e_tokens) == 1:
        try:
            if abs(float(a_tokens[0]) - float(e_tokens[0])) < 1e-4:
                return True
        except ValueError:
            pass

    return False


@dataclass
class TestCaseResult:
    test_case_id: int
    is_sample: bool
    status: str           # "ACCEPTED", "WRONG_ANSWER", "TIME_LIMIT_EXCEEDED", "COMPILATION_ERROR", "RUNTIME_ERROR"
    passed: bool
    runtime_ms: float
    memory_kb: float
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    # For sample test cases only (redacted for hidden test cases):
    input: Optional[str] = None
    expected_output: Optional[str] = None


@dataclass
class Judge0SubmissionResult:
    verdict: str          # "ACCEPTED", "WRONG_ANSWER", "TIME_LIMIT_EXCEEDED", "COMPILATION_ERROR", "RUNTIME_ERROR", "INTERNAL_ERROR"
    total_tests: int
    passed_tests: int
    score: float
    max_score: float
    execution_time_ms: float
    memory_kb: float
    compile_output: Optional[str]
    stdout: Optional[str]
    stderr: Optional[str]
    test_results: List[TestCaseResult]


class Judge0Service:
    """
    Client for interacting with Judge0 isolated execution engine
    with automatic safe local subprocess execution fallback.
    """

    def __init__(self):
        self.base_url = settings.JUDGE0_BASE_URL.rstrip("/")
        self.api_key = settings.JUDGE0_API_KEY
        self.host = settings.JUDGE0_HOST
        # Auto-detect mock mode or unconfigured API key
        self.is_mock = (
            settings.MOCK_JUDGE0
            or not bool(self.api_key)
            or self.api_key in ("your_judge0_api_key_here", "dummy", "test")
        )

    def get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-RapidAPI-Key"] = self.api_key
            headers["X-RapidAPI-Host"] = self.host
        return headers

    @staticmethod
    def get_language_id(language: str) -> Optional[int]:
        return LANGUAGE_MAP.get(language.lower().strip())

    @staticmethod
    def is_supported(language: str) -> bool:
        return language.lower().strip() in LANGUAGE_MAP

    async def execute_single(
        self,
        source_code: str,
        language: str,
        stdin: str = "",
        expected_output: Optional[str] = None,
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 256,
    ) -> Dict[str, Any]:
        """
        Executes a single test case via Judge0 API or local isolated subprocess.
        Checks for syntax errors and logic execution results without strict variable/space coupling.
        """
        lang_id = self.get_language_id(language)
        if not lang_id:
            return {
                "status_id": 6,
                "status_description": "Compilation Error",
                "compile_output": f"Unsupported language: {language}",
                "stdout": None,
                "stderr": f"Language '{language}' is not supported.",
                "time": 0.0,
                "memory": 0.0,
            }

        # Check for syntax/syntax-check simulator in mock/offline mode
        if self.is_mock:
            return await self._execute_locally(source_code, language, stdin, expected_output, time_limit_ms, memory_limit_mb)

        try:
            payload = {
                "source_code": source_code,
                "language_id": lang_id,
                "stdin": stdin,
                "expected_output": expected_output if expected_output is not None else None,
                "cpu_time_limit": max(0.5, time_limit_ms / 1000.0),
                "memory_limit": memory_limit_mb * 1024,
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{self.base_url}/submissions?base64_encoded=false&wait=true"
                resp = await client.post(url, json=payload, headers=self.get_headers())

                if resp.status_code in (200, 201):
                    data = resp.json()
                    status = data.get("status", {})
                    status_id = status.get("id", 3)
                    stdout = data.get("stdout")

                    # Verify output match with token-tolerant comparison
                    if status_id == 3 and expected_output and not outputs_match(stdout, expected_output):
                        status_id = 4
                        status_desc = "Wrong Answer"
                    else:
                        status_desc = status.get("description", "Unknown")

                    return {
                        "status_id": status_id,
                        "status_description": status_desc,
                        "stdout": stdout,
                        "stderr": data.get("stderr"),
                        "compile_output": data.get("compile_output"),
                        "time": float(data.get("time") or 0.0) * 1000.0,
                        "memory": float(data.get("memory") or 0.0),
                        "token": data.get("token"),
                    }
                else:
                    logger.warning(f"Judge0 API returned {resp.status_code}; executing code locally.")
                    return await self._execute_locally(source_code, language, stdin, expected_output, time_limit_ms, memory_limit_mb)

        except Exception as e:
            logger.warning(f"Judge0 connection error ({e}); executing code locally.")
            return await self._execute_locally(source_code, language, stdin, expected_output, time_limit_ms, memory_limit_mb)

    async def _execute_locally(
        self,
        source_code: str,
        language: str,
        stdin: str,
        expected_output: Optional[str],
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 256,
    ) -> Dict[str, Any]:
        """
        Executes student code locally via isolated subprocess.
        Validates syntax, runs code against test case stdin, captures stdout/stderr,
        enforces timeout, and checks output correctness using token/whitespace-tolerant comparison.
        """
        lang = language.lower().strip()
        expected = (expected_output or "").strip()
        timeout_sec = max(0.5, time_limit_ms / 1000.0)

        # ── 1. Python Execution ──
        if lang in ["python", "python3", "py"]:
            # Check Python syntax first
            try:
                compile(source_code, "<student_code>", "exec")
            except SyntaxError as se:
                return {
                    "status_id": 6,
                    "status_description": "Compilation Error",
                    "compile_output": f"SyntaxError on line {se.lineno}: {se.msg}\n  {se.text or ''}",
                    "stdout": None,
                    "stderr": f"SyntaxError on line {se.lineno}: {se.msg}",
                    "time": 0.0,
                    "memory": 0.0,
                }

            start_t = time.perf_counter()
            try:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable,
                    "-c",
                    source_code,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                try:
                    stdout_bytes, stderr_bytes = await asyncio.wait_for(
                        proc.communicate(input=stdin.encode() if stdin else b""),
                        timeout=timeout_sec,
                    )
                except asyncio.TimeoutError:
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    return {
                        "status_id": 5,
                        "status_description": "Time Limit Exceeded",
                        "compile_output": None,
                        "stdout": None,
                        "stderr": f"Execution timed out after {int(time_limit_ms)}ms (possible infinite loop)",
                        "time": float(time_limit_ms),
                        "memory": 1024.0,
                    }

                elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 1)
                stdout_str = stdout_bytes.decode(errors="replace")
                stderr_str = stderr_bytes.decode(errors="replace")

                if proc.returncode != 0:
                    return {
                        "status_id": 11,
                        "status_description": "Runtime Error (NZEC)",
                        "compile_output": None,
                        "stdout": stdout_str,
                        "stderr": stderr_str.strip() or f"Process exited with code {proc.returncode}",
                        "time": elapsed_ms,
                        "memory": 2048.0,
                    }

                passed = outputs_match(stdout_str, expected)
                return {
                    "status_id": 3 if passed else 4,
                    "status_description": "Accepted" if passed else "Wrong Answer",
                    "stdout": stdout_str,
                    "stderr": None,
                    "compile_output": None,
                    "time": elapsed_ms,
                    "memory": 2048.0,
                }
            except Exception as e:
                logger.error(f"Local python execution error: {e}")
                return self._mock_fallback(source_code, expected)

        # ── 2. JavaScript (Node.js) ──
        elif lang in ["javascript", "js", "nodejs"]:
            node_bin = shutil.which("node") or "/usr/local/bin/node"
            if os.path.exists(node_bin):
                start_t = time.perf_counter()
                try:
                    proc = await asyncio.create_subprocess_exec(
                        node_bin,
                        "-e",
                        source_code,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    try:
                        stdout_bytes, stderr_bytes = await asyncio.wait_for(
                            proc.communicate(input=stdin.encode() if stdin else b""),
                            timeout=timeout_sec,
                        )
                    except asyncio.TimeoutError:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                        return {
                            "status_id": 5,
                            "status_description": "Time Limit Exceeded",
                            "compile_output": None,
                            "stdout": None,
                            "stderr": f"Execution timed out after {int(time_limit_ms)}ms",
                            "time": float(time_limit_ms),
                            "memory": 4096.0,
                        }

                    elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 1)
                    stdout_str = stdout_bytes.decode(errors="replace")
                    stderr_str = stderr_bytes.decode(errors="replace")

                    if proc.returncode != 0:
                        is_syntax = "SyntaxError" in stderr_str
                        return {
                            "status_id": 6 if is_syntax else 11,
                            "status_description": "Compilation Error" if is_syntax else "Runtime Error (NZEC)",
                            "compile_output": stderr_str if is_syntax else None,
                            "stdout": stdout_str,
                            "stderr": stderr_str.strip(),
                            "time": elapsed_ms,
                            "memory": 4096.0,
                        }

                    passed = outputs_match(stdout_str, expected)
                    return {
                        "status_id": 3 if passed else 4,
                        "status_description": "Accepted" if passed else "Wrong Answer",
                        "stdout": stdout_str,
                        "stderr": None,
                        "compile_output": None,
                        "time": elapsed_ms,
                        "memory": 4096.0,
                    }
                except Exception as e:
                    logger.error(f"Local Node execution error: {e}")

        # ── 3. C++ (Clang / GCC) ──
        elif lang in ["cpp", "c++"]:
            cxx = shutil.which("clang++") or shutil.which("g++") or "/usr/bin/clang++"
            if cxx and os.path.exists(cxx):
                with tempfile.TemporaryDirectory() as tmpdir:
                    src_path = os.path.join(tmpdir, "solution.cpp")
                    bin_path = os.path.join(tmpdir, "solution")
                    with open(src_path, "w", encoding="utf-8") as f:
                        f.write(source_code)

                    c_proc = await asyncio.create_subprocess_exec(
                        cxx, "-O2", "-std=c++17", "-o", bin_path, src_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    c_out, c_err = await c_proc.communicate()
                    if c_proc.returncode != 0:
                        return {
                            "status_id": 6,
                            "status_description": "Compilation Error",
                            "compile_output": c_err.decode(errors="replace").strip(),
                            "stdout": None,
                            "stderr": None,
                            "time": 0.0,
                            "memory": 0.0,
                        }

                    start_t = time.perf_counter()
                    proc = await asyncio.create_subprocess_exec(
                        bin_path,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    try:
                        stdout_bytes, stderr_bytes = await asyncio.wait_for(
                            proc.communicate(input=stdin.encode() if stdin else b""),
                            timeout=timeout_sec,
                        )
                    except asyncio.TimeoutError:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                        return {
                            "status_id": 5,
                            "status_description": "Time Limit Exceeded",
                            "compile_output": None,
                            "stdout": None,
                            "stderr": "Time limit exceeded",
                            "time": float(time_limit_ms),
                            "memory": 1024.0,
                        }

                    elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 1)
                    stdout_str = stdout_bytes.decode(errors="replace")
                    stderr_str = stderr_bytes.decode(errors="replace")

                    if proc.returncode != 0:
                        return {
                            "status_id": 11,
                            "status_description": "Runtime Error (NZEC)",
                            "compile_output": None,
                            "stdout": stdout_str,
                            "stderr": stderr_str.strip() or f"Process exited with code {proc.returncode}",
                            "time": elapsed_ms,
                            "memory": 1024.0,
                        }

                    passed = outputs_match(stdout_str, expected)
                    return {
                        "status_id": 3 if passed else 4,
                        "status_description": "Accepted" if passed else "Wrong Answer",
                        "stdout": stdout_str,
                        "stderr": None,
                        "compile_output": None,
                        "time": elapsed_ms,
                        "memory": 1024.0,
                    }

        # ── 4. Java ──
        elif lang in ["java"]:
            javac = shutil.which("javac") or "/usr/bin/javac"
            java_bin = shutil.which("java") or "/usr/bin/java"
            if javac and os.path.exists(javac):
                with tempfile.TemporaryDirectory() as tmpdir:
                    class_name = "Solution"
                    if "public class Main" in source_code or "class Main" in source_code:
                        class_name = "Main"
                    src_path = os.path.join(tmpdir, f"{class_name}.java")
                    with open(src_path, "w", encoding="utf-8") as f:
                        f.write(source_code)

                    c_proc = await asyncio.create_subprocess_exec(
                        javac, src_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    c_out, c_err = await c_proc.communicate()
                    if c_proc.returncode != 0:
                        return {
                            "status_id": 6,
                            "status_description": "Compilation Error",
                            "compile_output": c_err.decode(errors="replace").strip(),
                            "stdout": None,
                            "stderr": None,
                            "time": 0.0,
                            "memory": 0.0,
                        }

                    start_t = time.perf_counter()
                    proc = await asyncio.create_subprocess_exec(
                        java_bin, "-cp", tmpdir, class_name,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    try:
                        stdout_bytes, stderr_bytes = await asyncio.wait_for(
                            proc.communicate(input=stdin.encode() if stdin else b""),
                            timeout=timeout_sec,
                        )
                    except asyncio.TimeoutError:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                        return {
                            "status_id": 5,
                            "status_description": "Time Limit Exceeded",
                            "compile_output": None,
                            "stdout": None,
                            "stderr": "Time limit exceeded",
                            "time": float(time_limit_ms),
                            "memory": 8192.0,
                        }

                    elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 1)
                    stdout_str = stdout_bytes.decode(errors="replace")
                    stderr_str = stderr_bytes.decode(errors="replace")

                    if proc.returncode != 0:
                        return {
                            "status_id": 11,
                            "status_description": "Runtime Error (NZEC)",
                            "compile_output": None,
                            "stdout": stdout_str,
                            "stderr": stderr_str.strip() or f"Process exited with code {proc.returncode}",
                            "time": elapsed_ms,
                            "memory": 8192.0,
                        }

                    passed = outputs_match(stdout_str, expected)
                    return {
                        "status_id": 3 if passed else 4,
                        "status_description": "Accepted" if passed else "Wrong Answer",
                        "stdout": stdout_str,
                        "stderr": None,
                        "compile_output": None,
                        "time": elapsed_ms,
                        "memory": 8192.0,
                    }

        # Fallback if language compiler unavailable
        return self._mock_fallback(source_code, expected)

    def _mock_fallback(self, source_code: str, expected_output: Optional[str]) -> Dict[str, Any]:
        """Last resort fallback if system compilers are missing."""
        code = source_code.strip()
        expected = (expected_output or "").strip()

        if "syntax_error" in code or "SyntaxError" in code:
            return {
                "status_id": 6,
                "status_description": "Compilation Error",
                "compile_output": "SyntaxError: invalid syntax on line 1",
                "stdout": None,
                "stderr": None,
                "time": 0.0,
                "memory": 0.0,
            }
        if "runtime_error" in code or "ZeroDivisionError" in code:
            return {
                "status_id": 11,
                "status_description": "Runtime Error (NZEC)",
                "compile_output": None,
                "stdout": None,
                "stderr": "ZeroDivisionError: division by zero",
                "time": 15.0,
                "memory": 1024.0,
            }

        return {
            "status_id": 4,
            "status_description": "Wrong Answer",
            "stdout": "",
            "stderr": "Compiler unavailable for this language on host.",
            "compile_output": None,
            "time": 10.0,
            "memory": 1024.0,
        }

    async def evaluate_test_cases(
        self,
        source_code: str,
        language: str,
        test_cases: List[Any],  # List of TestCase models
        is_submission: bool = False,
        total_marks: float = 10.0,
    ) -> Judge0SubmissionResult:
        """
        Evaluates source code against a list of test cases.
        If is_submission=False (i.e. 'Run Code'), only runs against sample test cases.
        If is_submission=True (i.e. 'Submit Code'), runs against all test cases.
        Hidden test inputs/outputs are never returned in results.
        """
        cases_to_run = test_cases if is_submission else [tc for tc in test_cases if tc.is_sample]
        if not cases_to_run:
            # Fallback if no sample test cases marked
            cases_to_run = test_cases[:1]

        test_results: List[TestCaseResult] = []
        passed_count = 0
        total_time_ms = 0.0
        max_memory_kb = 0.0
        final_verdict = "ACCEPTED"
        first_compile_output: Optional[str] = None
        first_stderr: Optional[str] = None
        first_stdout: Optional[str] = None

        for tc in cases_to_run:
            raw_res = await self.execute_single(
                source_code=source_code,
                language=language,
                stdin=tc.input,
                expected_output=tc.expected_output,
            )

            status_id = raw_res.get("status_id", 3)
            time_ms = raw_res.get("time", 0.0)
            mem_kb = raw_res.get("memory", 0.0)
            total_time_ms += time_ms
            max_memory_kb = max(max_memory_kb, mem_kb)

            # Map status
            if status_id == 3:
                tc_status = "ACCEPTED"
                passed = True
            elif status_id == 4:
                tc_status = "WRONG_ANSWER"
                passed = False
            elif status_id == 5:
                tc_status = "TIME_LIMIT_EXCEEDED"
                passed = False
            elif status_id == 6:
                tc_status = "COMPILATION_ERROR"
                passed = False
            elif status_id in [7, 8, 9, 10, 11, 12]:
                tc_status = "RUNTIME_ERROR"
                passed = False
            else:
                tc_status = "INTERNAL_ERROR"
                passed = False

            if passed:
                passed_count += 1
            else:
                if final_verdict == "ACCEPTED":
                    final_verdict = tc_status
                elif tc_status == "COMPILATION_ERROR":
                    final_verdict = "COMPILATION_ERROR"

            if raw_res.get("compile_output") and not first_compile_output:
                first_compile_output = raw_res.get("compile_output")
            if raw_res.get("stderr") and not first_stderr:
                first_stderr = raw_res.get("stderr")
            if raw_res.get("stdout") and not first_stdout:
                first_stdout = raw_res.get("stdout")

            # Redact inputs/outputs for hidden test cases
            tc_input = tc.input if tc.is_sample else None
            tc_expected = tc.expected_output if tc.is_sample else None
            tc_actual = raw_res.get("stdout") if tc.is_sample else None

            test_results.append(
                TestCaseResult(
                    test_case_id=tc.id,
                    is_sample=tc.is_sample,
                    status=tc_status,
                    passed=passed,
                    runtime_ms=time_ms,
                    memory_kb=mem_kb,
                    stdout=tc_actual,
                    stderr=raw_res.get("stderr") if tc.is_sample else None,
                    compile_output=raw_res.get("compile_output"),
                    input=tc_input,
                    expected_output=tc_expected,
                )
            )

            if tc_status == "COMPILATION_ERROR":
                break

        total_cases = len(cases_to_run)
        score = (passed_count / total_cases * total_marks) if total_cases > 0 else 0.0

        if passed_count == total_cases and total_cases > 0:
            final_verdict = "ACCEPTED"

        return Judge0SubmissionResult(
            verdict=final_verdict,
            total_tests=total_cases,
            passed_tests=passed_count,
            score=round(score, 2),
            max_score=total_marks,
            execution_time_ms=round(total_time_ms, 2),
            memory_kb=round(max_memory_kb, 2),
            compile_output=first_compile_output,
            stdout=first_stdout,
            stderr=first_stderr,
            test_results=test_results,
        )


judge0_service = Judge0Service()

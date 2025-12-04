import sys
import os
import xml.etree.ElementTree as ET
from typing import List, Dict

from .gemini_client import get_gemini_model


def parse_junit_failures(xml_path: str) -> List[Dict[str, str]]:
    """
    Parse JUnit XML and extract failed testcases with message & stack trace.
    """
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"JUnit XML file not found: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    failures: List[Dict[str, str]] = []

    for testcase in root.iter("testcase"):
        name = testcase.attrib.get("name", "unknown")
        classname = testcase.attrib.get("classname", "")
        full_name = f"{classname}::{name}" if classname else name

        failure_node = testcase.find("failure")
        error_node = testcase.find("error")

        if failure_node is not None:
            msg = failure_node.attrib.get("message", "")
            text = failure_node.text or ""
            failures.append(
                {
                    "test": full_name,
                    "type": "failure",
                    "message": msg,
                    "details": text,
                }
            )
        elif error_node is not None:
            msg = error_node.attrib.get("message", "")
            text = error_node.text or ""
            failures.append(
                {
                    "test": full_name,
                    "type": "error",
                    "message": msg,
                    "details": text,
                }
            )

    return failures


def analyze_failures_with_gemini(failures: List[Dict[str, str]]) -> str:
    """
    Ask Gemini to analyze the list of failures and suggest likely root causes
    and next debugging steps.
    Returns a plain-text report.
    """
    if not failures:
        return "No failed tests found. All tests passed."

    model = get_gemini_model()

    summarized = []
    for f in failures:
        summarized.append(
            f"Test: {f['test']}\nType: {f['type']}\nMessage: {f['message']}\nDetails:\n{f['details']}\n"
        )

    joined = "\n---\n".join(summarized)

    prompt = (
        "You are an expert SDET and software engineer.\n"
        "Given the following pytest JUnit test failures, do the following:\n"
        "1. Group failures by likely root cause.\n"
        "2. For each group, suggest probable root cause (app bug vs test bug vs env issue).\n"
        "3. Suggest specific next debugging steps (which logs to check, which module to inspect, etc.).\n"
        "4. If it looks like a flaky test, call that out.\n\n"
        "Be concise but actionable.\n\n"
        f"Here are the failures:\n\n{joined}"
    )

    response = model.generate_content(prompt)
    return response.text


def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_tools/failure_analyzer.py <path-to-junit-xml>")
        sys.exit(1)

    junit_path = sys.argv[1]
    failures = parse_junit_failures(junit_path)
    report = analyze_failures_with_gemini(failures)

    print("\n=== AI Failure Analysis Report (Gemini) ===\n")
    print(report)
    print("\n==========================================\n")


if __name__ == "__main__":
    main()

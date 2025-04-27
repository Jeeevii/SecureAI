import json
import re
import sys
import argparse
from collections import Counter

"""
Module: safety_vuln_extractor.py

SafetyReportParser can parse a Safety JSON report in three formats:
 1. Array-style JSON (top-level list)
 2. Dict with "remediations" key (tree-style)

It extracts a simplified list containing:
  - package_name
  - analyzed_version
  - vulnerabilities_found

"""
class SafetyReportParser:
    def __init__(self, raw_text: str):
        self._raw_text = raw_text
        self._report = None

    @classmethod
    def from_file(cls, path: str) -> 'SafetyReportParser':
        try:
            raw = open(path, 'r', encoding='utf-8').read()
        except OSError as e:
            raise RuntimeError(f"Unable to read file '{path}': {e}")
        return cls(raw)

    def _parse_raw_json(self):
        m = re.search(r'[\[\{]', self._raw_text)
        trimmed = self._raw_text[m.start():] if m else self._raw_text
        try:
            data, _ = json.JSONDecoder().raw_decode(trimmed)
            self._report = data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

    def get_vulnerabilities(self) -> list:
        """
        Parses the raw JSON report and returns a list of dicts with:
        package_name, analyzed_version, vulnerabilities_found
        """
        if self._report is None:
            self._parse_raw_json()
        rpt = self._report
        if isinstance(rpt, dict) and 'remediations' in rpt:
            return self._parse_remediations(rpt['remediations'])
        if isinstance(rpt, dict) and isinstance(rpt.get('vulnerabilities'), list):
            return self._filter_array(rpt['vulnerabilities'])
        if isinstance(rpt, list):
            return self._filter_array(rpt)
        return []

    @staticmethod
    def _parse_remediations(remediations: dict) -> list:
        results = []
        for pkg, pkg_info in remediations.items():
            for spec, detail in pkg_info.get('requirements', {}).items():
                version = detail.get('version') or spec.lstrip('=<>!')
                vuln_count = detail.get('vulnerabilities_found', 0)
                results.append({
                    'package_name': pkg,
                    'analyzed_version': version,
                    'vulnerabilities_found': vuln_count
                })
        return results

    @staticmethod
    def _filter_array(vulns: list) -> list:
        counts = Counter((v.get('package_name'), v.get('installed_version') or v.get('analyzed_version')) for v in vulns)
        return [
            {
                'package_name': pkg,
                'analyzed_version': ver,
                'vulnerabilities_found': cnt
            }
            for (pkg, ver), cnt in sorted(counts.items())
        ]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract simplified vulnerabilities from a Safety JSON report."
    )
    parser.add_argument('report_file', help='Path to the Safety JSON report')
    args = parser.parse_args()
    try:
        extractor = SafetyReportParser.from_file(args.report_file)
        simplified = extractor.get_vulnerabilities()
        print(json.dumps(simplified, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

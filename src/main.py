import json
import os
from itertools import groupby

import requests
from datetime import datetime, timezone


def _get_annotation_message(start_line, end_line):
    if end_line == start_line:
        return f"Added line #L{start_line} not covered by tests"
    else:
        return f"Added lines #L{start_line}-{end_line} not covered by tests"


def get_missing_range(range_list):
    for a, b in groupby(enumerate(range_list), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield {"start_line" : b[0][1], "end_line": b[-1][1]}


def create_single_annotation(error, file_path):
    start_line = error['start_line']
    end_line = error['end_line']
    message = _get_annotation_message(start_line, end_line)
    annotation = dict(
        path=file_path,
        start_line=start_line,
        end_line=end_line,
        annotation_level='warning',
        message=message,
    )
    return annotation


class CheckRun:
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
    GITHUB_EVENT_PATH = os.environ['GITHUB_EVENT_PATH']
    GITHUB_API= os.environ['GITHUB_API_URL']

    ACCEPT_HEADER_VALUE = f"application/vnd.github.v3+json"
    AUTH_HEADER_VALUE = f"token {GITHUB_TOKEN}"

    # This is the max annotations Github API allows.
    MAX_ANNOTATIONS = 50

    def __init__(self):
        self.repo_full_name = os.environ['GITHUB_REPOSITORY']
        self.head_sha = os.environ['PR_HEAD_SHA']
        self.read_coverage_output()
        self.files_with_missing_coverage = 0
        self.annotations = []

    def read_coverage_output(self):
        with open('coverage.json') as coverage_output_file:
            self.coverage_output = json.loads(coverage_output_file.read())

    def create_annotations(self):
        for file_path, file_data in self.coverage_output["files"].items():
            missing_lines = file_data["missing_lines"]
            if len(missing_lines) == 0:
                continue
            self.files_with_missing_coverage += 1
            for missing_range in get_missing_range(missing_lines):
                annotation = create_single_annotation(missing_range, file_path)
                self.annotations.append(annotation)
                if len(self.annotations) == 50:
                    return

    def get_summary(self):
        number_of_annotations = len(self.annotations)
        total_coverage_files = self.coverage_output["files"].keys()
        missing_coverage_file_count = sum([True if len(self.coverage_output["files"][file_report]["missing_lines"])
                                           else False for file_report in total_coverage_files])
        missing_ranges_count = number_of_annotations if number_of_annotations < 50 else "50+"
        summary = f"""
        Coverage Report:
        Total files : {len(total_coverage_files)}
        Files with missing lines : {missing_coverage_file_count}
        Missing coverage line ranges : {missing_ranges_count}
        """
        return summary

    def get_conclusion(self):
        if len(self.annotations) == 0:
            return 'success'
        return 'failure'

    def get_payload(self):
        summary = self.get_summary()
        conclusion = self.get_conclusion()

        payload = {
            'name': 'pytest-coverage',
            'head_sha': self.head_sha,
            'status': 'completed',
            'conclusion': conclusion,
            'completed_at': datetime.now(timezone.utc).isoformat(),
            'output': {
                'title': 'Coverage Result',
                'summary': summary,
                'text': 'Coverage results',
                'annotations': self.annotations,
            },
        }
        return payload

    def create(self):
        self.create_annotations()
        payload = self.get_payload()
        response = requests.post(
            f'{self.GITHUB_API}/repos/{self.repo_full_name}/check-runs',
            headers={
                'Accept': self.ACCEPT_HEADER_VALUE,
                'Authorization': self.AUTH_HEADER_VALUE,
            },
            json=payload,
        )
        response.raise_for_status()


if __name__ == '__main__':
    check_run = CheckRun()
    check_run.create()

import argparse
import json
from typing import List, Optional

from .sync_project import run


def main(argv: Optional[List[str]] = None) -> int:
    argparse.ArgumentParser(description="Read back the Campaign OS Project").parse_args(argv)
    report = run(False)
    verified = (
        report["project_exists"]
        and report["canonical_issue_items"] == 69
        and report["issue_items"] >= report["canonical_issue_items"]
        and report["pull_request_items"] >= 1
        and report["private"]
        and not report["custom_fields_missing"]
        and not report["preview_url_mismatches"]
        and not report["browser_configuration_required"]
    )
    print(json.dumps({"verified_core": verified, **report}, sort_keys=True))
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import json
from pathlib import Path
from typing import List, Optional

from .sync_issues import run


def main(argv: Optional[List[str]] = None) -> int:
    argparse.ArgumentParser(description="Verify canonical Campaign OS Issues").parse_args(argv)
    report = run(False)
    missing_or_drifted = len(report["planned_actions"])
    print(json.dumps({"verified": missing_or_drifted == 0, "drift": missing_or_drifted, "remote_campaign_os_issues": report["remote_campaign_os_issues"]}))
    return 0 if missing_or_drifted == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

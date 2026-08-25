import argparse
import json
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional

from .gh_client import GitHubClient, GitHubError
from .sync_issues import KEY_RE


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "github-campaign-os" / "project-schema.json"
MANIFEST_PATH = ROOT / "github-campaign-os" / "manifest.json"
REPORT_PATH = ROOT / "github-campaign-os" / "project-sync-report.json"
OWNER = "vincent-laroche"
REPO = "vincent-laroche/email-marketing-ops"

RECORD_TO_FIELD = {
    "Stage": "stage", "Priority": "priority", "Work Type": "work_type", "Platform": "platform",
    "Campaign Type": "campaign_type", "Objective": "objective", "Audience": "audience", "Offer": "offer",
    "Execution Mode": "execution_mode", "Messaging State": "messaging_state", "Shopify Messaging URL": "shopify_messaging_url",
    "Flow Required": "flow_required", "Flow State": "flow_state", "Shopify Flow URL": "shopify_flow_url",
    "Automation Trigger": "automation_trigger", "Automation / Flow Name": "automation_flow_name",
    "Production Start": "production_start", "Send Date": "send_date", "Results Review": "results_review",
    "Recipients": "recipients", "Open Rate %": "open_rate", "Click Rate %": "click_rate",
    "Conversion Rate %": "conversion_rate", "Revenue": "revenue", "Unsubscribe Rate %": "unsubscribe_rate",
    "Primary KPI": "primary_kpi", "Target KPI": "target_kpi", "Preview URL": "preview_url",
}
COLORS = ["BLUE", "GREEN", "PURPLE", "ORANGE", "RED", "YELLOW", "PINK", "GRAY"]


PROJECT_QUERY = """query($login:String!,$title:String!){
  user(login:$login){ id projectsV2(first:50,query:$title){nodes{id number title closed public
    fields(first:100){nodes{... on ProjectV2FieldCommon{id name dataType} ... on ProjectV2SingleSelectField{id name dataType options{id name}}}}
    items(first:100){nodes{id type content{... on Issue{id number body repository{nameWithOwner}} ... on PullRequest{id number repository{nameWithOwner}}}}}
    views(first:20){nodes{id name layout filter}}
  }}}
  repository(owner:"vincent-laroche",name:"email-marketing-ops"){id isPrivate}
}"""


def project_state(client: GitHubClient, title: str) -> Dict[str, Any]:
    data = client.graphql(PROJECT_QUERY, {"login": OWNER, "title": title})
    matches = [project for project in data["user"]["projectsV2"]["nodes"] if project["title"] == title and not project["closed"]]
    if len(matches) > 1:
        raise GitHubError("duplicate Campaign OS Projects")
    return {"owner_id": data["user"]["id"], "repository": data["repository"], "project": matches[0] if matches else None}


def graphql_batch(client: GitHubClient, mutation_name: str, input_type: str, inputs: List[Dict[str, Any]], selection: str) -> None:
    for start in range(0, len(inputs), 20):
        batch = inputs[start:start + 20]
        variables = ",".join(f"$i{index}:{input_type}!" for index in range(len(batch)))
        calls = "\n".join(f"m{index}:{mutation_name}(input:$i{index}){{{selection}}}" for index in range(len(batch)))
        client.graphql(f"mutation({variables}){{{calls}}}", {f"i{index}": value for index, value in enumerate(batch)})


def option_inputs(names: Iterable[str]) -> List[Dict[str, str]]:
    return [{"name": name, "color": COLORS[index % len(COLORS)], "description": "Campaign OS"} for index, name in enumerate(names)]


def create_or_reconcile_structure(client: GitHubClient, state: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    project = state["project"]
    if project is None:
        data = client.graphql("mutation($input:CreateProjectV2Input!){createProjectV2(input:$input){projectV2{id}}}", {"input": {"ownerId": state["owner_id"], "repositoryId": state["repository"]["id"], "title": schema["title"]}})
        project_id = data["createProjectV2"]["projectV2"]["id"]
    else:
        project_id = project["id"]
    fresh = project_state(client, schema["title"])["project"]
    fields = {field["name"]: field for field in fresh["fields"]["nodes"]}
    status = fields.get("Status")
    if status and [item["name"] for item in status.get("options", [])] != schema["status"]:
        client.graphql("mutation($input:UpdateProjectV2FieldInput!){updateProjectV2Field(input:$input){projectV2Field{... on ProjectV2SingleSelectField{id}}}}", {"input": {"fieldId": status["id"], "singleSelectOptions": option_inputs(schema["status"])}})
    create_inputs = []
    for field in schema["fields"]:
        if field["name"] in fields:
            existing = fields[field["name"]]
            if field["type"] == "single_select" and [item["name"] for item in existing.get("options", [])] != field["options"]:
                client.graphql("mutation($input:UpdateProjectV2FieldInput!){updateProjectV2Field(input:$input){projectV2Field{... on ProjectV2SingleSelectField{id}}}}", {"input": {"fieldId": existing["id"], "singleSelectOptions": option_inputs(field["options"])}})
            continue
        value = {"projectId": project_id, "name": field["name"], "dataType": field["type"].upper()}
        if field["type"] == "single_select":
            value["singleSelectOptions"] = option_inputs(field["options"])
        create_inputs.append(value)
    graphql_batch(client, "createProjectV2Field", "CreateProjectV2FieldInput", create_inputs, "projectV2Field{... on ProjectV2FieldCommon{id}}")
    return project_state(client, schema["title"])["project"]


def add_items(client: GitHubClient, project: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, str]:
    issues = [item for item in client.paginate(f"/repos/{REPO}/issues?state=all") if "pull_request" not in item]
    by_key = {}
    for issue in issues:
        match = KEY_RE.search(issue.get("body") or "")
        if match:
            by_key[match.group(1)] = issue
    existing = {node.get("content", {}).get("id"): node["id"] for node in project["items"]["nodes"] if node.get("content")}
    inputs = [{"projectId": project["id"], "contentId": by_key[record["key"]]["node_id"]} for record in manifest["records"] if by_key[record["key"]]["node_id"] not in existing]
    graphql_batch(client, "addProjectV2ItemById", "AddProjectV2ItemByIdInput", inputs, "item{id}")
    fresh = project_state(client, project["title"])["project"]
    existing_content_ids = {node.get("content", {}).get("id") for node in fresh["items"]["nodes"] if node.get("content")}
    campaign_issue_numbers = {issue["number"] for issue in by_key.values()}
    pull_requests = client.paginate(f"/repos/{REPO}/pulls?state=all")
    pr_inputs = []
    for pull_request in pull_requests:
        references = {int(value) for value in re.findall(r"#(\d+)", pull_request.get("body") or "")}
        if references & campaign_issue_numbers and pull_request["node_id"] not in existing_content_ids:
            pr_inputs.append({"projectId": project["id"], "contentId": pull_request["node_id"]})
    graphql_batch(client, "addProjectV2ItemById", "AddProjectV2ItemByIdInput", pr_inputs, "item{id}")
    fresh = project_state(client, project["title"])["project"]
    item_by_key = {}
    issue_number_to_key = {issue["number"]: key for key, issue in by_key.items()}
    for node in fresh["items"]["nodes"]:
        content = node.get("content")
        if content and content.get("repository", {}).get("nameWithOwner") == REPO and content.get("number") in issue_number_to_key:
            item_by_key[issue_number_to_key[content["number"]]] = node["id"]
    return item_by_key


def update_values(client: GitHubClient, project: Dict[str, Any], manifest: Dict[str, Any], item_by_key: Dict[str, str]) -> None:
    fields = {field["name"]: field for field in project["fields"]["nodes"]}
    updates = []
    for record in manifest["records"]:
        field_values = {"Status": record["status"]}
        field_values.update({name: record[key] for name, key in RECORD_TO_FIELD.items()})
        for name, value in field_values.items():
            if value is None or value == "":
                continue
            field = fields[name]
            if field["dataType"] == "SINGLE_SELECT":
                option = next((item for item in field["options"] if item["name"] == str(value)), None)
                if option is None:
                    raise GitHubError(f"missing Project option {name}: {value}")
                encoded = {"singleSelectOptionId": option["id"]}
            elif field["dataType"] == "NUMBER":
                encoded = {"number": float(value)}
            elif field["dataType"] == "DATE":
                encoded = {"date": value}
            else:
                encoded = {"text": str(value)[:1024]}
            updates.append({"projectId": project["id"], "itemId": item_by_key[record["key"]], "fieldId": field["id"], "value": encoded})
    graphql_batch(client, "updateProjectV2ItemFieldValue", "UpdateProjectV2ItemFieldValueInput", updates, "projectV2Item{id}")


def run(apply: bool) -> Dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    client = GitHubClient()
    state = project_state(client, schema["title"])
    project = state["project"]
    before_items = 0 if project is None else len(project["items"]["nodes"])
    if apply:
        project = create_or_reconcile_structure(client, state, schema)
        item_by_key = add_items(client, project, manifest)
        project = project_state(client, schema["title"])["project"]
        update_values(client, project, manifest, item_by_key)
        project = project_state(client, schema["title"])["project"]
    actual_views = [] if project is None else [{"name": view["name"], "layout": view["layout"], "filter": view.get("filter") or ""} for view in project["views"]["nodes"]]
    expected_views = [{"name": view["name"], "layout": view["layout"], "filter": view.get("filter") or ""} for view in schema["views"]]
    actual_field_names = set() if project is None else {field["name"] for field in project["fields"]["nodes"]}
    missing_fields = [field["name"] for field in schema["fields"] if field["name"] not in actual_field_names]
    missing_views = [view["name"] for view in expected_views if view not in actual_views]
    issue_items = 0 if project is None else sum(node["type"] == "ISSUE" for node in project["items"]["nodes"])
    pull_request_items = 0 if project is None else sum(node["type"] == "PULL_REQUEST" for node in project["items"]["nodes"])
    report = {
        "mode": "apply" if apply else "dry-run", "project_exists": project is not None,
        "project_number": project.get("number") if project else None, "project_url": f"https://github.com/users/{OWNER}/projects/{project['number']}" if project else None,
        "private": (not project.get("public")) if project else True, "repository": REPO,
        "issue_items": issue_items if project else before_items, "pull_request_items": pull_request_items,
        "custom_fields_expected": len(schema["fields"]), "custom_fields_missing": missing_fields,
        "views_expected": len(schema["views"]), "views": actual_views,
        "browser_configuration_required": missing_views,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize the private Campaign OS Project")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run(args.apply), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

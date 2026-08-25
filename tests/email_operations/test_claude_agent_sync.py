from pathlib import Path
import re
import unittest

from tools.sync_claude_agents import CLASS_COLOR, MARKER, render, sources
from tools.validate_project_agents import EXPECTED_ROLES, parse_definition


ROOT = Path(__file__).resolve().parents[2]
FRONTMATTER = re.compile(r"\A---\n(?P<meta>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)


def _generated(name: str) -> str:
    return (ROOT / ".claude/agents" / name).read_text(encoding="utf-8")


class ClaudeAgentSyncTest(unittest.TestCase):
    def test_generated_suite_is_current(self):
        for source in sources():
            with self.subTest(agent=source.name):
                self.assertEqual(render(source), _generated(source.name))

    def test_every_codex_agent_has_a_claude_twin(self):
        """Exactly the Codex agents, no strays.

        Compares only files carrying the provenance marker: the directory also
        holds a hand-written README, which the sync deliberately leaves alone.
        """
        generated = {
            path.name
            for path in (ROOT / ".claude/agents").glob("*.md")
            if MARKER in path.read_text(encoding="utf-8")
        }
        self.assertEqual({path.name for path in sources()}, generated)

    def test_hand_written_files_are_not_reclaimed(self):
        readme = ROOT / ".claude/agents/README.md"
        self.assertTrue(readme.is_file(), "the sync deleted the hand-written README")
        self.assertNotIn(MARKER, readme.read_text(encoding="utf-8"))

    def test_tools_are_comma_separated_not_a_yaml_list(self):
        """Claude Code documents `tools` as a comma-separated string.

        A YAML list is undocumented. If its entries resolve to nothing Claude
        Code refuses to launch the agent; if the field is lost altogether the
        agent inherits every tool, which would silently give a read-only
        reviewer Write and Edit.
        """
        for source in sources():
            with self.subTest(agent=source.name):
                meta = FRONTMATTER.match(_generated(source.name)).group("meta")
                tools = [
                    line for line in meta.splitlines() if line.startswith("tools:")
                ]
                self.assertEqual(1, len(tools))
                self.assertNotIn("[", tools[0])

    def test_permission_class_boundaries_survive_translation(self):
        write_tools = {"Write", "Edit", "NotebookEdit"}
        for source in sources():
            definition = parse_definition(source)
            permission = EXPECTED_ROLES[definition.name]
            meta = FRONTMATTER.match(_generated(source.name)).group("meta")
            declared = {
                part.strip()
                for line in meta.splitlines()
                if line.startswith("tools:")
                for part in line.split(":", 1)[1].split(",")
            }
            with self.subTest(agent=source.name, permission=permission):
                if permission == "read-only":
                    self.assertEqual(set(), declared & write_tools)
                elif permission == "local-write":
                    self.assertLessEqual({"Write", "Edit"}, declared)
                elif permission == "approval-gated":
                    self.assertEqual(set(), declared & {"Write", "Edit"})
                self.assertNotIn("Agent", declared)

    def test_descriptions_survive_a_real_yaml_parser(self):
        """The repository validator parses frontmatter by hand; Claude Code does not.

        `email-project-manager` describes itself as routing "for Project #4",
        and unquoted YAML treats ' #' as a comment — truncating the routing
        trigger Claude Code relies on to select the agent.
        """
        yaml = __import__("yaml")
        for source in sources():
            with self.subTest(agent=source.name):
                stored = str(parse_definition(source).metadata.get("description", ""))
                meta = FRONTMATTER.match(_generated(source.name)).group("meta")
                self.assertEqual(stored, yaml.safe_load(meta)["description"])

    def test_body_is_copied_byte_for_byte(self):
        for source in sources():
            with self.subTest(agent=source.name):
                original = FRONTMATTER.match(
                    source.read_text(encoding="utf-8")
                ).group("body")
                generated = FRONTMATTER.match(_generated(source.name)).group("body")
                self.assertTrue(generated.endswith(original))

    def test_colour_encodes_permission_class(self):
        for source in sources():
            definition = parse_definition(source)
            expected = CLASS_COLOR[EXPECTED_ROLES[definition.name]]
            with self.subTest(agent=source.name):
                self.assertIn(f"color: {expected}", _generated(source.name))


if __name__ == "__main__":
    unittest.main()

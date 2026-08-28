# Email Marketing project-agent system

The project-local team is intentionally twelve specialised roles. It replaces
the four thin definitions and does not reactivate the older global,
MailerLite-first agents.

Every role follows [the shared operating contract](EMAIL_MARKETING_AGENT_CONTRACT.md).
All work is attached to a canonical Issue or `campaign-os-key`; evidence moves
between roles through the standard packet in that contract.

| Role | Invoke when | Owns | Does not own |
| --- | --- | --- | --- |
| `email-project-manager` | a queue, dependency, or priority needs review | read-only Campaign OS reconciliation and next-task routing | GitHub mutations or platform operation |
| `email-lifecycle-architect` | one journey needs an implementation contract | entry/exit/collision, eligibility, rollback, KPI plan | implementation or activation |
| `email-producer` | one Email Issue needs assembly | named email HTML/copy and local validation | reusable modules or platform drafts |
| `email-design-module-specialist` | a reusable module needs work | named module trio/design consistency | complete Email Issue assembly |
| `email-preview-qa-engineer` | stable source needs fixture/render proof | private preview artifacts and provenance | Pages enablement or publication |
| `email-audience-consent-steward` | an audience or consent premise needs proof | read-only eligibility/suppression evidence | tags, segments, or customers |
| `shopify-messaging-campaign-operator` | Vincent explicitly authorizes one draft | one named Messaging draft and complete read-back | schedule, activation, or send |
| `shopify-flow-automation-builder` | Vincent explicitly authorizes one accepted journey | one disabled Flow graph and read-back | activation or sending |
| `email-deliverability-release-reviewer` | a candidate is ready for the final gate | fail-closed release verdict | activation or send |
| `email-performance-analyst` | live/release evidence exists | read-only normalized measurement and learning | metric invention or platform changes |
| `campaign-os-engineer` | Issue/Project automation needs maintenance | local manifest/sync tooling and zero-drift checks | unapproved `--apply` or platform operation |
| `shopify-notification-template-specialist` | an approved native notification template batch needs work | named transactional templates and verification | marketing campaigns or sending |

Run `python3 scripts/validate-email-agent-system.py` after changing the suite.
The check validates agent names, frontmatter, shared-contract routing,
approved tools, role boundaries, and the required safety/output sections.

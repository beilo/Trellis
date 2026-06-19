# Trellis

Trellis coordinates AI-assisted development workflows for projects and the AI tools that operate inside them.

## Language

**Code Intelligence MCP Integration**:
A capability that lets AI tools use an external code intelligence service through MCP. Trellis provides an explicit opt-in entry point, while the external service owns MCP setup details, indexing, generated instructions, and code-graph answers.
_Avoid_: GitNexus project template, GitNexus CLI wrapper

**Opt-in Integration**:
An integration that is installed only after an explicit user choice. It is not inferred from the selected AI platform or from project configuration.
_Avoid_: default integration, platform-implied integration

**Setup Command**:
A Trellis CLI command that explicitly installs or configures an external capability for an already initialized Trellis project. `tl init` remains Trellis project onboarding; `tl setup <target>` installs a named external capability.
_Avoid_: init flag, hidden compatibility alias, integration subcommand hidden under init, interactive integration prompt

**Setup Target**:
A registered external capability that `tl setup` can install or configure for the current project. Unknown targets are rejected instead of interpreted dynamically.
_Avoid_: init option, platform flag, Trellis project template

**Delegated MCP Setup**:
MCP configuration performed by an external integration's setup command after the user explicitly runs a Trellis setup command. Trellis owns the opt-in decision; the integration owns the detailed MCP wiring it knows how to install.
_Avoid_: Trellis-authored MCP wiring, hand-copied MCP configuration

**Setup Authorization Command**:
A setup command that grants Trellis permission to run the external integration's setup command without a second confirmation prompt. The explicit command is the user's consent for the setup side effects.
_Avoid_: second setup prompt, implicit setup

**Required Integration Setup**:
An explicitly requested setup target whose setup must complete successfully for the Trellis command to succeed. If the external setup command fails, the Trellis setup command fails too.
_Avoid_: best-effort integration setup, warning-only setup failure

**Setup-only Enablement**:
An integration enablement flow that runs the external MCP setup command but does not create or refresh a code index. Indexing remains a separate user-authorized action.
_Avoid_: setup-and-index enablement, implicit first index

**External Setup Command**:
The concrete command Trellis runs after a user opts in to an external integration. For GitNexus, the first supported setup command is `npx --yes gitnexus setup`.
_Avoid_: global binary requirement, pinned latest setup command

**Stateless Integration Enablement**:
An enablement flow that does not write a Trellis-owned project configuration flag for the setup target. The target's availability is determined by its own setup, MCP configuration, and index state rather than a Trellis config marker.
_Avoid_: Trellis integration registry, project-level integration flag

**External Artifact Ownership**:
Files and ignore rules created for an external integration remain owned by that integration or by the user, not by Trellis. Trellis does not add project ignore rules or local artifact management for a stateless integration.
_Avoid_: Trellis-managed external artifacts, integration-owned files in Trellis templates

**Lazy Code Indexing**:
Code index creation triggered only after an AI tool needs code intelligence, discovers that the integration has no usable index, and receives user approval to create it. Project initialization does not eagerly build the index.
_Avoid_: init-time indexing, automatic indexing

**On-demand Index Refresh**:
Index refresh performed only when an AI tool needs fresh code-graph answers after the code has changed. It is not tied to every file edit, project update, or task lifecycle event.
_Avoid_: per-edit indexing, always-fresh index

**User-authorized Indexing**:
Index creation or refresh that occurs only after the user explicitly allows it. AI tools may identify that an index is missing or stale, but they do not decide to build or refresh it on their own.
_Avoid_: autonomous indexing, implicit refresh

**Per-refresh Consent**:
A consent model where each index creation or refresh is approved individually by the user. Enabling the integration does not grant standing permission to run future indexing commands.
_Avoid_: project-level auto indexing, standing indexing permission

**GitNexus-owned Instructions**:
Agent instructions generated and maintained by GitNexus for its own code intelligence workflow. Trellis may allow these instructions to coexist with Trellis instructions, but Trellis does not author or reinterpret the detailed GitNexus rules.
_Avoid_: Trellis-authored GitNexus rules, copied GitNexus prompts

**Instruction-free Setup Delegation**:
A setup delegation where Trellis does not add any integration-specific agent instructions. Any integration-specific instructions are produced later by the external integration's own indexing or setup workflow.
_Avoid_: Trellis-authored integration hints, minimal Trellis integration block

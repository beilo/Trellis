# Delegate GitNexus Setup Instead of Owning Its Integration Surface

Trellis will treat GitNexus as an external code intelligence MCP integration, not as a Trellis-owned project template feature. `tl init --with-gitnexus` runs `npx --yes gitnexus setup` after Trellis writes its normal project files, and setup failure fails the command; Trellis will not author GitNexus instructions, manage GitNexus index files, write GitNexus ignore rules, store a project-level GitNexus enabled flag, run `gitnexus analyze`, or provide `tl update --with-gitnexus` in the first integration shape.

This keeps ownership clear: GitNexus owns MCP setup details, indexing, and its generated `gitnexus` instruction block, while Trellis only provides an explicit opt-in entry point for new project initialization. Existing projects can run `gitnexus setup` directly, and a future dedicated command can be added if retrying setup through Trellis becomes important.

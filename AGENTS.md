# Fabric SRE repository

This repository contains a reusable Microsoft Fabric SRE accelerator.

## Rules

- Keep the shared core free of tenant, subscription, workspace, capacity, item,
  semantic model, and report IDs.
- Put customer values only in `config/client.parameters.yaml`, which is ignored.
- Preserve separate French and English deliverables.
- Keep the agent read-only by default. Never add a write operation without the
  approval guard and an audit record.
- Surface API errors and schema drift. Honor `Retry-After`.
- Generate PBIR with `scripts/generate-report.mjs`, then validate both reports.
- Validate TMDL before publishing.
- Update `docs/solution.fr.md` and `docs/solution.en.md` for behavior changes.

If you are in VS Code, read the vscode-microsoft-foundry skill first.


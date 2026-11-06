# Academic website maintenance

This is Feng Li's bilingual academic website, published at https://fonx1997.github.io/ from the `main` branch of `FonX1997/FonX1997.github.io`.

The user wants to request website changes conversationally and have the assistant implement, verify, and publish them. Treat requests to change this website as authorization to update its live version unless the user asks for a draft or local preview only. Keep changes within the requested scope.

## Source and content

- `tools/build_site.py` generates `index.html`, `research.html`, `publications.html`, `assets/publications.js`, and the BibTeX downloads. Edit the generator and data instead of changing generated HTML alone.
- `data/publications.json` contains the publication records. Preserve the distinction between published and accepted papers; do not invent DOIs, authors, years, or metrics. Maintain both languages and accurate first/corresponding-author labels.
- `assets/style.css` and `assets/main.js` contain styling and interactive behavior.
- The current Chinese CV in the adjacent `李峰的个人简历` folder is the local content reference. A website-only request does not authorize unrelated CV edits. The user does not want CV PDFs on the public website: keep the original CVs local, do not publish copies or download links, and do not reintroduce them during later updates unless explicitly requested.
- Preserve the user's preference for AI, deep learning, reinforcement learning, and parallel control. Do not add teaching, recruitment, or lab-resource sections unless asked.
- Do not display the user's GitHub profile or repository links in the public-facing website unless explicitly requested. Keep the Beihang emblem in the shared profile header.
- Follow the approved navy and pale-blue design: dark horizontal university/navigation header, pale-blue profile sidebar, clear text sections, restrained buttons and dividers. Avoid decorative hero graphics, 3D scientific objects, or ornamental backgrounds.
- The homepage has no News & updates section. Its Research areas section is a plain text list, without links or button styling.
- Show complete citations on both the homepage and publication page: all authors, full title, available journal/year/volume/issue/pages or article number, visible DOI, author role, and existing journal indicators and status. Do not invent missing bibliographic fields.

## Update and publish

1. Inspect the working tree, fetch the remote, and incorporate upstream updates without overwriting unrelated local changes. Use fast-forward updates where possible.
2. Implement the requested change. Regenerate the website using `python3 tools/build_site.py` when the generator or publication data changes.
3. Verify the affected pages and interactions. Use a local HTTP server and browser checks when layout or behavior changes. `tools/check_site.mjs` checks the current three-page layout, both languages, publication filters, citations, downloads, and mobile overflow; adapt assertions when requested content changes.
4. Commit only relevant, reviewed files and push to `origin main`. Never force-push. GitHub Pages is configured to publish this branch.
5. Verify the actual changed content on the live site after deployment, including affected links and downloads, before reporting completion. HTTP 200 alone does not establish that an update has deployed.

Repository-local `core.sshCommand` selects the dedicated SSH key and pinned GitHub host keys. Credentials live outside the repository. Never print private keys, copy credentials into site files, or commit `node_modules` or temporary screenshots. If authentication is unavailable, report that the repository deploy-key authorization must be completed; do not request account passwords or secret tokens in chat.

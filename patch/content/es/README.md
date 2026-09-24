Spanish versions of the patch pages in the directory above.

`markdown_page.render_markdown` looks here first when the active language is
Spanish and falls back to the English file when a translation is missing, so
these can be added one at a time. Keep the filenames identical to the English
ones — that's how they're matched.

Still English: summary.md, patch-notes.md, faq.md, server.md, wireguard.md.

# Review rules for maintainers

Contributors never write these files by hand; Zero-Out opens the pull request.
Your job is the part a program cannot judge.

## Every pull request

1. One file per pull request, and it is added, never edited. CI fails any pull
   request that modifies, renames or deletes an existing file under `trees/`.
2. CI must pass: the format check (`tools/community_check.py`) and the
   added-files-only check. Do not merge on red.
3. Read the prompts. They should read like a company's phone menu ("For billing,
   press 1"), not like a person talking, a voicemail greeting for an individual,
   or a conversation that was overheard.
4. Reject any file with personal data: a person's name or number, an address, an
   account detail, an email. The check strips and refuses long digit runs only; it
   cannot see a name.
5. Reject a file whose company name does not match the number's menu, or that is
   plainly junk, abusive or an advertisement.
6. Squash-free merge, so the file lands as submitted.

## Removing a bad file

If a merged file turns out to hold personal data or abuse:

1. Open a pull request that deletes that one file, with the reason in the
   description. The added-only check will fail it on purpose; a maintainer with
   admin rights merges it past that one check, and only for a deletion.
2. If it holds personal data, it still lives in git history. Ask GitHub support
   to purge the cached views, and if needed rewrite history with
   `git filter-repo --path <file> --invert-paths`, then force push with the
   other maintainers' agreement.
3. Tell the contributor if you can reach them.

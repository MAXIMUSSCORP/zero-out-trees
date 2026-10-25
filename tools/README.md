# tools

`community_check.py` and `site_build.py` are copies of the files of the same name
in zeroout's `zeroout/` package. The first line of each says so. Do not edit them
here; change them in zeroout and copy them over, adding the header comment as the
first line.

- `community_check.py`: checks one contribution file against SCHEMA.md.
- `site_build.py`: builds the read-only website. `python tools/site_build.py trees _site`
  (it also runs the checker over every file and exits 1 if any fail).

Both use only the Python standard library.

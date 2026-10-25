# zero-out-trees

A community map of US toll-free phone menus, built by people running
[Zero-Out](https://github.com/MAXIMUSSCORP/zero-out). Each file records what one
person's copy of Zero-Out heard when it called a company: the menu words, the
keys on offer, and where each key led.

Browse it: https://maximusscorp.github.io/zero-out-trees/

## Contribute

In Zero-Out, choose "Share with the community". It writes one file under
`trees/<number>/` and opens a pull request. You do not edit this repo by hand.
A check runs on every pull request; a maintainer reads what passes.

## What a file holds

- The company name and its toll-free number.
- For each menu position: the words of the prompt, the keys and their labels,
  what happened next (menu, hold, human, and so on), and when it was heard.

## What a file never holds

- No audio.
- No personal data. Runs of six or more digits are removed before sharing and
  the check refuses any that remain.
- Nothing about who ran the call beyond an anonymous 12 character contributor id
  in the file name.

The exact format is in [SCHEMA.md](SCHEMA.md). Maintainer rules are in
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

The data is released under CC0-1.0 (public domain dedication). See [LICENSE](LICENSE).

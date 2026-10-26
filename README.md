# brand

Skills for Claude Code, delivered as one package:

- `brand-builder` creates a brand from a brief, or imports a brand package or
  guide, and writes it to `docs/brand/` of the project: the rules, the tokens,
  the CSS variables, the logos, and the fonts. It maps the tokens into the
  theme of the project and adds a rule that loads the brand for each UI file.
- `brand-check` finds each place where the code, the assets, the copy, or
  the rules of the project differ from `docs/brand/`. For each grave
  deviation it proposes a guard: a change of a rule, a linter, or a check
  that stops the deviation from coming back.

## Contents

- `skills/brand-builder/SKILL.md` — the brand-builder skill.
- `skills/brand-check/SKILL.md` — the brand-check skill.
- `skills/brand-check/tools/brand-lint` — the machine check. It reads
  `<workspace>/docs/brand/tokens.json` and reports colors, fonts, corner
  radii, and ASCII forms of the name that the brand does not hold.
- `skills/brand-check/tools/test_brand_lint.py` — the tests of brand-lint.

## Why each part exists

- **One folder, `docs/brand/`.** The agent, the code, and the check read the
  same source. A brand that lives only in a PDF reaches the code through
  memory, and memory drifts.
- **One direction.** A package of alternatives is a choice to make. Marks,
  palettes, and fonts from several directions give no recognizable identity.
- **Three directions in create mode.** One proposal leaves the human no
  choice; more than three take longer to compare than they add.
- **`docs/brand/directions.md` between two turns.** The flow stops for the
  choice of the human. The next turn reads the list and the source from the
  file, so a one-word answer ("Datum") resumes the flow.
- **Confirmation before a replacement.** A second import over `docs/brand/`
  erases the rules and their exceptions; the human decides that.
- **`tokens.json` as the source of the values.** brand-lint reads it, and
  `brand.css` and the theme repeat it. A value that changes in one place
  shows as a lint finding in the others.
- **`BRD` rules with `must` or `should`.** The obligation word sets the
  severity, so brand-check grades a finding with no judgment of its own.
- **`Check: brand-lint` or `Check: review` on each rule.** The agent spends
  its reading on the rules that a script cannot test.
- **A machine check and a review check.** Colors, fonts, radii, and the
  spelling of the name are text matches, so a script finds each one in
  seconds. Voice, logo use, and layout need a reader.
- **A rules check.** A deviation in the code comes back while the rule that
  produced it stays: an agent skill that says "use Inter", a Tailwind theme
  that extends the default palette. The check reads the files that tell an
  agent, a linter, or a build what to write.
- **Grave at 3 repeats.** One deviation is a slip that one fix closes. A
  deviation that repeats shows a missing guard, so the fix alone comes back.
- **`theme`, not `theme.extend`.** With the default palette replaced, a class
  such as `text-blue-500` has no value, so the build shows the deviation.
- **Guards after approval, and declined guards stay declined.** A guard
  changes how the whole project is linted or written; the human owns that
  change. A declined guard that returns on each run trains the human to
  ignore the report.
- **Findings keep their `B` number.** Commits and issues name a finding by
  its number, so the number stays with it.
- **Exceptions in `lint` of `tokens.json`, with a reason in the guide.** An
  email signature needs a font that each mail client has; a vendor widget
  brings its own colors. A listed exception keeps the report about real
  deviations.
- **brand-lint reads the file list from git.** `.gitignore` already names the
  generated and vendored files of the project, so a monorepo needs no list
  of its own. Outside git, the tool skips dependency and build folders at
  any depth.
- **brand-lint skips `#123` outside a stylesheet.** In Markdown, YAML, and
  code, a short number after `#` is an issue or a pull request.

## Install

```sh
gh release download --repo dsl400/brand --pattern brand.tar.gz -O - | tar -xz -C ~/.claude/skills
```

Or from the source:

```sh
git clone git@github.com:dsl400/brand.git
ln -s "$PWD/brand/skills/brand-builder" ~/.claude/skills/brand-builder
ln -s "$PWD/brand/skills/brand-check" ~/.claude/skills/brand-check
```

## Test

```sh
python3 -m unittest discover -s skills/brand-check/tools -p 'test_*.py'
```

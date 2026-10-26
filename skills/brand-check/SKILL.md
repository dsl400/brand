---
name: brand-check
description: Use when the user asks to check that the code, the assets, or the project rules match the brand in docs/brand/, or when a change of the UI, the copy, or the rules needs a brand review.
metadata:
  source: https://github.com/dsl400/brand
  version: 0.1.0
---

# brand-check

The brand lives in `<workspace>/docs/brand/`: the rules in `README.md`
(`BRD-n`) and the values in `tokens.json`. The brand-builder skill writes
them and defines their shape. This skill finds each place where the code,
the assets, the copy, or the rules of the project differ from the brand, and
proposes a guard for each grave deviation.

`<skill>` is the folder of this file. `<workspace>` is the root of the project
that holds `docs/`.

## The machine check

```sh
<skill>/tools/brand-lint [<path> ...] --workspace <workspace>
```

```
src/app.css:12:10 — BL-COLOR — #3B82F6 is not in the palette
src/Hero.tsx:4:15 — BL-FONT — font 'Inter' is not in the typography of the brand
src/Card.css:8:3 — BL-RADIUS — radius 8px is not the corner radius of the brand
index.html:6:8 — BL-NAME — 'Andrei Dragan' in place of 'Andrei Drăgan'
```

- With no path, the tool scans the workspace: the files that git tracks or
  that `.gitignore` permits. It skips `docs/brand/`, `reports/`, dependency
  and build folders at any depth, and the globs of `lint.exclude` in
  `tokens.json`.
- A line that holds `brand-lint: allow` is skipped. Each such line needs a
  comment with the reason.
- `BL-NAME` is a deviation in each place a person reads: a title, an Open
  Graph tag, an `alt` text, a heading, a copyright line, PDF metadata. It is
  correct in a field that rejects diacritics, such as a mail header of a
  system that sends ASCII only. Confirm each one by reading the line.
- The docstring of the tool lists the patterns it cannot read. Read those
  by hand in the review check.

## The review check

Apply each `BRD` rule with `Check: review` by reading the code, the assets,
and the copy:

- The logo: each use comes from `docs/brand/logos/`, with the clear space and
  the minimum size of the guide. A redrawn, stretched, recolored, or
  re-typeset logo is a deviation.
- Color: compute the WCAG ratio of each pair of text and background from
  their hex values, and compare it with `contrast_min`. The accent covers the
  area that the guide gives it.
- Type: the role of each font (display, body, utility) and its weight match
  the guide.
- Voice: headlines, calls to action, and bios follow the voice of the guide
  and its sample lines.
- Layout and motion: alignment, margins, and durations match the guide.
- The patterns that brand-lint cannot read: `oklch()`, `color-mix()`, named
  Tailwind classes (`rounded-lg`, `text-blue-500`), values built at runtime,
  PNG, PDF, and Office files.

## The rules check

Read each file that tells an agent, a linter, or a build how to write the
UI: `AGENTS.md`, `CLAUDE.md`, `.claude/rules/*.md`,
`.claude/skills/*/SKILL.md`, `.stylelintrc*`, `.eslintrc*`,
`eslint.config.*`, `tailwind.config.*`, the theme and token files of the
design system, and the CI workflows.

| Deviation | Severity |
|---|---|
| `.claude/rules/brand.md` is absent, or its `paths` miss a UI file type of the project | grave |
| A rule, a skill, or `AGENTS.md` prescribes a value off the brand: a font ("use Inter"), a library default ("shadcn defaults", "the Tailwind palette"), a radius class (`rounded-md`), a tone | grave |
| The theme (`tailwind.config.*` `theme`, a token file) holds a color, a font, or a radius off the brand, or extends the default palette in place of a replacement | grave |
| No linter rule and no CI step enforces the tokens | minor; grave when a code deviation repeats 3 or more times |

## Severity

| Severity | When |
|---|---|
| `grave` | A `must` rule of the guide is broken |
| `grave` | The same deviation repeats in 3 or more places |
| `grave` | A row of the rules check marks it grave |
| `minor` | A `should` rule is broken, or a single deviation of a value |

## The report

`<workspace>/reports/brand-check.md` holds the findings. Each finding keeps
its number for the life of the file.

```markdown
# Brand check

## B4. The interface uses Inter for the body text
- Severity: grave
- Rule: BRD-03
- Evidence: `src/styles/base.css:3`, `src/components/Hero.tsx:4`, `src/components/Card.tsx:9`
- Facts: Three files set `font-family: Inter`. The guide gives Manrope for the body.
- Fix: Use `var(--font-body)` in the three files.
- Guard: Set `theme.fontFamily` in `tailwind.config.js` to the fonts of the brand only.
- Guard status: proposed
- Status: open
```

- A new finding gets the next free `B` number.
- A finding that is already in the file gets the new `Evidence` lines.
- A finding that the code no longer has gets `Status: closed`; the entry stays.
- Each `grave` finding has a `Guard` and a `Guard status`: `proposed`,
  `applied`, or `declined: <reason of the human>`. A declined guard stays
  declined; the next run proposes no guard for that finding.

## Guards

A guard is a change of a rule, a linter, or a check that stops a deviation.
Pick the guard that acts earliest:

| Cause | Guard |
|---|---|
| The theme holds off-brand values or extends the default palette | Set `theme.colors`, `theme.fontFamily`, and `theme.borderRadius` of `tailwind.config.*` (in `theme`, not `theme.extend`) to the values of `tokens.json`, so a class off the brand has no name |
| A literal value in a stylesheet | stylelint: `color-no-hex`, `color-named: never`, and `declaration-property-value-allowed-list` for `font-family` and `border-radius` with the `var(--brand-*)` and `var(--font-*)` values |
| A literal value in a JSX or TS style | ESLint `no-restricted-syntax` with a selector for a hex string in a `style` or `sx` property |
| The name in many files | One constant or one i18n key for the name, and each file reads it |
| The agent writes off-brand code | `.claude/rules/brand.md` as the brand-builder skill writes it, and the line of `AGENTS.md` that names `docs/brand/` |
| A rule or skill of the project contradicts the brand | The change of the line of that rule or skill |
| No check runs before a merge | Copy `<skill>/tools/brand-lint` to `docs/brand/brand-lint`, and add a CI step: `python3 docs/brand/brand-lint --workspace .` |
| The guide is silent, vague, or wrong on the case | A new or changed `BRD` rule, through the brand-builder skill |
| A real exception, such as a vendor widget or a legacy page | An entry in `lint` of `tokens.json`, with its reason in the guide |
| brand-lint misses or misreads the pattern | An issue on the repository of `metadata.source`, with the line that it misread |

A guard changes only after the human approves it.

## Flow

```lnl
START:
  ASK   does the message approve or decline the guards that an earlier turn showed?
  JUMP  APPLY IF yes
  ASK   does docs/brand/tokens.json exist?
  STOP  tell the human to build the brand with the brand-builder skill first IF no
  DO    read docs/brand/README.md, docs/brand/tokens.json, and reports/brand-check.md when it exists
  DO    run <skill>/tools/brand-lint on the paths of the request, or on the workspace, with --workspace <workspace>
  DO    confirm each BL-NAME finding by reading its line, and drop each one in a field that rejects diacritics
  DO    apply the review check to the code, the assets, and the copy of the scope
  DO    apply the rules check to the files that tell an agent, a linter, or a build how to write the UI
  DO    write each finding to reports/brand-check.md with its severity, rule, evidence, facts, and fix
GUARDS:
  DO    write a guard from the table of guards to each grave finding that has no guard status
  ASK   does a grave finding hold a guard with Guard status: proposed?
  STOP  show each proposed guard with its finding, and ask the human to approve or decline each one IF yes
  JUMP  REVIEW
APPLY:
  DO    apply each approved guard and write Guard status: applied
  DO    write Guard status: declined with the reason of the human to each declined guard
  DO    run <skill>/tools/brand-lint again on the paths of the applied guards
  JUMP  REVIEW
REVIEW:
  CHECK each finding names a BRD rule or a row of the rules check, evidence with file:line, and a fix
  CHECK each grave finding has a guard and a guard status
  CHECK each finding keeps its B number, and each new finding takes the next free number
  CHECK each applied guard had the approval of the human
  CHECK each entry of lint in tokens.json has its reason in docs/brand/README.md
  CHECK reports/brand-check.md passes the checks of the write-md skill
REPLY:
  SAY   the open findings by severity, the grave findings with their guards, and the guards applied or declined
  END
```

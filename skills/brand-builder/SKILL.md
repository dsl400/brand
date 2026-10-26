---
name: brand-builder
description: Use when the user asks to create a brand or identity, to import a brand package or guide into the project, or to change the brand rules in docs/brand/.
metadata:
  source: https://github.com/dsl400/brand
  version: 0.1.0
---

# brand-builder

The brand of a project lives in `<workspace>/docs/brand/`. The code, the
agents, and the brand-check skill read it from there.

`<workspace>` is the root of the project that holds `docs/`.

## Sources

| Request | Mode |
|---|---|
| A brand package or a guide: a folder, a PDF, a ZIP, a URL | Import: list its directions, write the chosen one to `docs/brand/` |
| A brief, or a request to create a brand | Create: write three directions, write the chosen one to `docs/brand/` |
| A change of the brand in `docs/brand/` | Change: edit the rules and the tokens, keep each `BRD` number |

The brand takes one direction: one mark, one palette, one set of fonts. An
import or a create over an existing `docs/brand/` replaces it after the
human confirms.

## The choice file

`docs/brand/directions.md` holds the directions between the turn that lists
them and the turn where the human chooses. Each direction is one section:

```markdown
# Directions

Source: /home/user/Downloads/Brand_Package/

## Datum
- Idea: A datum is the reference from which a system is measured.
- Best fit: systems architecture and technical advisory.
- Folder: 01_datum/
```

In create mode, each section also holds the positioning line, the voice, a
headline, the palette (five hex values with their roles), the fonts
(display, body, utility), and the mark: an SVG in `docs/brand/directions/`.
The three directions differ in idea, palette, and type.

## The brief

Create mode needs these answers:

- The owner: the person or the company, and the name exactly as written,
  with its diacritics.
- The roles and the offer.
- The audience and the decision the audience makes.
- The tone: three words.
- The constraints: marks to keep, languages, media (web, print, slides).

Each fact of the guide comes from the brief or the package. The guide holds
no invented project, client, or contact detail.

## The folder

```
docs/brand/
  README.md        the guide: idea, voice, the BRD rules, the lint exceptions
  tokens.json      the values that the code and brand-lint read
  brand.css        @font-face and the :root variables
  logos/           editable/ with live text, outlined/ with text as paths, png/
  fonts/           the TTF files and their licenses
```

### tokens.json

```json
{
  "brand": "Andrei Drăgan",
  "names": { "standard": "Andrei Drăgan", "ascii": "Andrei Dragan" },
  "colors": {
    "ink": "#172623",
    "paper": "#F1F0E8",
    "accent": "#D85635",
    "secondary": "#C2C9BD",
    "muted": "#56655E"
  },
  "typography": {
    "display": "Space Grotesk",
    "display_weight": 600,
    "body": "Manrope",
    "utility": "IBM Plex Mono"
  },
  "spacing_px": [4, 8, 12, 16, 24, 32, 48, 64, 96],
  "corner_radius_px": 0,
  "motion_duration_ms": 240,
  "contrast_min": 4.5,
  "lint": { "allow_colors": [], "allow_fonts": [], "allow_radius": [], "exclude": [] }
}
```

- `colors` maps each role to a hex value.
- `names.ascii` is present when the standard name has a character that some
  systems reject.
- `contrast_min` is 4.5, the WCAG AA ratio for body text, unless the guide
  gives a higher one.
- `lint` holds the exceptions of brand-lint: colors (hex or CSS names),
  fonts, radius values, and `exclude` globs from the workspace root (`**/`
  for any depth). Each entry has its reason in the section `Lint exceptions`
  of the guide.

An imported package has its own shape. Map it:

| Package | tokens.json |
|---|---|
| A palette as an object or a list | `colors` as a flat map of role to hex |
| A table of contrast ratios | `contrast_min` from the lowest ratio the guide permits for text, or 4.5 |
| An ASCII lockup or an ASCII spelling of the name | `names.ascii` |
| Font URLs relative to the package (`../fonts/`) | `fonts/` |

### brand.css

```css
@font-face { font-family: 'Manrope'; src: url('fonts/Manrope.ttf') format('truetype'); font-weight: 100 900; font-display: swap; }
:root {
  --brand-ink: #172623;
  --brand-accent: #D85635;
  --font-body: 'Manrope', sans-serif;
  --brand-radius: 0px;
}
```

One variable for each color, each font role, and the radius. `brand.css`
holds the values of `tokens.json` and one generic fallback for each font
role.

### README.md

```markdown
# Brand: Andrei Drăgan

## Idea
A datum is the reference from which a system is measured. …

## Voice
Exact, composed, decisive. Short statements. Name the constraint, explain the
decision, show the result.

| Off-brand | On-brand |
|---|---|
| We leverage cutting-edge solutions. | I find the constraint first, then build. |

## Rules
- **BRD-01** — Each color of the interface must come from the palette of
  `tokens.json`. Check: brand-lint
- **BRD-02** — Body text must reach a contrast of 4.5:1 or more on its
  background. Check: review
- **BRD-03** — The name must take the form `Andrei Drăgan`, except in a
  field that rejects diacritics, where it takes `Andrei Dragan`. Check: brand-lint
- **BRD-04** — Each use of the logo must come from `docs/brand/logos/`, with
  clear space equal to the height of the symbol. Check: review

## Lint exceptions
- `Arial` in `allow_fonts`: the email signature needs a font that each mail
  client has.
```

- A rule is one sentence with one obligation word: `must` or `should`.
- Each rule ends with `Check: brand-lint` when brand-lint reads its value
  (color, font, radius, name), else `Check: review`.
- A new rule gets the next free number. A removed rule keeps its number
  retired.
- IF `docs/reference/README.md` exists, THEN add the prefix `BRD` with
  `../brand/README.md` to its prefix table.

## Fonts and logos

- Import: copy the TTF files and their license files of the chosen direction
  to `docs/brand/fonts/`, and its logo masters to `docs/brand/logos/`.
- Create: choose fonts under the SIL Open Font License. Download each TTF
  and its `OFL.txt` from `https://github.com/google/fonts/tree/main/ofl/<family>/`,
  where `<family>` is the name in lower case with no spaces (`spacegrotesk`).
- Create: write the mark as SVG in `logos/editable/`. Install the fonts, then
  outline the text into `logos/outlined/`:

  ```sh
  inkscape <in.svg> --export-text-to-path --export-plain-svg -o <out.svg>
  ```

  IF Inkscape is absent, THEN keep `logos/outlined/` empty and name the gap
  in the reply.

## Integration

- Copy `brand.css` and `fonts/` together into the public folder of the
  project (`public/brand/`, `static/brand/`), so the relative font URLs hold.
  Link the copy, or map its variables into the theme of the project: set
  `theme.colors`, `theme.fontFamily`, and `theme.borderRadius` of Tailwind,
  or the token file of the design system.
- Write `.claude/rules/brand.md` in the project:

  ```markdown
  ---
  paths:
    - "**/*.{css,scss,html,jsx,tsx,vue,svelte,svg}"
  ---

  # brand

  WHEN you write or edit a UI file, use the variables of `docs/brand/brand.css`
  and the rules of `docs/brand/README.md`, then run the brand-check skill on
  the files you changed.
  ```

- Add one line to `AGENTS.md`: `The brand lives in docs/brand/; the
  brand-check skill checks it.`

## Flow

```lnl
START:
  ASK   does docs/brand/directions.md exist, and does the message choose one of its directions?
  JUMP  WRITE IF yes
  ASK   does the request ask to change the brand of docs/brand/?
  JUMP  CHANGE IF yes
  ASK   does docs/brand/tokens.json exist?
  JUMP  SOURCE IF no
  ASK   does the message confirm that the new brand replaces docs/brand/?
  STOP  show the brand of docs/brand/ and ask the human to confirm its replacement IF no
SOURCE:
  ASK   does the request give a brand package or a guide?
  JUMP  IMPORT IF yes
BRIEF:
  ASK   does the conversation hold each answer of the brief?
  STOP  ask the human for each missing answer of the brief IF no
  DO    write three directions to docs/brand/directions.md, each with its mark in docs/brand/directions/
  ASK   does docs/brand/directions.md hold three directions?
  STOP  show the three directions and ask the human to choose one IF yes
  STOP  show the error of the write and ask the human how to continue IF no
IMPORT:
  DO    read the package or the guide, and write the source and each direction to docs/brand/directions.md
  ASK   does the package hold more than one direction?
  JUMP  WRITE IF no
  ASK   does the message name the direction to import?
  JUMP  WRITE IF yes
  STOP  list the directions with their best fit, and ask the human to choose one IF no
CHANGE:
  ASK   does docs/brand/tokens.json exist?
  STOP  tell the human that the project has no brand, and ask for a package, a guide, or a brief IF no
  DO    edit the rules and the tokens that the request names, in docs/brand/README.md and docs/brand/tokens.json
  DO    rewrite brand.css, its public copy, and the theme mapping from tokens.json
  JUMP  REVIEW
WRITE:
  DO    write tokens.json in the shape of this skill, with the map of the package when it is an import
  DO    write brand.css and README.md from tokens.json and the chosen direction
  DO    write fonts/ and logos/ by the section Fonts and logos
  DO    remove docs/brand/directions.md and docs/brand/directions/
  DO    copy brand.css and fonts/ to the public folder, and map the variables in the theme of the project
  DO    write .claude/rules/brand.md, the line of AGENTS.md, and the BRD prefix of docs/reference/README.md when it exists
  JUMP  REVIEW
REVIEW:
  CHECK tokens.json, brand.css, its public copy, the theme, and README.md hold the same values
  CHECK each BRD rule is one sentence with one obligation word and ends with Check: brand-lint or Check: review
  CHECK each BRD rule keeps its number, and each new rule takes the next free number
  CHECK each entry of lint in tokens.json has its reason in the section Lint exceptions
  CHECK each font of tokens.json has its TTF and its license in docs/brand/fonts/
  CHECK logos/outlined/ holds an SVG with text as paths for each master, or the reply names the gap
  CHECK each fact of the guide comes from the brief or the package
  CHECK docs/brand/README.md passes the checks of the write-md skill
REPLY:
  SAY   the direction written, the files of docs/brand/, the integration done, the gaps, and the next step: run the brand-check skill
  END
```

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).parent / "brand-lint"

TOKENS = {
    "brand": "Andrei Drăgan",
    "names": {"standard": "Andrei Drăgan", "ascii": "Andrei Dragan"},
    "colors": {"ink": "#172623", "paper": "#F1F0E8", "accent": "#D85635"},
    "typography": {"display": "Space Grotesk", "display_weight": 600, "body": "Manrope"},
    "corner_radius_px": 0,
    "lint": {"allow_colors": ["#FFFFFF"], "allow_radius": ["50%"], "exclude": ["legacy/**"]},
}


def run(files, tokens=TOKENS, git=False, args=()):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        if tokens is not None:
            (root / "docs/brand").mkdir(parents=True)
            (root / "docs/brand/tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text, encoding="utf-8")
        if git:
            subprocess.run(["git", "init", "-q", d], check=True)
        r = subprocess.run([sys.executable, "-I", str(TOOL), *[a.replace("{ws}", d) for a in args],
                            "--workspace", d, "--json"], capture_output=True, text=True)
        return r.returncode, json.loads(r.stdout or "[]")


def rules(files, **kw):
    return [f["rule"] for f in run(files, **kw)[1]]


class Colors(unittest.TestCase):
    def test_palette_passes(self):
        self.assertEqual(run({"a.css": "a{color:#172623;background:#f1f0e8;border-color:#fff}"}), (0, []))

    def test_short_hex_and_alpha_normalize(self):
        self.assertEqual(rules({"a.css": "a{color:#FFFF;background:#172623cc}"}), [])

    def test_outside_palette(self):
        self.assertEqual(rules({"a.css": "a{color:#ff0000;fill:rgb(1,2,3);stroke:hsl(0,100%,50%)}"}),
                         ["BL-COLOR"] * 3)

    def test_rgb_of_palette_passes(self):
        self.assertEqual(rules({"a.css": "a{color:rgb(23, 38, 35)}"}), [])

    def test_named_colors(self):
        self.assertEqual(rules({"a.css": "a{color:tomato;background:white;fill:none}"}), ["BL-COLOR"])
        self.assertEqual(rules({"a.svg": '<rect fill="red"/>'}), ["BL-COLOR"])

    def test_ids_links_and_selectors(self):
        html = '<a href="#add" id="#abc"></a><a href="/s?q=1#cafe"></a><rect fill="url(#bad)"/>'
        self.assertEqual(rules({"a.html": html}), [])
        self.assertEqual(rules({"a.css": "#fade { color: #172623; }\n#add,\n#bad { x: y }"}), [])
        self.assertEqual(rules({"a.ts": "document.querySelector('#add')"}), [])

    def test_markdown_needs_a_color_key_before_the_hex(self):
        self.assertEqual(rules({"a.md": "See issue #123 and [x](#abc)."}), [])
        self.assertEqual(rules({"a.md": "Color: see issue #123."}), [])
        self.assertEqual(rules({"a.md": "#00ff00 then the word color"}), [])
        self.assertEqual(rules({"a.md": "The accent color is #00ff00."}), ["BL-COLOR"])

    def test_tailwind_and_yaml(self):
        self.assertEqual(rules({"a.tsx": '<div className="bg-[#123456]" />'}), ["BL-COLOR"])
        self.assertEqual(rules({"a.yml": "primary: '#123456'"}), ["BL-COLOR"])


class Fonts(unittest.TestCase):
    def test_stack(self):
        self.assertEqual(rules({"a.css": "a{font-family:'Manrope', sans-serif}"}), [])
        self.assertEqual(rules({"a.css": "a{font-family:Inter, sans-serif}"}), ["BL-FONT"])
        self.assertEqual(rules({"a.css": "a{font-family:var(--font-body)}"}), [])

    def test_multiline_and_important(self):
        self.assertEqual(run({"a.css": 'a{\n  font-family:\n    "Inter" !important,\n    sans-serif;\n}'})[1][0]["message"],
                         "font 'Inter' is not in the typography of the brand")
        self.assertEqual(rules({"a.css": 'a{font-family:"Manrope" !important}'}), [])

    def test_inline_style_and_svg_attribute(self):
        found = run({"a.html": '<div style="font-family: Arial">x</div>'})[1]
        self.assertEqual([f["message"] for f in found], ["font 'Arial' is not in the typography of the brand"])
        self.assertEqual(rules({"a.svg": "<text font-family=\"'Space Grotesk', sans-serif\">A</text>"}), [])
        self.assertEqual(rules({"a.svg": '<text font-family="Inter">A</text>'}), ["BL-FONT"])

    def test_shorthand(self):
        self.assertEqual(rules({"a.css": "a{font: 600 1rem/1.5 Inter, sans-serif}"}), ["BL-FONT"])
        self.assertEqual(rules({"a.css": "a{font: 1rem Manrope}"}), [])

    def test_js(self):
        self.assertEqual(rules({"a.tsx": "const s = { fontFamily: 'Roboto', borderRadius: 0 }"}), ["BL-FONT"])
        self.assertEqual(rules({"a.ts": "const s = { fontFamily: \"'Manrope', sans-serif\" }"}), [])
        cfg = "module.exports = { theme: { fontFamily: { sans: ['Inter', 'sans-serif'], 'mono': ['Manrope'] } } }"
        self.assertEqual(rules({"tailwind.config.js": cfg}), ["BL-FONT"])

    def test_google_fonts_and_tailwind(self):
        link = '<link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400&amp;family=Manrope">'
        self.assertEqual(run({"a.html": link})[1][0]["message"], "font 'Roboto Slab' is not in the typography of the brand")
        self.assertEqual(rules({"a.tsx": '<p className="font-[Inter] font-[600]" />'}), ["BL-FONT"])


class Radius(unittest.TestCase):
    def test_values(self):
        self.assertEqual(rules({"a.css": "a{border-radius:0;border-radius:50%;border-radius:inherit}"}), [])
        self.assertEqual(rules({"a.css": "a{border-radius:8px}"}), ["BL-RADIUS"])
        self.assertEqual(rules({"a.css": "a{border-radius:0 0 8px 8px}"}), ["BL-RADIUS"])

    def test_functions_and_important(self):
        self.assertEqual(rules({"a.css": "a{border-radius:calc(2px + 1px);border-radius:var(--brand-radius)}"}), [])
        self.assertEqual(rules({"a.css": "a{border-radius:0 !important}"}), [])

    def test_logical_js_and_tailwind(self):
        self.assertEqual(rules({"a.css": "a{border-start-start-radius:4px}"}), ["BL-RADIUS"])
        self.assertEqual(rules({"t.js": "x = { borderRadius: { md: '8px' } }"}), ["BL-RADIUS"])
        self.assertEqual(rules({"a.tsx": "s = { borderRadius: 8 }"}), ["BL-RADIUS"])
        self.assertEqual(rules({"a.tsx": '<b className="rounded-[6px] rounded-t-[0px]" />'}), ["BL-RADIUS"])


class Name(unittest.TestCase):
    def test_ascii_form_any_case(self):
        self.assertEqual(rules({"a.html": "<h1>Andrei Dragan</h1><p>ANDREI DRAGAN</p>"}), ["BL-NAME"] * 2)
        self.assertEqual(rules({"a.html": "<h1>Andrei Drăgan</h1>"}), [])

    def test_slug_and_email_pass(self):
        self.assertEqual(rules({"a.md": "andrei-dragan.ro, andrei.dragan@x.ro, /andrei-dragan/"}), [])


class Files(unittest.TestCase):
    def test_allow_comment_and_exclude(self):
        self.assertEqual(rules({"a.css": "a{color:#123456} /* brand-lint: allow */"}), [])
        self.assertEqual(rules({"legacy/a.css": "a{color:#123456}"}), [])

    def test_dependency_folders_at_any_depth(self):
        files = {"packages/app/node_modules/x/a.css": "a{color:#123456}",
                 "packages/app/dist/a.css": "a{color:#123456}",
                 "packages/app/src/a.css": "a{color:#123456}"}
        self.assertEqual(rules(files), ["BL-COLOR"])

    def test_gitignore(self):
        files = {".gitignore": "gen/\n", "gen/a.css": "a{color:#123456}", "src/a.css": "a{color:#654321}"}
        self.assertEqual([f["path"] for f in run(files, git=True)[1]], ["src/a.css"])

    def test_one_star_stays_in_its_folder(self):
        tokens = dict(TOKENS, lint={"exclude": ["*.css"]})
        self.assertEqual(rules({"a.css": "a{color:#123456}", "src/b.css": "a{color:#123456}"}, tokens=tokens),
                         ["BL-COLOR"])

    def test_path_outside_workspace(self):
        self.assertEqual(run({"a.css": "a{}"}, args=["/"])[0], 2)

    def test_missing_or_invalid_tokens(self):
        self.assertEqual(run({"a.css": "a{}"}, tokens=None)[0], 2)
        self.assertEqual(run({"a.css": "a{}"}, tokens={"colors": {"ink": "rgb(1,2,3)"}})[0], 2)

    def test_color_objects_in_tokens(self):
        tokens = dict(TOKENS, colors={"ink": {"value": "#172623"}})
        self.assertEqual(rules({"a.css": "a{color:#172623}"}, tokens=tokens), [])


if __name__ == "__main__":
    unittest.main()

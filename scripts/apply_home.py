"""Inject custom/home.svg into image-assets.js as DEMO_HOME. Idempotent."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
assets = root / "image-assets.js"
svg = (root / "custom" / "home.svg").read_text(encoding="utf-8").strip()

if "'" in svg:
    sys.exit("home.svg must not contain single quotes")

src = assets.read_text(encoding="utf-8")
new, n = re.subn(r"export const DEMO_HOME = '.*?';",
                 lambda m: f"export const DEMO_HOME = '{svg}';", src, flags=re.S)
if n != 1:
    sys.exit(f"Expected exactly one DEMO_HOME, found {n} - upstream format changed?")

if new != src:
    assets.write_text(new, encoding="utf-8")
    print("DEMO_HOME replaced")
else:
    print("DEMO_HOME already up to date")

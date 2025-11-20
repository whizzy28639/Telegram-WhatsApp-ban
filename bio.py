#!/usr/bin/env python3
"""
bio.py — small utility to store & print a personal bio.

Features:
- Holds structured bio data (name, role, skills, interests, contact)
- Print pretty to console, export to JSON or Markdown
- Safe defaults; edit fields below to personalize
"""

from dataclasses import dataclass, asdict, field
import json
import argparse
import textwrap
from datetime import date
from typing import List

@dataclass
class Bio:
    name: str = "Tizzy Whizzy"
    title: str = "Cybersecurity Instructor & Developer"
    location: str = "Nigeria"
    about: str = field(default_factory=lambda: (
        "I teach and build security tooling, focusing on practical, hands-on "
        "work with Termux, Python, and automation. I like making learning "
        "fun—sometimes with playful 'fake hacking' demos—and I value simple, "
        "secure defaults (passwords > fingerprints for some use cases)."
    ))
    skills: List[str] = field(default_factory=lambda: [
        "Python", "Bash/Termux", "Git/GitHub", "Network & App Security",
        "Scripting & Automation", "Teaching / Mentoring"
    ])
    hobbies: List[str] = field(default_factory=lambda: [
        "Teaching", "Building tools", "Trying new terminals", "Tinkering"
    ])
    contact: dict = field(default_factory=lambda: {
        "email": "",
        "github": ""
    })
    since: int = date.today().year

    def pretty(self) -> str:
        """Return a human-friendly formatted bio."""
        skills_line = ", ".join(self.skills)
        hobbies_line = ", ".join(self.hobbies)
        contact_lines = []
        if self.contact.get("email"):
            contact_lines.append(f"Email: {self.contact['email']}")
        if self.contact.get("github"):
            contact_lines.append(f"GitHub: {self.contact['github']}")
        contact_block = "\n".join(contact_lines) if contact_lines else "Contact: (not provided)"
        block = f"""
{self.name}
{self.title} — since {self.since}
Location: {self.location}

About
{self._indent(self.about, 2)}

Skills
  {skills_line}

Hobbies
  {hobbies_line}

{contact_block}
""".strip()
        return block

    def to_json(self) -> str:
        """Return pretty JSON representation."""
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Return markdown representation suitable for README or profile."""
        md = [
            f"# {self.name}",
            f"**{self.title}**  ",
            f"*Location:* {self.location}  ",
            "",
            "## About",
            self.about,
            "",
            "## Skills",
            ", ".join(self.skills),
            "",
            "## Hobbies",
            ", ".join(self.hobbies),
            "",
        ]
        if self.contact.get("github") or self.contact.get("email"):
            md += ["## Contact"]
            if self.contact.get("github"):
                md.append(f"- GitHub: `{self.contact['github']}`")
            if self.contact.get("email"):
                md.append(f"- Email: {self.contact['email']}")
        return "\n".join(md)

    @staticmethod
    def _indent(text: str, n: int) -> str:
        pad = " " * n
        return "\n".join(pad + line for line in textwrap.fill(text, width=72).splitlines())

def main():
    parser = argparse.ArgumentParser(description="Print or export a personal bio.")
    parser.add_argument("--format", "-f", choices=["text", "json", "md"], default="text",
                        help="Output format")
    parser.add_argument("--out", "-o", type=str, default=None,
                        help="Write output to file (instead of stdout)")
    args = parser.parse_args()

    # Create a default bio instance — edit fields here if you want
    bio = Bio(
        name="Tizzy Whizzy",
        title="Cybersecurity Instructor & Developer",
        location="Nigeria",
        about=(
            "I teach practical cybersecurity with a focus on hands-on tooling, "
            "automation, and Termux-based workflows. I enjoy making learning "
            "playful and accessible for others."
        ),
        skills=["Python", "Bash/Termux", "Git/GitHub", "Security Tools", "Scripting"],
        hobbies=["Teaching", "Building tools", "Tinkering with terminals"],
        contact={"email": "", "github": "https://github.com/your-username"},
        since=2018
    )

    if args.format == "text":
        out = bio.pretty()
    elif args.format == "json":
        out = bio.to_json()
    else:  # md
        out = bio.to_markdown()

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"Wrote bio to {args.out}")
    else:
        print(out)

if __name__ == "__main__":
    main()

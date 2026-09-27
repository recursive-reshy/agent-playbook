from prompt_chaining.llm import complete_structured, complete_text
from prompt_chaining.models import Outline

def generate_outline( topic: str ) -> Outline:
    system = (
        "You are an experienced blog editor. You plan clear, "
        "well-structured blog posts for a general technical audience."
    )

    prompt = (
        f"Create an outline for a blog post about: {topic}\n\n"
        "Requirements:\n"
        "- A compelling title\n"
        "- Between 3 and 6 sections\n"
        "- Each section has 2-4 key points\n"
        "- Sections should flow logically from introduction to conclusion"
    )

    return complete_structured( prompt, system, Outline )

def format_outline( outline: Outline ) -> str:
    lines = [ f"# {outline.title}" ]

    for section in outline.sections:
        lines.append( f"\n## {section.heading}" )
        for point in section.key_points:
            lines.append( f"- {point}" )

    return "\n".join( lines )

def write_draft( topic: str, outline: Outline ) -> str:
    system = (
        "You are a skilled technical writer. You turn outlines into "
        "complete, engaging blog posts in markdown."
    )

    prompt = (
        f"Write a blog post about: {topic}\n\n"
        f"Follow this outline exactly:\n<outline>\n{format_outline(outline)}\n</outline>\n\n"
        "Cover every key point. Use the outline's title and section headings. "
        "Output only the blog post in markdown."
    )

    return complete_structured( prompt, system )

def polish( draft: str ) -> str:
    system = (
        "You are a meticulous copy editor. You improve clarity and flow "
        "without changing the meaning or structure of a piece."
    )

    prompt = (
        f"Edit this blog post:\n<draft>\n{draft}\n</draft>\n\n"
        "- Tighten wordy sentences\n"
        "- Smooth transitions between sections\n"
        "- Fix grammar and awkward phrasing\n"
        "- Keep all headings and the overall structure\n\n"
        "Output only the edited post in markdown."
    )

    return complete_structured( prompt, system )
import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_PATH = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/colang_rule_snippet_2.png"

# Canvas dimensions (2x Retina)
WIDTH = 1800
HEIGHT = 960
PADDING = 40

# Create high-res image
img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Card bounding box
card_x0 = PADDING
card_y0 = PADDING
card_x1 = WIDTH - PADDING
card_y1 = HEIGHT - PADDING
card_radius = 24

# Outer drop shadow (layered soft alpha)
for offset, alpha in [(12, 25), (8, 40), (4, 60)]:
    draw.rounded_rectangle(
        [(card_x0 - offset, card_y0 - offset + 8), (card_x1 + offset, card_y1 + offset + 8)],
        radius=card_radius + offset,
        fill=(15, 23, 42, alpha)
    )

# Main Card Body (Deep VS Code Dark / Slate 950)
draw.rounded_rectangle(
    [(card_x0, card_y0), (card_x1, card_y1)],
    radius=card_radius,
    fill=(15, 23, 42, 255), # #0F172A
    outline=(51, 65, 85, 255), # #334155
    width=3
)

# Header Bar (Dark Slate 900)
header_h = 90
draw.rounded_rectangle(
    [(card_x0, card_y0), (card_x1, card_y0 + header_h + 20)],
    radius=card_radius,
    fill=(30, 41, 59, 255) # #1E293B
)
# Flatten bottom of header
draw.rectangle(
    [(card_x0, card_y0 + header_h), (card_x1, card_y0 + header_h + 20)],
    fill=(30, 41, 59, 255)
)
draw.line(
    [(card_x0, card_y0 + header_h + 20), (card_x1, card_y0 + header_h + 20)],
    fill=(51, 65, 85, 255),
    width=2
)

# macOS Window Control Dots
dot_y = card_y0 + 55
draw.ellipse([(card_x0 + 45, dot_y - 14), (card_x0 + 73, dot_y + 14)], fill=(239, 68, 68, 255)) # Close
draw.ellipse([(card_x0 + 90, dot_y - 14), (card_x0 + 118, dot_y + 14)], fill=(245, 158, 11, 255)) # Minimize
draw.ellipse([(card_x0 + 135, dot_y - 14), (card_x0 + 163, dot_y + 14)], fill=(16, 185, 129, 255)) # Maximize

# Fonts
font_code_path = "/System/Library/Fonts/Menlo.ttc"
font_code = ImageFont.truetype(font_code_path, 34, index=0)
font_code_bold = ImageFont.truetype(font_code_path, 34, index=1)
font_title = ImageFont.truetype(font_code_path, 28, index=1)
font_badge = ImageFont.truetype(font_code_path, 22, index=1)
font_footer = ImageFont.truetype(font_code_path, 24, index=0)

# Header Title & Icon
title_text = "rules/block_dan_roleplay_jailbreak.co"
draw.text((card_x0 + 200, card_y0 + 40), title_text, fill=(226, 232, 240, 255), font=font_title)

# Header Right Badge
badge_w = 340
badge_h = 44
badge_x1 = card_x1 - 40
badge_x0 = badge_x1 - badge_w
badge_y0 = card_y0 + 33
draw.rounded_rectangle(
    [(badge_x0, badge_y0), (badge_x1, badge_y0 + badge_h)],
    radius=10,
    fill=(22, 101, 52, 255), # Dark Emerald
    outline=(34, 197, 94, 255),
    width=2
)
draw.text((badge_x0 + 25, badge_y0 + 10), "● ACTIVE RAIL (+10.4s)", fill=(240, 253, 244, 255), font=font_badge)

# Code Lines Definition
lines = [
    [
        ("01", (100, 116, 139)),
        ("  # Autonomous Synthesized Rail (Taxonomy S3: Role-Play Hijack)", (148, 163, 184))
    ],
    [
        ("02", (100, 116, 139)),
        ("  define flow ", (244, 63, 94)), # Rose keyword
        ("block_dan_roleplay_jailbreak", (251, 191, 36)) # Amber flow name
    ],
    [
        ("03", (100, 116, 139)),
        ("    user ", (56, 189, 248)), # Sky blue role
        ("prompts unconstrained persona or jailbreak override", (167, 243, 208)) # Mint green
    ],
    [
        ("04", (100, 116, 139)),
        ("    $verdict", (147, 197, 253)), # Light blue variable
        (" = ", (226, 232, 240)),
        ("execute ", (244, 63, 94)), # Rose keyword
        ("classify_threat_intent(history)", (251, 191, 36)) # Amber function
    ],
    [
        ("05", (100, 116, 139)),
        ("    when ", (244, 63, 94)), # Rose keyword
        ("$verdict == 'UNSAFE'", (252, 165, 165)) # Soft red condition
    ],
    [
        ("06", (100, 116, 139)),
        ("      bot ", (56, 189, 248)), # Role
        ("trap_session_sticky_quarantine(:9100)", (252, 165, 165)) # Soft coral target
    ],
    [
        ("07", (100, 116, 139)),
        ("      stop", (244, 63, 94)) # Rose stop
    ]
]

# Draw Code Lines
code_start_y = card_y0 + header_h + 60
line_height = 80

for line_idx, tokens in enumerate(lines):
    curr_y = code_start_y + line_idx * line_height
    
    # Line number
    ln_str, ln_color = tokens[0]
    draw.text((card_x0 + 45, curr_y), ln_str, fill=ln_color, font=font_code)
    
    # Divider line after line numbers
    draw.line(
        [(card_x0 + 115, card_y0 + header_h + 30), (card_x0 + 115, card_y1 - 80)],
        fill=(51, 65, 85, 200),
        width=2
    )
    
    # Token segments
    curr_x = card_x0 + 140
    for text_segment, color in tokens[1:]:
        draw.text((curr_x, curr_y), text_segment, fill=color, font=font_code_bold)
        # Advance x coordinate
        bbox = draw.textbbox((curr_x, curr_y), text_segment, font=font_code_bold)
        curr_x += (bbox[2] - bbox[0])

# Bottom Footer Status Bar
footer_y0 = card_y1 - 70
draw.line([(card_x0, footer_y0), (card_x1, footer_y0)], fill=(51, 65, 85, 255), width=2)

draw.text((card_x0 + 45, footer_y0 + 20), "NVIDIA NeMo Guardrails (Colang 2.0)", fill=(148, 163, 184, 255), font=font_footer)
draw.text((card_x0 + 720, footer_y0 + 20), "• Synthesis Latency: 10.4s", fill=(251, 191, 36, 255), font=font_footer)
draw.text((card_x1 - 430, footer_y0 + 20), "• Regress Gate: 0% FP", fill=(74, 222, 128, 255), font=font_footer)

# Save final image
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
img.save(OUTPUT_PATH, "PNG")
print(f"Colang rule snippet 2 PNG successfully created at: {OUTPUT_PATH}")

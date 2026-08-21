import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_PATH = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/outcomes_milestones_card.png"

# Canvas dimensions (2x Retina Widescreen)
WIDTH = 1920
HEIGHT = 1080
PADDING = 40

# Create transparent image
img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Main Card Bounding Box
card_x0 = PADDING
card_y0 = PADDING
card_x1 = WIDTH - PADDING
card_y1 = HEIGHT - PADDING
card_radius = 24

# Outer drop shadow
for offset, alpha in [(12, 25), (8, 40), (4, 60)]:
    draw.rounded_rectangle(
        [(card_x0 - offset, card_y0 - offset + 8), (card_x1 + offset, card_y1 + offset + 8)],
        radius=card_radius + offset,
        fill=(15, 23, 42, alpha)
    )

# Main Card Body (Slate 950)
draw.rounded_rectangle(
    [(card_x0, card_y0), (card_x1, card_y1)],
    radius=card_radius,
    fill=(15, 23, 42, 255), # #0F172A
    outline=(51, 65, 85, 255), # #334155
    width=3
)

# Header Bar (Slate 900)
header_h = 100
draw.rounded_rectangle(
    [(card_x0, card_y0), (card_x1, card_y0 + header_h + 20)],
    radius=card_radius,
    fill=(30, 41, 59, 255) # #1E293B
)
draw.rectangle(
    [(card_x0, card_y0 + header_h), (card_x1, card_y0 + header_h + 20)],
    fill=(30, 41, 59, 255)
)
draw.line(
    [(card_x0, card_y0 + header_h + 20), (card_x1, card_y0 + header_h + 20)],
    fill=(51, 65, 85, 255),
    width=2
)

# macOS Window Controls
dot_y = card_y0 + 60
draw.ellipse([(card_x0 + 45, dot_y - 14), (card_x0 + 73, dot_y + 14)], fill=(239, 68, 68, 255))
draw.ellipse([(card_x0 + 90, dot_y - 14), (card_x0 + 118, dot_y + 14)], fill=(245, 158, 11, 255))
draw.ellipse([(card_x0 + 135, dot_y - 14), (card_x0 + 163, dot_y + 14)], fill=(16, 185, 129, 255))

# Fonts
font_code_path = "/System/Library/Fonts/Menlo.ttc"
font_title = ImageFont.truetype(font_code_path, 34, index=1)
font_badge = ImageFont.truetype(font_code_path, 22, index=1)
font_stat_big = ImageFont.truetype(font_code_path, 54, index=1)
font_card_title = ImageFont.truetype(font_code_path, 25, index=1)
font_card_sub = ImageFont.truetype(font_code_path, 20, index=1)
font_card_body = ImageFont.truetype(font_code_path, 21, index=0)
font_footer = ImageFont.truetype(font_code_path, 22, index=0)

# Header Title
draw.text((card_x0 + 200, card_y0 + 42), "HONEY-LLM: KEY OUTCOMES & EMPIRICAL MILESTONES", fill=(241, 245, 249, 255), font=font_title)

# Header Right Badge
badge_w = 360
badge_h = 46
badge_x1 = card_x1 - 40
badge_x0 = badge_x1 - badge_w
badge_y0 = card_y0 + 38
draw.rounded_rectangle(
    [(badge_x0, badge_y0), (badge_x1, badge_y0 + badge_h)],
    radius=10,
    fill=(22, 101, 52, 255),
    outline=(34, 197, 94, 255),
    width=2
)
draw.text((badge_x0 + 20, badge_y0 + 11), "● PHASES 1–4 VERIFIED", fill=(240, 253, 244, 255), font=font_badge)

# Grid Layout for 4 Cards (2x2)
grid_x0 = card_x0 + 40
grid_y0 = card_y0 + header_h + 40
grid_w = card_x1 - card_x0 - 80
grid_h = card_y1 - card_y0 - header_h - 135

card_gap_x = 35
card_gap_y = 28
single_w = (grid_w - card_gap_x) // 2
single_h = (grid_h - card_gap_y) // 2

cards_data = [
    {
        "col": 0, "row": 0,
        "title": "1. LATENCY & ROUTING EFFICIENCY",
        "stat": "~2.1 ms",
        "stat_color": (34, 197, 94), # Emerald
        "sub": "Fast-Path Latency (SLA Compliant)",
        "bullets": [
            "• Resolves benign queries without 8B model lag",
            "• Tier-0 Vector Cache + Tier-1 Sieve (~2.1ms)",
            "• 100% preservation of authentic customer experience"
        ],
        "bg": (20, 30, 48),
        "border": (30, 58, 138)
    },
    {
        "col": 1, "row": 0,
        "title": "2. THREAT DETECTION & CLASSIFICATION",
        "stat": "94.2%",
        "stat_color": (56, 189, 248), # Sky Blue
        "sub": "Ensemble Recall (500+ Vectors)",
        "bullets": [
            "• 8 Threat Taxonomy Classes (S1 Direct to S8 Hijack)",
            "• Calibrated Llama-Guard 3 8B deep inspection",
            "• Zero-escape on direct overrides & prompt dumps"
        ],
        "bg": (24, 30, 56),
        "border": (67, 56, 202)
    },
    {
        "col": 0, "row": 1,
        "title": "3. DECEPTIVE ISOLATION (SANDBOX)",
        "stat": "3.4x",
        "stat_color": (248, 113, 113), # Coral Red
        "sub": "Attacker Dwell-Time Amplification",
        "bullets": [
            "• Read-only rootfs + non-root UID (10001) execution",
            "• Strict zero-egress Docker container isolation (:9100)",
            "• Dynamic 'Sarah' persona synthetic bait generation"
        ],
        "bg": (45, 25, 35),
        "border": (185, 28, 28)
    },
    {
        "col": 1, "row": 1,
        "title": "4. CLOSED-LOOP IMMUNIZATION",
        "stat": "10.4s",
        "stat_color": (251, 191, 36), # Amber Gold
        "sub": "Automated In-Memory Time-to-Patch",
        "bullets": [
            "• NVIDIA NeMo Colang 2.0 autonomous rule synthesis",
            "• Automated Benign Regression Gate: 0% False Positives",
            "• Live in-memory hot-patching with zero service downtime"
        ],
        "bg": (42, 34, 20),
        "border": (180, 83, 9)
    }
]

for card in cards_data:
    cx0 = grid_x0 + card["col"] * (single_w + card_gap_x)
    cy0 = grid_y0 + card["row"] * (single_h + card_gap_y)
    cx1 = cx0 + single_w
    cy1 = cy0 + single_h
    
    # Card background
    draw.rounded_rectangle(
        [(cx0, cy0), (cx1, cy1)],
        radius=16,
        fill=card["bg"] + (255,),
        outline=card["border"] + (255,),
        width=2
    )
    
    # Card Header / Title
    draw.text((cx0 + 25, cy0 + 20), card["title"], fill=(226, 232, 240, 255), font=font_card_title)
    draw.line([(cx0 + 25, cy0 + 54), (cx1 - 25, cy0 + 54)], fill=card["border"] + (180,), width=1)
    
    # Big Stat & Subtitle
    stat_bbox = draw.textbbox((cx0 + 25, cy0 + 64), card["stat"], font=font_stat_big)
    draw.text((cx0 + 25, cy0 + 64), card["stat"], fill=card["stat_color"] + (255,), font=font_stat_big)
    sub_x = stat_bbox[2] + 25
    draw.text((sub_x, cy0 + 78), card["sub"], fill=(203, 213, 225, 255), font=font_card_sub)
    
    # Bullets
    bullet_start_y = cy0 + 145
    line_h = 38
    for b_idx, bullet in enumerate(card["bullets"]):
        draw.text((cx0 + 25, bullet_start_y + b_idx * line_h), bullet, fill=(226, 232, 240, 255), font=font_card_body)

# Bottom Status Footer
footer_y0 = card_y1 - 65
draw.line([(card_x0, footer_y0), (card_x1, footer_y0)], fill=(51, 65, 85, 255), width=2)

draw.text((card_x0 + 45, footer_y0 + 18), "Deliverables: NexTel Chat UI  •  SOC Threat Dashboard  •  Admin Decision Tracer", fill=(148, 163, 184, 255), font=font_footer)
draw.text((card_x1 - 420, footer_y0 + 18), "• Ready for Evaluation", fill=(74, 222, 128, 255), font=font_footer)

# Save image
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
img.save(OUTPUT_PATH, "PNG")
print(f"Outcomes milestones card PNG successfully created at: {OUTPUT_PATH}")

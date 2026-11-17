from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

font = TTFont('studio/fonts/Poppins-ExtraBold.ttf')
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()

def get_word_svg(text, target_height, start_x, baseline_y, fill_attr):
    total_h = font['hhea'].ascent - font['hhea'].descent
    scale = target_height / total_h
    current_x = start_x
    elements = []
    for ch in text:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(glyph_set)
        glyph_set[gname].draw(pen)
        d = pen.getCommands()
        adv = font['hmtx'][gname][0] * scale
        if d:
            elements.append(f'    <g transform="translate({current_x:.2f}, {baseline_y:.2f}) scale({scale:.5f}, {-scale:.5f})">\n      <path d="{d}" fill="{fill_attr}"/>\n    </g>')
        current_x += adv
    return '\n'.join(elements), current_x

shine_light, end_shine = get_word_svg('Shine', 115, 255, 152, '#FFFFFF')
cut_light, end_cut = get_word_svg('Cut', 115, end_shine + 12, 152, 'url(#textBrand)')

shine_dark, _ = get_word_svg('Shine', 115, 255, 152, '#1E140E')
cut_dark, _ = get_word_svg('Cut', 115, end_shine + 12, 152, 'url(#textBrand)')

total_w = int(end_cut + 25)

def build_svg(shine_markup, cut_markup):
    return f'''<svg width="{total_w}" height="220" viewBox="0 0 {total_w} 220" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="shineBgL" x1="0" y1="0" x2="220" y2="220" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#FFA845"/>
      <stop offset="50%" stop-color="#FF8324"/>
      <stop offset="100%" stop-color="#E55307"/>
    </linearGradient>
    <linearGradient id="starGradL" x1="50" y1="35" x2="170" y2="155" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#FFF0E3"/>
    </linearGradient>
    <linearGradient id="cutGradL" x1="85" y1="45" x2="185" y2="145" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#1E140E" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#2D1F16" stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="textBrand" x1="{end_shine:.1f}" y1="80" x2="{end_cut:.1f}" y2="160" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#FFA845"/>
      <stop offset="100%" stop-color="#FF7D20"/>
    </linearGradient>
    <filter id="softShadowL" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#802800" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Left Icon: Squircle -->
  <rect width="220" height="220" rx="54" fill="url(#shineBgL)"/>
  <rect x="2" y="2" width="216" height="216" rx="52" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="3"/>

  <!-- Left Icon: Shine and Cut Mark -->
  <g filter="url(#softShadowL)">
    <!-- Primary 4-point Star (Shine) -->
    <path d="M102 36C102 70 120 88 154 88C120 88 102 106 102 140C102 106 84 88 50 88C84 88 102 70 102 36Z" fill="url(#starGradL)"/>

    <!-- Dynamic 45-degree Precision Cut Blade -->
    <path d="M72 136L158 50L168 60L82 146Z" fill="url(#cutGradL)"/>
    <path d="M75 137L159 53" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-opacity="0.8"/>

    <!-- Modern Video / Play notch -->
    <polygon points="98,80 98,96 112,88" fill="#FF8324"/>

    <!-- Secondary Satellite Sparkle -->
    <path d="M165 125C165 140 172 147 187 147C172 147 165 154 165 169C165 154 158 147 143 147C158 147 165 140 165 125Z" fill="url(#starGradL)"/>

    <!-- Micro accent sparkle -->
    <circle cx="58" cy="152" r="4.5" fill="#FFFFFF"/>
  </g>

  <!-- Vectorized Brand Typography -->
  <g id="brand-text">
{shine_markup}
{cut_markup}
  </g>
</svg>'''

svg_light = build_svg(shine_light, cut_light)
svg_dark = build_svg(shine_dark, cut_dark)

with open('web/brand/logo-light.svg', 'w', encoding='utf-8') as f:
    f.write(svg_light)

with open('web/brand/logo.svg', 'w', encoding='utf-8') as f:
    f.write(svg_dark)

print('Updated logo-light.svg and logo.svg successfully. Total width:', total_w)


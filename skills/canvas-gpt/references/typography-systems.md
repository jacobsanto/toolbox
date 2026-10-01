# Typography Systems
# CanvasGPT Reference — Type classification, pairing, scale, and specifications

---

## Type Classification Reference

### Serif Families

**Old Style / Humanist Serif**
Character: Warm, classical, literary
Best for: Publishing, luxury, heritage brands, long-form text
Examples: Garamond, Caslon, Palatino, EB Garamond
Avoid for: Digital UI, SaaS, technology

**Transitional Serif**
Character: Balanced, refined, authoritative
Best for: Finance, law, editorial, academic
Examples: Times New Roman, Baskerville, Georgia
Avoid for: Consumer brands, youth markets

**Modern / Didone Serif**
Character: Sophisticated, high-contrast, fashion-forward
Best for: Luxury fashion, editorial, premium brands
Examples: Didot, Bodoni, Playfair Display
Avoid for: Body text (low readability at small sizes), digital UI

**Slab Serif**
Character: Strong, confident, approachable
Best for: Branding, display, food brands, sports
Examples: Rockwell, Clarendon, Courier, Roboto Slab
Avoid for: Formal/luxury contexts

### Sans-Serif Families

**Geometric Sans**
Character: Modern, clean, precise, cold
Best for: Technology, architecture, contemporary design
Examples: Futura, Circular, Nunito, Poppins
Avoid for: Warm/human contexts, long body text (low readability)

**Humanist Sans**
Character: Readable, warm, accessible, contemporary
Best for: UI, digital products, healthcare, education, most modern brands
Examples: Gill Sans, Frutiger, Calibri, Inter, DM Sans
Best all-purpose choice for most digital products

**Neo-Grotesque Sans**
Character: Neutral, Swiss precision, professional
Best for: Corporate, information design, global brands
Examples: Helvetica, Arial, Univers, Plus Jakarta Sans
Avoid for: Brands needing strong personality

**Grotesque Sans**
Character: Quirky, characterful, authentic
Best for: Artisanal brands, food, culture
Examples: Franklin Gothic, Trade Gothic, Aktiv Grotesk

---

## Type Scale Systems

### Modular Scale — Perfect Fourth (1.333) — Most Versatile

| Token | Size | Line height | Use |
|---|---|---|---|
| text-xs | 12px | 1.5 | Captions, labels, metadata |
| text-sm | 14px | 1.5 | Secondary text, UI labels |
| text-base | 16px | 1.6 | Body text — primary reading |
| text-lg | 21px | 1.5 | Lead paragraphs, introductions |
| text-xl | 28px | 1.3 | H3, card titles |
| text-2xl | 37px | 1.2 | H2, section headings |
| text-3xl | 50px | 1.1 | H1, page titles |
| text-4xl | 67px | 1.05 | Display, hero headlines |

### Modular Scale — Major Third (1.25) — Compact

| Token | Size | Line height | Use |
|---|---|---|---|
| text-xs | 12px | 1.5 | Labels |
| text-sm | 14px | 1.5 | Secondary |
| text-base | 16px | 1.6 | Body |
| text-lg | 20px | 1.4 | Lead |
| text-xl | 24px | 1.3 | H3 |
| text-2xl | 30px | 1.2 | H2 |
| text-3xl | 38px | 1.15 | H1 |
| text-4xl | 48px | 1.1 | Display |

### Modular Scale — Perfect Fifth (1.5) — Editorial

| Token | Size | Line height | Use |
|---|---|---|---|
| text-base | 16px | 1.6 | Body |
| text-lg | 24px | 1.4 | Lead |
| text-xl | 36px | 1.25 | H3 |
| text-2xl | 54px | 1.1 | H2 |
| text-3xl | 81px | 1.05 | H1 |

---

## Font Pairing Guide

### Reliable Pairing Formulas

**Formula 1: Contrasting Serifs + Sans**
Display/headline serif + clean sans for body
Example: Playfair Display + Inter
Works for: Luxury, editorial, premium consumer brands

**Formula 2: Geometric + Humanist**
Geometric display + humanist body
Example: Circular + DM Sans
Works for: Modern tech, SaaS, contemporary brands

**Formula 3: Slab + Geometric**
Slab serif display + geometric sans body
Example: Roboto Slab + Roboto
Works for: Strong, confident brands

**Formula 4: Single Superfamily**
One typeface family, multiple weights
Example: Inter Regular + Inter SemiBold + Inter Bold
Works for: Clean, systematic, UI-focused products
Risk: Can feel generic without strong hierarchy through weight variation

### Specific Pairings by Industry

**Finance / Professional Services:**
Baskerville / Georgia + Inter
Playfair Display + Source Sans Pro
Libre Baskerville + Open Sans

**SaaS / Technology:**
Inter + Inter (weight contrast)
DM Sans + DM Serif Display
Plus Jakarta Sans + Playfair Display (for humanising tech brands)

**Healthcare:**
Nunito + Source Serif Pro
Lato + Merriweather

**Luxury / Premium:**
Cormorant Garamond + Montserrat
Playfair Display + Raleway
Bodoni Moda + DM Sans

**Food & Beverage:**
Playfair Display + Lato
Josefin Sans + Merriweather

---

## Typography Rules

### Body Text Non-Negotiables
- Minimum 16px on web (14px absolute minimum, 16px preferred)
- Line height: 1.5-1.7 for body text
- Maximum line length: 65-75 characters (CPL)
- Minimum contrast: 4.5:1 against background (WCAG AA)

### Heading Rules
- Heading line height: 1.1-1.3
- Heading tracking: slightly negative for large sizes (-0.02em to -0.04em)
- Maximum 2 levels of heading weight contrast on a single page

### Tracking (Letter Spacing)
- Body text: 0 (normal) or very slight positive (+0.01em)
- Headlines: slight negative (-0.02em to -0.04em at large sizes)
- All caps text: always add positive tracking (+0.05em to +0.1em)
- Never tighten tracking on small text

### Web Font Performance
- Use variable fonts where possible (single file, multiple weights)
- Maximum 3 font weights loaded per typeface
- Use font-display: swap to prevent invisible text during load
- Prefer system fonts for UI elements where brand expression is low priority

---

## Responsive Typography

Text must scale appropriately across viewport sizes.

### Clamp-based fluid typography (CSS)
```css
/* Scales from 16px at 320px viewport to 20px at 1440px viewport */
font-size: clamp(16px, 1vw + 14px, 20px);

/* Scales from 32px at 320px to 64px at 1440px */
font-size: clamp(32px, 3vw + 22px, 64px);
```

### Breakpoint-based scale

| Viewport | Base size | H1 | H2 | H3 |
|---|---|---|---|---|
| Mobile (375px) | 16px | 32px | 24px | 20px |
| Tablet (768px) | 16px | 40px | 30px | 24px |
| Desktop (1280px) | 16px | 56px | 40px | 30px |
| Large (1440px+) | 18px | 72px | 48px | 36px |

# Design Systems Architecture
# CanvasGPT Reference — Tokens, spacing, components, and system specifications

---

## What a Design System Is

A design system is not a style guide. It is not a component library.
It is the single source of truth for every visual decision across every touchpoint.
It governs how the brand looks, feels, and behaves — consistently, at scale.

A style guide tells you what colours to use.
A design system tells you why, when, how, and in what combination —
and enforces consistency across every person and tool that touches the brand.

---

## Design Token Architecture

### Level 1 — Primitive Tokens

Raw values with no semantic meaning. The foundation layer.

```
/* Colour primitives */
--color-blue-50: #EFF6FF;
--color-blue-100: #DBEAFE;
--color-blue-500: #3B82F6;
--color-blue-900: #1E3A5F;

/* Typography primitives */
--font-size-12: 12px;
--font-size-14: 14px;
--font-size-16: 16px;
--font-size-20: 20px;
--font-size-24: 24px;
--font-size-32: 32px;
--font-size-48: 48px;
--font-size-64: 64px;

/* Spacing primitives */
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
--space-12: 48px;
--space-16: 64px;

/* Border radius primitives */
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 16px;
--radius-xl: 24px;
--radius-full: 9999px;
```

### Level 2 — Semantic Tokens

Purpose-mapped values that reference primitives.
These are what designers and developers actually use.

```
/* Brand colours */
--color-brand-primary: var(--color-blue-500);
--color-brand-primary-dark: var(--color-blue-900);
--color-brand-primary-light: var(--color-blue-50);

/* Semantic colours */
--color-success: #22C55E;
--color-warning: #F59E0B;
--color-error: #EF4444;
--color-info: var(--color-blue-500);

/* Text colours */
--color-text-primary: #111827;
--color-text-secondary: #6B7280;
--color-text-disabled: #9CA3AF;
--color-text-inverse: #FFFFFF;

/* Surface colours */
--color-surface-base: #FFFFFF;
--color-surface-elevated: #F9FAFB;
--color-surface-overlay: #F3F4F6;

/* Typography semantic */
--text-xs: var(--font-size-12);
--text-sm: var(--font-size-14);
--text-base: var(--font-size-16);
--text-lg: var(--font-size-20);
--text-xl: var(--font-size-24);
--text-2xl: var(--font-size-32);
--text-3xl: var(--font-size-48);
--text-4xl: var(--font-size-64);
```

### Level 3 — Component Tokens

Component-specific tokens that reference semantic tokens.

```
/* Button tokens */
--button-primary-bg: var(--color-brand-primary);
--button-primary-text: var(--color-text-inverse);
--button-primary-hover-bg: var(--color-brand-primary-dark);
--button-padding-x: var(--space-4);
--button-padding-y: var(--space-2);
--button-radius: var(--radius-md);

/* Card tokens */
--card-bg: var(--color-surface-elevated);
--card-border: 1px solid #E5E7EB;
--card-radius: var(--radius-lg);
--card-padding: var(--space-6);
--card-shadow: 0 1px 3px rgba(0,0,0,0.1);
```

---

## Spacing Systems

### The 4px Base System (most common)

Every spacing value is a multiple of 4px.

| Token | Value | Use |
|---|---|---|
| space-1 | 4px | Micro spacing — icon gaps, tight elements |
| space-2 | 8px | Tight spacing — within components |
| space-3 | 12px | Small spacing — compact layouts |
| space-4 | 16px | Default spacing — standard component padding |
| space-6 | 24px | Medium spacing — between related elements |
| space-8 | 32px | Large spacing — section separation |
| space-12 | 48px | XL spacing — major section breaks |
| space-16 | 64px | XXL — hero sections, major layout breaks |
| space-24 | 96px | Maximum — page-level spacing |

### The 8px Base System (alternative)

Used when designs need more breathing room. 8px base, all multiples.

| Token | Value | Use |
|---|---|---|
| space-1 | 8px | Tight component spacing |
| space-2 | 16px | Standard component padding |
| space-3 | 24px | Between related elements |
| space-4 | 32px | Section separation |
| space-6 | 48px | Major section breaks |
| space-8 | 64px | Page-level breaks |

**Rule:** Pick one system and use it exclusively.
Mixed spacing systems create visual inconsistency that users feel
even when they cannot name it.

---

## Grid Systems

### Web Grid (12-column standard)

```
Desktop (1440px): 12 columns, 24px gutter, 80px margins
Laptop (1280px):  12 columns, 24px gutter, 64px margins
Tablet (768px):   8 columns,  20px gutter, 32px margins
Mobile (375px):   4 columns,  16px gutter, 16px margins
```

### Alternative grids

**Editorial (magazine-style):** 6 columns, larger gutters, asymmetric layouts
**Dashboard (information-dense):** 24 columns, tight gutters
**Marketing page:** 12 columns, generous margins

---

## Component Specifications

### Button Sizes

| Size | Height | Padding X | Font size | Use |
|---|---|---|---|---|
| XS | 28px | 10px | 12px | Compact tables, tags |
| SM | 32px | 12px | 14px | Secondary actions |
| MD (default) | 40px | 16px | 14-16px | Primary UI actions |
| LG | 48px | 20px | 16px | Hero CTAs, prominent actions |
| XL | 56px | 24px | 18px | Landing page primary |

**Touch target:** Minimum 44x44px for any interactive element (WCAG 2.5.5)
Visual size can be smaller if the touch target is padded to minimum.

### Form Elements

**Input field height:** 40px (MD) / 48px (LG) / 36px (SM)
**Label position:** Above input (most accessible, most readable)
**Placeholder:** Supplementary only — never as label replacement
**Error state:** Red border + error icon + error text below field
**Focus state:** Visible focus ring — 2-3px, brand colour — mandatory for accessibility

### Card Components

**Padding:** 16px (compact) / 24px (standard) / 32px (spacious)
**Border radius:** 8px (modern) / 4px (corporate) / 16px (friendly/consumer)
**Shadow levels:**
- Level 1: 0 1px 3px rgba(0,0,0,0.1) — subtle, resting state
- Level 2: 0 4px 12px rgba(0,0,0,0.15) — elevated, hover state
- Level 3: 0 8px 24px rgba(0,0,0,0.2) — floating, modal/dropdown

---

## Dark Mode Architecture

Dark mode is not simply inverting colours. It requires a parallel token system.

**Common mistakes:**
- Pure black backgrounds (#000000) create too much contrast — use #0F172A or #111827
- Pure white text on dark (#FFFFFF) is too harsh — use #F8FAFC or #F1F5F9
- Colours with opacity (shadows, overlays) must be recalculated for dark backgrounds

**Dark mode surface layers:**
- Base: #111827
- Elevated: #1F2937
- Overlay: #374151

**Dark mode text:**
- Primary: #F9FAFB
- Secondary: #9CA3AF
- Disabled: #6B7280

---

## Accessibility Standards

### Contrast Requirements (WCAG 2.2)

| Text type | AA minimum | AAA preferred |
|---|---|---|
| Normal text (under 18px) | 4.5:1 | 7:1 |
| Large text (18px+ or 14px+ bold) | 3:1 | 4.5:1 |
| UI components / graphics | 3:1 | N/A |

**Test every combination.** Do not assume. Tools: Colour Contrast Analyser, Figma A11y plugins.

### Focus States
Every interactive element must have a visible focus indicator.
WCAG 2.2 (Focus Appearance) requirements:
- Minimum area: perimeter of component × 2px
- Minimum contrast: 3:1 against adjacent colours
- Do not remove browser default focus styles without replacing them

### Touch Targets
- Minimum 44×44px touch target for all interactive elements
- 8px minimum spacing between touch targets
- For icons used as buttons: ensure adequate hit area even if visual is smaller

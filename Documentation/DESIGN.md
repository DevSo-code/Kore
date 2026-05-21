# DESIGN.md — UI/UX Direction

## Design Philosophy

**"Focused darkness."** The app should feel like a professional tool, not a consumer app. Inspired by JetBrains IDEs, Figma's dark panels, and Linear's information density. Every pixel earns its place.

---

## Color Palette

### Base (Dark Mode — Primary)

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-base` | `#0F1117` | Main window background |
| `bg-surface` | `#1A1D27` | Tab panels, cards |
| `bg-elevated` | `#22263A` | Input fields, dropzones |
| `bg-hover` | `#2A2F47` | Hover states |
| `border` | `#2E3250` | Dividers, input borders |
| `border-focus` | `#5C6BC0` | Focused input ring |

### Accent

| Token | Hex | Usage |
|-------|-----|-------|
| `accent-primary` | `#6C63FF` | Primary buttons, active tab indicator |
| `accent-secondary` | `#00D4AA` | Success states, progress bar fill |
| `accent-danger` | `#FF5C6C` | Error banners, destructive actions |
| `accent-warning` | `#FFB347` | Warnings, queue states |

### Text

| Token | Hex | Usage |
|-------|-----|-------|
| `text-primary` | `#E8EAFF` | Headings, labels |
| `text-secondary` | `#8B90B8` | Descriptions, placeholders |
| `text-muted` | `#5A5F80` | Disabled states, metadata |

---

## Typography

- **Font:** `Inter` (bundled) → fallback `Segoe UI` (Win) / `SF Pro` (Mac) / `Noto Sans` (Linux)
- **Scale:**
  - App title / tab labels: `14px Medium`
  - Section headers: `13px SemiBold`
  - Body / labels: `12px Regular`
  - Metadata / paths: `11px Regular`, `text-muted`
- **Monospace** (file paths, URLs): `JetBrains Mono` or `Cascadia Code`

---

## Layout

```
┌─────────────────────────────────────────────────────┐
│  ⚙ Kore                  [_][□][×]  (titlebar)      │
├──────────────┬──────────────────────────────────────┤
│              │                                       │
│  [🖼 Image]  │           TAB CONTENT AREA            │
│  [📹 Video]  │                                       │
│  [🎵 Spotify]│                                       │
│  [⚙ Settings]│                                       │
│              │                                       │
│   (sidebar   │                                       │
│   nav)       │                                       │
├──────────────┴──────────────────────────────────────┤
│  Status bar: Ready  │  GPU: Off  │  v2.0.0           │
└─────────────────────────────────────────────────────┘
```

- **Navigation:** Left sidebar (icon + label), not top tabs — scales better for future modules
- **Content area:** Full-height, scrollable per tab
- **Status bar:** Always-visible, 24px height

---

## Component Design

### Drop Zone (Image Module)
```
┌─────────────────────────────────┐
│                                 │
│   [ ↑ ]                        │
│   Drop image here               │
│   or click to browse            │
│                                 │
│   PNG · JPG · WEBP              │
└─────────────────────────────────┘
```
- Dashed border `#2E3250`, 8px radius
- On hover/drag-over: border `#6C63FF`, bg `#1E1B3A`
- On drop: instant preview

### Progress Bar
- Track: `bg-elevated`
- Fill: animated gradient `#6C63FF` → `#00D4AA`
- Label below: `"Downloading... 42% · 3.2 MB/s · ETA 12s"`

### Buttons
- **Primary:** bg `#6C63FF`, hover `#7C75FF`, active scale `0.97`
- **Ghost:** transparent, border `#2E3250`, hover bg `#22263A`
- **Danger:** bg `#FF5C6C` — only for destructive actions
- Corner radius: `6px` for all buttons

### Toast / Notification
- Slides in from bottom-right
- Success: left border `4px solid #00D4AA`
- Error: left border `4px solid #FF5C6C`
- Auto-dismiss: 4 seconds

---

## Component Library

Since this is a **Python desktop app**, web component libraries (shadcn, Radix) don't apply directly. Equivalent recommendations:

| Web Equivalent | Desktop Python Equivalent |
|---------------|--------------------------|
| shadcn/ui | `CustomTkinter` (themed widgets) |
| Radix primitives | `Flet` (Flutter-based, cross-platform) |
| Tailwind colors | Custom `CTkTheme` JSON matching palette above |
| Framer Motion | `CTkAnimate` or manual thread-driven transitions |

**Recommended framework: `Flet`** — renders Flutter widgets, supports true GPU-composited animations, cleaner component model than CustomTkinter.

---

## Iconography

- **Library:** `Lucide` icons (SVG, bundled as PNG sprites at 16px/24px)
- Style: Outlined, 1.5px stroke, no fills
- Color: `text-secondary` default, `text-primary` on active state

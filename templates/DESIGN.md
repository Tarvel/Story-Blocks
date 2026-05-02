---
name: Interactive Storytelling Neo-Brutalism
colors:
  surface: '#fff9e5'
  surface-dim: '#dfdac6'
  surface-bright: '#fff9e5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f9f4df'
  surface-container: '#f3eeda'
  surface-container-high: '#ede8d4'
  surface-container-highest: '#e8e3ce'
  on-surface: '#1d1c10'
  on-surface-variant: '#4a4731'
  inverse-surface: '#333123'
  inverse-on-surface: '#f6f1dc'
  outline: '#7b785f'
  outline-variant: '#ccc7aa'
  surface-tint: '#676000'
  primary: '#676000'
  on-primary: '#ffffff'
  primary-container: '#ffee00'
  on-primary-container: '#736b00'
  inverse-primary: '#d8ca00'
  secondary: '#0035c6'
  on-secondary: '#ffffff'
  secondary-container: '#0448ff'
  on-secondary-container: '#d6daff'
  tertiary: '#006a6a'
  on-tertiary: '#ffffff'
  tertiary-container: '#75ffff'
  on-tertiary-container: '#007676'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#f7e600'
  primary-fixed-dim: '#d8ca00'
  on-primary-fixed: '#1f1c00'
  on-primary-fixed-variant: '#4e4800'
  secondary-fixed: '#dde1ff'
  secondary-fixed-dim: '#b9c3ff'
  on-secondary-fixed: '#001257'
  on-secondary-fixed-variant: '#0033c0'
  tertiary-fixed: '#6cf7f7'
  tertiary-fixed-dim: '#49dada'
  on-tertiary-fixed: '#002020'
  on-tertiary-fixed-variant: '#004f50'
  background: '#fff9e5'
  on-background: '#1d1c10'
  surface-variant: '#e8e3ce'
typography:
  display-xl:
    fontFamily: Epilogue
    fontSize: 80px
    fontWeight: '900'
    lineHeight: '1.0'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Epilogue
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Epilogue
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
  body-lg:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '400'
    lineHeight: '1.5'
  body-md:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  metadata:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 24px
  margin: 32px
---

## Brand & Style
The brand personality of this design system is unapologetic, high-energy, and structural. It is designed for an interactive storytelling platform that values raw expression and clarity over traditional "polish." The aesthetic rejects the softness of modern SaaS design in favor of a Neo-brutalist movement—using aggressive visual weight, high-contrast boundaries, and a functionalist layout.

The UI should evoke a sense of digital "physicality." Every element feels like a heavy block or a tactile punch-out, grounding the imaginative nature of storytelling with a gritty, reliable interface. This design system targets creators and readers who appreciate transparency in digital construction and a bold, editorial attitude.

## Colors
This design system utilizes a high-contrast, high-impact palette. The foundation is built on stark white and light gray backgrounds to provide a canvas for dense information. 

- **Primary Accent:** A sharp, aggressive yellow used for high-priority interactive elements and key navigational landmarks.
- **Secondary Accent:** An electric blue used for secondary actions, links, and system-level feedback.
- **Structural Neutral:** Solid black is used for all borders, shadows, and primary text, ensuring maximum legibility and a "comic-book" or "zine" structural feel.
- **Backgrounds:** Use the stark white for primary content cards and the light gray for page backgrounds to create subtle layering without relying on gradients.

## Typography
Typography is a structural pillar of this design system. We employ a dual-font strategy to balance editorial impact with technical precision.

- **Headlines:** Epilogue is used in its heaviest weights. It provides a geometric, distinctive, and slightly "loud" feel. For Display and Headline levels, use tight letter-spacing to enhance the chunky aesthetic.
- **Metadata and Technicals:** Space Grotesk is used for body copy, labels, and metadata. Its technical, geometric construction mimics monospaced fonts while maintaining superior legibility for long-form storytelling. Use uppercase for labels and small metadata to emphasize the "utility" look.

## Layout & Spacing
The layout philosophy is a rigid, fluid grid. The system uses a 12-column grid for desktop views, prioritizing heavy-duty containers that span specific column counts.

Spacing is governed by a strict 4px/8px rhythm. Margins and gutters are generous to prevent the high-contrast elements from feeling cluttered. Content blocks should not use soft padding; instead, use large, intentional gutters to create "air" between the heavy, black-bordered components. Layouts should favor vertical stacking and clear horizontal divisions.

## Elevation & Depth
In this design system, depth is not simulated with light or blur. Instead, it uses "Hard Offset Shadows."

- **Shadow Character:** All shadows are 100% opacity solid black. They are offset exactly 4px or 8px horizontally and vertically. There is 0px blur.
- **The "Lift" Effect:** When an element is hovered, the offset shadow should increase in distance or the element should move "into" the shadow (a reverse-press effect) to signal interactivity.
- **Layers:** Use thickness rather than shadow size to denote hierarchy. A 4px border is the standard for primary containers, while a 3px border is used for nested elements.

## Shapes
This design system uses a strictly sharp shape language. The `roundedness` value is set to 0. 

Every component—from buttons and input fields to large content cards—features 90-degree corners. This reinforces the "raw" and "unrefined" brutalist aesthetic. The only exceptions are specific circular icons or user avatars, which should be contained within square frames to maintain the system's geometric integrity.

## Components
Components in this design system must feel chunky, heavy, and high-contrast.

- **Buttons:** Use a 4px solid black border and the sharp yellow (Primary) or electric blue (Secondary) background. Every button must have a 4px black offset shadow. On click, the button should shift 4px down and right to "hide" the shadow, simulating a physical press.
- **Input Fields:** Stark white backgrounds with 4px black borders. Placeholder text should be in Space Grotesk at 50% opacity. Focused states should swap the border color to electric blue or increase the shadow depth.
- **Cards:** Large containers for story chapters or assets. Use the light gray background with a 4px black border. Headers inside cards should be separated by a solid 4px black horizontal line.
- **Chips/Tags:** Small rectangular blocks with a 2px black border and no shadow. Use these for categories or metadata labels.
- **Progress Bars:** Use a 4px black border "track" with a solid electric blue "fill" that has no rounding.
- **Interactive Narrative Nodes:** Specific to this platform, these should appear as chunky blocks with thick borders, using the electric blue to indicate paths already taken and the sharp yellow for the current active path.
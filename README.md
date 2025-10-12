# Pilgrim Packages — Frontend (HTML / CSS / JS)

Summary
- Single-page static site using Bootstrap 5.3 for layout and components.
- Minimal internal CSS placed in `<head>` (keeps overrides small and easy to change).
- No custom JavaScript (only Bootstrap's bundle is included). All previous custom JS was removed.
- Accessibility and performance improvements applied (skip link, lazy loading for images, semantic markup).

Files (main)
- `index.html` — primary HTML file. Contains:
  - Bootstrap CSS import and Google Fonts preconnect.
  - JSON-LD organization schema.
  - A compact internal `<style>` block for small site-specific styles and utilities.
  - Site content: navbar, hero/header, carousels, cards, contact form, about and footer.
  - Bootstrap JS bundle at the end of the body.
- `index-progressive.html` — added: progressive image demo using LQIP (blur-up), <picture> with WebP/AVIF sources and a small IntersectionObserver loader. Use this to compare progressive loading patterns with the baseline.
- `img/` — (local images referenced by `index.html`).

Key decisions & how they map to files
1. Styling
   - Bootstrap handles the majority of layout, spacing and components.
   - Small internal CSS (in `index.html` head) centralizes previously inline styles:
     - body base (font, background, top padding for fixed navbar)
     - header visuals (gradient, spacing, shadow)
     - carousel image sizing
     - utility classes:
       - `.nav-logo` — logo size & border radius
       - `.about-img` — fixed height & object-fit for the about image
       - `.event-card` — fixed width for carousel event cards
       - `.visually-hidden-focusable` — skip-link visibility on focus
   - Rationale: keeping a small internal stylesheet improves maintainability while avoiding an external file for this small project.

2. JavaScript
   - All custom JS (external-link safety, demo contact form, back-to-top, dropdown hover handlers) was intentionally removed per project decision.
   - Only Bootstrap's official JS bundle is included:
     ```html
     <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
     ```
   - This keeps behavior consistent with native Bootstrap components (click-to-open dropdown on mobile and desktop).

3. Accessibility & Performance
   - Skip link added: `.visually-hidden-focusable` so keyboard users can skip to main content.
   - `loading="lazy"` applied to most non-critical images; first carousel image uses `loading="eager"`.
   - ARIA and semantic elements are used where appropriate (e.g., form controls).
   - Avoided target="_blank" mass-manipulation JS — you can add `rel="noopener noreferrer"` manually where needed.

How to edit styles
- Localized styles live inside `<style>` in `index.html` head. To change:
  - Small visual tweaks (colors, spacing): edit the CSS variables or class rules in that block.
  - Larger style sets / many pages: extract the styles to `assets/css/site.css` and link it from the head.

How to add custom JS (if needed)
- If you later require behavior (e.g., back-to-top, enhanced dropdown hover):
  - Create `assets/js/site.js`
  - Add it just before the Bootstrap bundle or after it depending on whether you rely on bootstrap JS:
    ```html
    <script src="assets/js/site.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    ```
  - Keep scripts unobtrusive: prefer event delegation, avoid inline handlers, and guard touch vs hover using media queries in CSS.

SEO & Metadata
- Primary metadata is in the `<head>`: title, description, keywords, canonical, Open Graph tags, and JSON-LD Organization schema.
- For better results per package/offers, consider adding Offer/Product structured data for each package card.

Run / Test locally
1. Open `index.html` in your browser (double-click or use a local static server).
2. For a simple local server (recommended to preserve relative URLs and avoid CORS when testing):
   - Python 3: `python -m http.server 8000` (from the project directory), then open http://localhost:8000/
   - Node: `npx serve .`

How to test the progressive demo
1. Open `index-progressive.html` in a browser or run a local static server (recommended).
2. Observe hero and key card images: a tiny placeholder is shown immediately, full responsive image loads and the blur is removed when the image finishes loading.
3. For production use: generate WebP/AVIF variants and optionally progressive JPEGs on the server.

Suggested next steps
- Move the internal `<style>` into `assets/css/site.css` when styles grow.
- Reintroduce small JS features as separate files (not inline) with feature detection (touch vs hover).
- Optimize images: generate WebP and responsive `srcset` for better performance on mobile.
- Add a server-side contact form handler or integrate a form service with validation + CAPTCHA.
- Add unit tests / visual regression tests if the UI evolves.

Contact & Contribution
- This README documents the current front-end structure. For any change requests (design or behavior), modify `index.html` and, if needed, add `assets/css/site.css` and `assets/js/site.js` to keep concerns separated.


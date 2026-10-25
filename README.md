# MindEcliptic — Wheel of the Year (static production build)

This is the standalone GitHub Pages–ready version of the approved Wheel of the Year calendar. It does not include a duplicate website header, navigation, or footer menu.

## What's included

- `index.html`: markup, SEO basics, and accessible controls
- `styles.css`: approved desktop and responsive design
- `app.js`: eight Sabbats, 2026–2100 astronomical dates, interactions, and Next Sabbat countdown
- `assets/wheel.webp`: approved wheel illustration (kept unchanged)
- `assets/*.webp`: the eight approved separate detail illustrations (kept unchanged)
- `.nojekyll`: optional static Pages deployment helper

All images were extracted from the previously approved, verified offline HTML without recompression or modification. The artwork inside the wheel intentionally differs from the image displayed after selecting a Sabbat.

## Preview locally

For best results, use a local HTTP server instead of opening `index.html` inside ChatGPT. From this directory:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/` in a browser. `index.html` may also work directly in Chrome when opened from disk because the app does not fetch JSON or call any remote API.

## Deploy to GitHub Pages (not done yet)

1. Create a repository (e.g. `mindecliptic-wheel-of-the-year`).
2. Upload the **contents** of this folder to the repository root. `index.html` must be in the root, not nested inside a second directory.
3. In repository Settings > Pages, select **Deploy from a branch**, branch `main`, folder `/ (root)`. Confirm the final URL shown by GitHub.
4. Test every Sabbat, image, year selector and Next Sabbat in the published site, both desktop and mobile.

When published as a repository site, the Pages URL is generally `https://ACCOUNT.github.io/REPOSITORY/`. Use the actual GitHub-provided URL and do not assume the example address is live.

## WordPress embedding (not done yet)

Embed the verified GitHub Pages URL within a WordPress Custom HTML block using an iframe. A dynamic iframe-height/resize solution may be required because the seven accordion sections change the document height. The parent WordPress page should include a short indexable introduction and accessibility-friendly context; iframe text may not be indexed as part of the parent page. Validate responsiveness, content security settings, font rendering, performance, and mobile tap targets on the real WordPress page before public launch.

## Maintainer notes

- Do not replace the wheel artwork with a collage of the detail images: the original wheel layout was intentionally approved.
- `Next Sabbat` is based on the visitor's **local current date**, not the manually selected historical/future year.
- The four Lesser Sabbats use 2026–2100 stored astronomical instants and the visitor's device time zone. Greater Sabbats use conventional calendar dates.
- `Next Sabbat` refreshes every minute and on tab focus/visibility. The calendar has no analytics, tracking, third-party libraries, or external images.
- `app.js` includes editorial content for all eight festival cards. To revise a text block, edit its corresponding field in the `SABBATS` array.
- This build keeps artwork, section texts, date logic, and interactive behavior unchanged from `Wheel_of_the_Year_VERIFIED.html`.

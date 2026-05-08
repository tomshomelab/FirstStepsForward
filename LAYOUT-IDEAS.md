# Layout & design ideas — phase 2

Captured during the initial GoDaddy → self-hosted ingestion. The
priority for phase 1 was **faithful text + visual recognisability**.
These are improvements deferred for phase 2, after Dad has signed off
on the imported content being correct.

## Will-do (clear wins, low risk)

- **Drop the "First Steps Forward × 8" header artifact** in the hero —
  it's a GoDaddy template bug, not a design choice.
- **Drop the period** after "First Steps Forward." in the hero.
- **Break up the wall-of-text** in The Practice / Counselling and
  Neurodiversity / The Setting. Currently each is one 8-sentence
  block. Targets: 2–3 sentence paragraphs, with sub-headings or
  pull-quotes where natural.
- **Drop the Show More / Show Less collapsers** on the Related
  Services blocks. Bad for SEO, bad for skimming, hides info
  visitors actually want.
- **Add an above-the-fold CTA** to the hero — currently just the
  email. A "Book an initial conversation" button (mailto: or
  scrolls to #contact) would convert better.
- **Drop the empty "More" nav dropdown** — it's confusing and has
  nothing in it.
- **Add Message field** to the contact form. Original asks only
  Name + Email, which makes initial enquiries info-poor.

## Worth discussing with Dad

- **Pricing as a clean two-column list / table** instead of prose
  sentences. Each price gets a row with title, amount, conditions.
- **Strengthen the About page** with a real bio + a photo of the
  garden shed setting. The shed is a genuine differentiator.
- **Trust signals at the top**: MNCS / National Counselling Society
  logo near the nav so credentials are visible immediately.
- **Concerns list as wrapped tag-cloud** (already done) vs back to
  the original linear list — depends which feels more approachable.

## Maintenance / code

- Wire the contact form to **Formspree** or **Web3Forms** before
  going live — currently just submits to `#`.
- Add **Umami analytics snippet** to `templates/base.html.j2` once
  the analytics stack confirms the site is added.
- Consider **Sveltia/Decap admin UI** (per the SOP) so Dad can edit
  copy himself once layout is settled.
- Pull the hero image to a smaller WebP variant — current
  `hero-bg.jpg` is 178KB, could be ~40KB at WebP quality 80.

## Won't do (without explicit ask)

- Major restructure of pages (e.g. splitting Home into Home /
  Services / Pricing) — current single-long-page is recognisable.
- New brand colour or typography — Sanchez + #a69179 is the
  existing brand, keep it.

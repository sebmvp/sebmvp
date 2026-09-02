<p align="center">
  <img src="assets/profile-header.svg" alt="Sebastian Vaskes Pimentel — building systems for messy data" width="100%"/>
</p>

I like taking messy information and figuring out how to make it usable. Most of what I build sits somewhere between data engineering, automation, analytics, and applied AI. I care that the systems can be rerun, inspected, and explained when something goes wrong. A pipeline you can't rerun safely is a liability with a scheduler.

## Selected work

<a href="https://github.com/sebmvp/commerce-data-platform">
  <img src="assets/card-commerce.svg" alt="Commerce Data Platform — validated ingest, safe reruns, quarantine, audit" width="420"/>
</a>
<a href="https://github.com/sebmvp/enterprise-rag-data-pipeline">
  <img src="assets/card-harpak.svg" alt="Enterprise RAG Data Pipeline — metadata normalization, entity resolution, provenance" width="420"/>
</a>
<a href="https://github.com/sebmvp/macro-asset-stress-modeling">
  <img src="assets/card-macro.svg" alt="Macro Stress & Asset Behavior — gold vs. bitcoin as safe havens under market stress" width="420"/>
</a>

**[Commerce Data Platform](https://github.com/sebmvp/commerce-data-platform)** — a data platform built around resale-commerce operations. The interesting engineering is the ingest lifecycle: content-hash change detection makes builds rerun-safe, Pydantic validation quarantines bad records instead of dropping them, every run writes an audit record, and SCD-2 + event-sourced modeling keeps historical state queryable. `docker compose up` rebuilds the whole warehouse from bundled synthetic data; CI does the same on every push.

**[Enterprise RAG Data Pipeline](https://github.com/sebmvp/enterprise-rag-data-pipeline)** — a sanitized case study of my Harpak-ULMA internship work. I owned the offline side of a retrieval system: turning inconsistent company documents and equipment metadata into structured, validated records — controlled schemas, layered exact/regex/fuzzy matching, provenance on every record — so the downstream system could answer questions about the right machine.

**[Macro Stress & Asset Behavior](https://github.com/sebmvp/macro-asset-stress-modeling)** — group research, not an engineering platform: when markets get stressed, does Gold actually protect you, and does Bitcoin behave anything like it? 4,150 daily observations, stress regimes, chronological modeling, walk-forward validation. Gold is a *conditional* safe haven; Bitcoin is not digital gold; and the MLP we trained failed in a way that taught us more than the models that worked.

## Currently

- polishing the commerce platform
- turning the macro project into a reproducible public writeup
- looking for a useful contribution in document/data tooling

## Off keyboard

Usually reading, training, traveling, or automating something that probably didn't need automating.

## Find me

- [linkedin.com/in/sebastianvaskes](https://www.linkedin.com/in/sebastianvaskes)
- [sebavaspim@gmail.com](mailto:sebavaspim@gmail.com)

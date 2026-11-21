# Requirements

18 requirements consolidated from 28 elicitation statements (similar-systems review, a client interview, and analysis of one week of published posts plus prototype defect notes). Priorities use MoSCoW.

## Functional

| ID | Requirement | Priority |
|---|---|---|
| FR1 | Add positions by hand or by uploading a broker export, including shares and options (call or put, strike, expiry), across more than one account, and calculate the break-even for each. | Must |
| FR2 | Keep a watch list of stocks the user does not own. | Must |
| FR3 | Let the administrator choose which analysts WaveDesk follows. | Must |
| FR4 | Collect new posts from followed analysts during the posting window, and split posts with several charts into separate chart items that keep the shared caption. | Must |
| FR5 | Read the levels from each chart image (not only the caption), classify each level, and mark a level as unreadable instead of guessing. | Must |
| FR6 | Match each item to a stock using the post's symbol tag, not by searching the text. | Must |
| FR7 | Show a dashboard with one row per position: live price, break-even, nearest levels above and below, invalidation level and when it was last covered. | Must |
| FR8 | Show a position detail page with each analyst's levels and disagreeing counts side by side, without picking one. | Must |
| FR9 | Alert when price reaches an analyst's level on a held or watched stock; send invalidation alerts on holdings as a phone notification within about two minutes. | Must |
| FR10 | Alert when an analyst adds, moves or removes a level on a held stock. | Must |
| FR11 | Send a morning and an evening summary, and hold non-urgent alerts during quiet hours. | Should |
| FR12 | For options, show whether each target is expected before the option expires, based on the analyst's stated timing. | Must |
| FR13 | Credit every level to the analyst who posted it, with the post link and time. | Must |

## Non-functional

| ID | Requirement | Priority |
|---|---|---|
| NFR1 | **Accuracy:** label every price as live or as of the chart time, store each level's price scale, store times in Eastern Time with their source, and flag stale levels. | Must |
| NFR2 | **Compliance:** only report what analysts posted, never make recommendations, never republish full posts. | Must |
| NFR3 | **Privacy:** never ask for brokerage login details; keep each user's positions private. | Must |
| NFR4 | **Coverage and speed:** never miss a chart on a held stock; deliver urgent alerts within two minutes. | Must |
| NFR5 | **Usability:** the daily review should take about fifteen minutes instead of an hour and a half. | Should |

**Will not (for now):** automatic wave counting, placing trades, analyst accuracy tracking. These would mean the system forming its own view of the market or acting on it.

## Prototype coverage

| Requirement | In the prototype (`src/wavedesk`) |
|---|---|
| FR1 | `io.load_positions` (CSV import with row-level errors), `Position.break_even` |
| FR2 | `watch_only` positions |
| FR5 | unreadable levels kept separate, never guessed |
| FR6 | `rules.ticker_from_tags` |
| FR7 | `reconcile` builds one row per position |
| FR11 | `brief.render` (morning brief) |
| FR12 | `rules.expiry_status` |
| FR13 | every `Level` carries analyst, post time and link |
| NFR1 | `Quote` vs chart price, `price_scale`, staleness |
| NFR2 | brief reports only, with a standing disclaimer |

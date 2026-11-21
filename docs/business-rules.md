# Business rules

Most rules came from real defects found while using an early prototype; the rest come from the client and from Canadian securities rules. Every rule with a limit has a number, because a vague rule cannot be tested. Rules marked with a test are enforced in `src/wavedesk/rules.py`.

| ID | Rule | Tested |
|---|---|---|
| BR1 | An invalidation alert on a held position is sent within two minutes at any hour. Other alerts during quiet hours (10 pm to 7 am) wait for the next summary. | |
| BR2 | A level is accepted only if it traces to the analyst's own chart, with analyst, post time and link. | model |
| BR3 | A price read from a chart is stored as "chart price at post time" and is never shown as live. | model |
| BR4 | Levels are compared only on the same price scale and contract. | yes |
| BR5 | When analysts disagree, all counts are shown side by side. WaveDesk never chooses one. | |
| BR6 | Two analysts agree only when their levels are within 1% and both charts are fresh. Agreement is reported, never recommended. | yes |
| BR7 | A level is stale when its chart is older than 1 trading day (intraday) or 3 days (daily and weekly). Stale levels are labelled, not deleted. | yes |
| BR8 | A ticker comes only from the post's symbol tag. A word in the text (such as "MA") never assigns a ticker. | yes |
| BR9 | An unreadable level is marked unreadable and sent to review. WaveDesk never guesses. | yes |
| BR10 | For options, a target is "before expiry" only if the analyst's stated timing ends before expiry; otherwise "after expiry" or "timing not stated". | yes |
| BR11 | WaveDesk reports what analysts posted and never makes recommendations. It stores levels and a short summary, never the full post. | |
| BR12 | WaveDesk never asks for brokerage logins. Positions come from manual entry or an uploaded file. | |
| BR13 | All times are stored in Eastern Time with their source; post time decides the order of updates. | |

## Where the rules came from

- **BR3:** a data source assumed to show closing prices was showing live intraday prices.
- **BR4:** levels compared across a stock split looked wildly wrong.
- **BR7:** week-old charts were being read as current.
- **BR8:** a post saying "MA" in passing was linked to Mastercard.
- **BR11:** in Canada, advice tailored to a specific person requires registration (NI 31-103, s. 8.25). A tool that matches analysis to a portfolio must report, not recommend.

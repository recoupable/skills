# Genre coverage sources

Verified 2026-09-07 against official MiniMax commit `945655064d59b98004dd70002e7eb5c8c6e11373`.
Read each of the 18 family indexes, count its compact-card rows, and compare the count
with its header. All headers matched; the sum was 1,000. Counts refer to prompting
examples, not training examples or measured genre quality.

[Official router](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/genre-router.md) · [Caption-rewriter method](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/SKILL.md)

| Family index | Verified cards |
|---|---:|
| [Metal & Heavy Rock](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-metal-heavy-rock.md) | 78 |
| [East Asian Modern Pop](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-east-asian-modern.md) | 75 |
| [Pop & Alternative Rock](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-pop-alternative-rock.md) | 75 |
| [Hip-Hop & Rap](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-hip-hop-rap.md) | 74 |
| [East Asian Ballad & Heritage Pop](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-east-asian-ballad-heritage.md) | 72 |
| [Modern R&B & Neo-Soul](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-modern-rnb-neo-soul.md) | 66 |
| [Jazz, Swing & Big Band](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-jazz-swing-big-band.md) | 65 |
| [Contemporary Folk & Acoustic](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-contemporary-folk-acoustic.md) | 64 |
| [Electronic, Synth & Ambient Pop](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-electronic-synth-ambient-pop.md) | 59 |
| [Soul, Blues & Gospel](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-soul-blues-gospel.md) | 59 |
| [Cinematic Pop & Ballad](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-cinematic-pop-ballad.md) | 54 |
| [Country & Americana](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-country-americana.md) | 50 |
| [Traditional Vocal & Stage](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-traditional-vocal-stage.md) | 43 |
| [Cinematic Orchestral & Epic](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-cinematic-orchestral-epic.md) | 42 |
| [Dance-Pop, Disco & Funk](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-dance-pop-disco-funk.md) | 37 |
| [Club, EDM, House & Trance](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-club-edm-house-trance.md) | 29 |
| [General Pop & Ballad](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-general-pop-ballad.md) | 29 |
| [Roots, Traditional & Global](https://github.com/MiniMax-AI/MiniMax-Music3/blob/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter/references/index-roots-traditional-global.md) | 29 |

Follow template links only from the one or two chosen family indexes during stage 3.
Do not load all 1,000 templates to write a caption.

# Film direction and prompt kit

## Prompt template

Replace the scene, camera direction, palette, and exact uppercase title for each card. Keep the temporal arc and exclusions consistent.

```text
Create an extraordinary eight-second promotional feature-card film for a music creation product.
[PERSON performs SPECIFIC ACTION in MUSIC SETTING. Materials transform into a PHYSICAL METAPHOR for this workflow. Specify camera movement and a distinct palette.]
Beginning 0–2 seconds: immediate cinematic human action.
Middle 2–5 seconds: astonishing transition from the human scene into tactile graphic design and motion design.
End 5–8 seconds: preserve moving humans and the rich visual world while the exact feature title "[EXACT TITLE]" lands beautifully and remains readable for at least two seconds.
Use two or three intentional lines for a long title, with monumental readable lettering.
The title is part of the scene, integrated in perspective and lighting, not a subtitle or generic overlay.
Only these title words may appear; no additional captions, labels, logos, or watermarks.
Maintain title within the central 80 percent safe area.
High-end music video craft, cinematic lensing, believable people, strong art direction, playful confident energy, seamless physical transformations.
No user interfaces, dashboards, app screens, charts, mock websites, static slideshow, or generic stock montage.
One coherent film. Crisp 16:9 composition. Silent.
Make the ending and opening compatible for repeated playback without sacrificing the title hold.
```

The final sentence is a loop-quality improvement to the recorded workflow; inspect the result rather than assuming the provider obeys it.

## Worked scenes

These scene briefs capture the approach used for the Recoup gallery. They contain no customer data or provider account identifiers.

| Card title | Human action and transformation | Camera and palette |
|---|---|---|
| Add a release | An artist places a record on a turntable; sleeves and stage elements open into a release world and the exact title. | Follow the record into the reveal; warm light and bold accent color. |
| Check my release metadata | An electronic artist snaps a clapperboard shut; album artwork, magnetic tape, and tactile letter blocks float and click into alignment. | Push through suspended pieces; cobalt and acid yellow. |
| Import my catalog | A record-store owner pulls a sleeve from a shelf; records sweep into a tunnel and assemble into an architectural archive whose shelves form the title. | Follow the sleeve into the whirlwind; walnut, teal, burnt orange. |
| Check my song credits | Musicians exchange a gesture; tactile objects connect the contributors and form the title without suggesting verified rights. | Preserve human expressions; warm stage light and sculptural materials. |
| Explain this music contract | A musician turns a page; paper unfolds into an expressive musical world and physical title letters. | Move through unfolding paper; a distinct palette from the archive scene. |

For publishing, a generation in the original batch ended in provider moderation with no asset. The shipped alternative was an explicitly authored silent motion graphic: score pages and ribbons arrange into a composition inventory, then reveal the title. This is a disclosed fallback, not evidence that the cinematic generation succeeded.

## Manifest template

```json
{
  "cardId": "example-workflow",
  "title": "Exact display title",
  "assetKind": "generated",
  "prompt": "Full submitted prompt",
  "settings": {
    "model": "seedance_2_5",
    "mode": "t2v",
    "duration": 8,
    "resolution": "720p",
    "aspect_ratio": "16:9",
    "generate_audio": false,
    "count": 1
  },
  "jobId": null,
  "terminalStatus": "not-submitted",
  "assetLocation": null,
  "review": {
    "wholeFilm": "not-reviewed",
    "exactTitle": "not-reviewed",
    "crop": "not-reviewed",
    "loopBoundary": "not-reviewed",
    "browserPlayback": "not-tested",
    "deployedAsset": "not-tested"
  }
}
```

Do not substitute sample statuses for actual evidence. Use `assetKind: authored` for a fallback and retain the failed generation's separate record.

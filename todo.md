# todo

## high prio
- new scraping/json file logic:
only for events with title that contains "legend" in it:  -- parse them and store them into the json object
the website page itself fomatting goes:
```
image (banner)
date (text)
image
date (text)
image
date (text)
image
```
example json:
```json
{
  "events": [
    {
      "title": "title",
      "legend": {
          "dates": [
              "dateX",
              "dateY",
              "dateZ",
          ],
          "images": [
              "imageX",
              "imageY",
              "imageZ",
          ]
      }
    }
  ]
}
```

## low prio
chanme logic similar to legend (multiple dates, 1 img)

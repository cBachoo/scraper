# todo

## high prio
- new scraping/json file logic:
only for events with title that contains "legend" in it:  -- parse them and store them into the json object
the website page itself fomatting goes:
image (incorrect header/banner)
date (text)
image
date (text)
image
date (text)
image
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
- implement legend race logic:
legend races have 3 images / 3 dates -- we need to parse them corectly

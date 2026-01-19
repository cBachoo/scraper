# todo

## high prio
- new scraping/json file logic:
if a site has multiple titles/url -- parse them and store them into the json object, e.g
```json
{
  "scouts": [
    {
      "title": "example title",
      "dates": [
        {
          "dateX": "date (utc)"
        },
        {
          "dateY": "date (utc)"
        },
        {
          "dateZ": "date (utc)"
        }
      ],
      "images": [ //images can also return only 1 
        {
          "imgX": "link"
        },
        {
          "imgY": "link"
        },
        {
          "imgZ": "link"
        }
      ]
    }
  ]
}
```
- instead of ignoring/skipping based on duplicate dates, ignore based on keyword 'coming' in title

## low prio
- implement legend race logic:
legend races have 3 images / 3 dates -- we need to parse them corectly

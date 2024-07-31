---
toc: false
---

```js
import {Card, CardList} from "./components/Card.js";

const data = await FileAttachment("data/latest.json").json();
```

# NOAA Hurricane Data Scraper

Tidied up versions of the map files posted by the U.S. government’s National Hurricane Center and Central Pacific Hurricane Center

```jsx
display(<CardList cards={data}></CardList>)
```

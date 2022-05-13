# RandomSakuga
A Python script that uses the moebooru API to communicate with [Sakugabooru](https://www.sakugabooru.com) to fetch a random animated video. the Video is then posted to Facebook using the Graph API along with some info like the artist name, the media title (movie/TV show/OVA/etc) and a possible link to MyAnimeList queried using the Jikan API if the media is eastern.

## TODO
- [ ] ~~If config file not present at the same directory as the executable **and** not an input argument, create a formatted config file.~~ **Dropped**
- [x] ~~Create rules or a dictionary for capitalizing certain sequences (a letter after an apostrophe shouldn't be capitalized, all letters in Roman numerals should be capitalized, etc.)~~

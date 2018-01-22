# gen-champ-lb

"Lobster, this is the worst documentation I've ever seen."

"Good, it'll match the worst code you've ever seen."


### Usage
The script entry point is `genchamplb.py`, which expects two arguments:
- The name of the config file (without the `.ini` extension), in a directory called `data`
- A command to execute, can be any of `{"gen", "add", "upd", "del"}`

### Configuration
Configuration is performed via an `.ini` file whose name is passed as the first argument to
`genchamplb.py`. The file is expected to be in the following format:

```ini
[Authentication]
; Riot Games API Key
RiotKey=

[Leaderboard]
; Champion ID for retrieving Mastery Data
ChampionID=
; Output format, can be any of {"console", "json", "reddit"}
Ouptut=

[Files]
; Where to store user data such as the Summoner ID. Must be a JSON file.
UserData=
; Where to write output.
OutputFile=
```

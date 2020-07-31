# **IMPORTANT! We've moved development of this repo to the `main` branch. You will not be able to merge changes into `master`.**

## **UPDATING LOCAL CLONES**

(via [this link](https://www.hanselman.com/blog/EasilyRenameYourGitDefaultBranchFromMasterToMain.aspx), thanks!)

If you have a local clone, you can update and change your default branch with the steps below.

```sh
git checkout master
git branch -m master main
git fetch
git branch --unset-upstream
git branch -u origin/main
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
```

The above steps accomplish:

1. Go to the master branch
2. Rename master to main locally
3. Get the latest commits from the server
4. Remove the link to origin/master
5. Add a link to origin/main
6. Update the default branch to be origin/main



[![Code of Conduct](https://img.shields.io/badge/%E2%9D%A4-code%20of%20conduct-blue.svg?style=flat)](https://github.com/edgi-govdata-archiving/overview/blob/master/CONDUCT.md)

# Analyze EDGI Monitored Pages for Word Changes

A quick and dirty tool to load the earliest and latest version of every page EDGI's Web Monitoring team tracks and compare them to see what words on the page have changed.

Run it against all the data! This will take a long time and generate some huge files. And probably eat all your RAM.

```sh
> python analyze.py > output.json
```

Options:

- `--pattern <url_pattern>` Only analyze pages with a URL matching this pattern. e.g. `*energy.gov/*`.

- `--ngrams <count>` Consider up to `<count>` consecutive words to form a term. For example, if you set this to three and saw the following phrase added: `atmospheric carbon is increasing`, the following terms would be considered as changed:
        1. `atmospheric`
        2. `carbon`
        3. `is`
        4. `increasing`
        5. `atmospheric carbon`
        6. `carbon is`
        7. `is increasing`
        8. `atmospheric carbon is`
        9. `carbon is increasing`

    Defaults to `2`. Maximum value is `5`.

- `--sqlite <path>` Output a SQLite database of the results to this path for easy analysis.

- `--cache` Cache requests to web-monitoring-db in `./cache.sqlite`. Useful when running repeatedly and adjusting other options or altering the code.

- `--verbose` Print a list of all the pages that were skipped or failed and why.

- ~`--readability` Parse the versions with readability before diffing. This will hopefully create results focused only on changes to the main body of a page, and not count changes to text in headers, footers, navigation, etc.~ (This is *always* true right now, you don't need to specify it.)

    **This is broken.** You'll need to start the readability server manually in the `readability-server` directory:

    ```sh
    > cd readability-server
    > npm install
    > node index.js
    ```

    And if you don't want to use it, edit `analyze_page()` in `analyze.py`.

You can use the `--sqlite` option to generate a database for usage with [Datasette](https://datasette.readthedocs.io/). For example: https://cute-oyster.glitch.me/changes


## Output

This generates JSON output on `stdout`. Each line a single JSON object representing on page in the web monitoring database, and expands to something like:

```json
{
  "id": "df581bbe-ea83-418f-9372-262e704d079b",
  "first_id": "25ad24c8-2a02-4a6a-90be-61f04438c703",
  "last_id": "ac89fc61-1f8a-49a2-b8bd-632faa5ee8d6",
  "url": "https://www.fs.fed.us/managing-land/national-forests-grasslands",
  "title": "Forests and Grasslands | US Forest Service",
  "status": 200,
  "first_date": "2017-05-26T16:23:42+00:00Z",
  "last_date": "2019-09-26T02:07:31+00:00Z",
  "percent_changed": 0.7375728964176618,
  "terms": [
    {
      "restoring": 1,
      "hope": 1,
      "video": 1,
      "recreation": 1,
      "service restoring": 1,
      "restoring hope": 1,
      "hope video": 1,
      "lands recreation": 1,
      "recreation providing": 1
    },
    {
      "forests": 4,
      "forest": 6,
      "service": 2,
      "stewards": 1,
      "impressive": 1,
      "portfolio": 1,
      "landscapes": 1,
      "across": 1,
      "193": 1,
      "million": 2,
      "acres": 1,
      "national": 3,
      "grasslands": 5,
      "public": 1,
      "trust": 1,
      "agencys": 1,
      "top": 1,
      "priority": 1,
      "maintain": 1,
      "improve": 1,
      "health": 3,
      "diversity": 2,
      "productivity": 2,
      "nations": 1,
      "meet": 1,
      "needs": 1,
      "current": 2,
      "future": 2,
      "generations": 2,
      "management": 4,
      "products": 1,
      "vegetation": 2,
      "protection": 1,
      "minerals": 2,
      "geology": 2,
      "manages": 1,
      "mineral": 1,
      "energy": 1,
      "program": 1,
      "provide": 1,
      "commodities": 1,
      "commensurate": 1,
      "need": 1,
      "sustain": 1,
      "long": 1,
      "term": 1,
      "biological": 1,
      "ecosystems": 3,
      "plants": 5,
      "native": 4,
      "valued": 1,
      "economic": 1,
      "ecological": 1,
      "genetic": 1,
      "aesthetic": 1,
      "benefits": 1,
      "using": 1,
      "plant": 3,
      "material": 1,
      "projects": 1,
      "maintains": 1,
      "restores": 1,
      "gene": 1,
      "pools": 1,
      "communities": 1,
      "help": 1,
      "reverse": 1,
      "trend": 1,
      "species": 3,
      "loss": 1,
      "north": 1,
      "america": 1,
      "celebrating": 1,
      "wildflowers": 1,
      "materials": 1,
      "pollinators": 1,
      "rare": 2,
      "invasive": 1,
      "rangelands": 2,
      "united": 1,
      "states": 1,
      "diverse": 1,
      "lands": 1,
      "wet": 1,
      "florida": 1,
      "desert": 2,
      "shrub": 1,
      "wyoming": 1,
      "include": 1,
      "high": 1,
      "mountain": 1,
      "meadows": 1,
      "utah": 1,
      "floor": 1,
      "california": 1,
      "rangeland": 1,
      "wild": 1,
      "horse": 1,
      "burro": 1,
      "recreation": 1,
      "restoration": 6,
      "helping": 1,
      "nature": 2,
      "recover": 1,
      "degradation": 1,
      "damage": 1,
      "destruction": 1,
      "goal": 1,
      "establish": 1,
      "balance": 1,
      "needed": 1,
      "air": 2,
      "water": 6,
      "animals": 1,
      "thrive": 1,
      "overview": 1,
      "research": 1,
      "programs": 1,
      "one": 1,
      "important": 1,
      "resources": 1,
      "flowing": 1,
      "providing": 1,
      "drinking": 1,
      "180": 1,
      "people": 2,
      "facts": 1,
      "watershed": 2,
      "climate": 1,
      "change": 1,
      "wildlife": 3,
      "fish": 2,
      "work": 1,
      "includes": 1,
      "restoring": 2,
      "aquatic": 1,
      "organism": 1,
      "passage": 1,
      "stream": 1,
      "habitat": 2,
      "floodplains": 1,
      "enhancing": 1,
      "lake": 1,
      "vast": 1,
      "array": 1,
      "hummingbirds": 1,
      "bighorn": 1,
      "sheep": 1,
      "spotted": 1,
      "frogs": 1,
      "black": 1,
      "bears": 1,
      "connecting": 1,
      "outdoors": 1,
      "lands forests": 1,
      "forest service": 2,
      "service stewards": 1,
      "impressive portfolio": 1,
      "landscapes across": 1,
      "across 193": 1,
      "193 million": 1,
      "million acres": 1,
      "national forests": 2,
      "public trust": 1,
      "agencys top": 1,
      "top priority": 1,
      "health diversity": 1,
      "nations forests": 1,
      "future generations": 2,
      "generations forest": 1,
      "forest management": 1,
      "management forest": 2,
      "forest products": 1,
      "products vegetation": 1,
      "vegetation management": 1,
      "forest health": 1,
      "health protection": 1,
      "protection minerals": 1,
      "service manages": 1,
      "energy program": 1,
      "provide commodities": 1,
      "generations commensurate": 1,
      "long term": 1,
      "term health": 1,
      "biological diversity": 1,
      "ecosystems minerals": 1,
      "geology management": 1,
      "management plants": 1,
      "plants native": 1,
      "native plants": 1,
      "economic ecological": 1,
      "ecological genetic": 1,
      "aesthetic benefits": 1,
      "benefits using": 1,
      "using native": 1,
      "native plant": 3,
      "plant material": 1,
      "vegetation projects": 1,
      "projects maintains": 1,
      "restores native": 1,
      "plant gene": 1,
      "gene pools": 1,
      "pools communities": 1,
      "help reverse": 1,
      "species loss": 1,
      "north america": 1,
      "america celebrating": 1,
      "celebrating wildflowers": 1,
      "wildflowers native": 1,
      "plant materials": 1,
      "materials pollinators": 1,
      "pollinators rare": 1,
      "rare plants": 2,
      "plants invasive": 1,
      "invasive species": 1,
      "species rangelands": 1,
      "rangelands rangelands": 1,
      "united states": 1,
      "diverse lands": 1,
      "wet grasslands": 1,
      "desert shrub": 1,
      "shrub ecosystems": 1,
      "high mountain": 1,
      "mountain meadows": 1,
      "desert floor": 1,
      "california rangeland": 1,
      "rangeland management": 1,
      "management national": 1,
      "national grasslands": 1,
      "grasslands wild": 1,
      "wild horse": 1,
      "burro recreation": 1,
      "recreation providing": 1,
      "restoration restoration": 1,
      "helping nature": 1,
      "nature recover": 1,
      "degradation damage": 1,
      "nature needed": 1,
      "air water": 1,
      "water plants": 1,
      "thrive restoration": 1,
      "restoration overview": 1,
      "overview forest": 1,
      "forest restoration": 1,
      "restoration research": 1,
      "research restoration": 1,
      "restoration programs": 1,
      "programs water": 1,
      "water water": 1,
      "important water": 1,
      "water resources": 1,
      "resources flowing": 1,
      "grasslands providing": 1,
      "providing drinking": 1,
      "drinking water": 1,
      "180 million": 1,
      "million people": 1,
      "people water": 1,
      "water facts": 1,
      "facts watershed": 1,
      "watershed restoration": 1,
      "restoration climate": 1,
      "climate change": 1,
      "change wildlife": 1,
      "work includes": 1,
      "includes restoring": 1,
      "restoring aquatic": 1,
      "aquatic organism": 1,
      "organism passage": 1,
      "passage stream": 1,
      "stream habitat": 1,
      "floodplains enhancing": 1,
      "enhancing lake": 1,
      "lake productivity": 1,
      "productivity restoring": 1,
      "restoring habitat": 1,
      "vast array": 1,
      "wildlife species": 1,
      "bighorn sheep": 1,
      "spotted frogs": 1,
      "black bears": 1,
      "connecting people": 1,
      "outdoors watershed": 1,
      "watershed fish": 1,
      "fish wildlife": 1,
      "wildlife air": 1
    }
  ]
}
```

`terms` is an array of:

1. All the 1-word and 2-word sets that were removed.
2. All the 1-word and 2-word sets that were added.

Note that the SQLite output includes a separate table with the *net change* for each term, and is not broken out into removals and additions. It’s easier to work with for most analyst use cases, but carries less information than the JSON does.

The SQLite is also limited to just the `KEY_TERMS` (see the top of `analyze.py`), while the JSON has *all* the words that were changed. You can change how large the word sequences we grab are with the `gram` argument to `analyze_page()`. (`1` to only extract single words; `2` to extract 1- and 2-word groups; `3` to extract 1-, 2-, and 3-word groups; etc.)


## Helper to List All Unique Terms

There is a helper script named `list_unique_terms.py` that you can use to list all the unique terms in the results that were output from `analyze.py`:

```sh
> python list_unique_terms.py path/to/analyze/output.json
```

Outputs a CSV like:

| term          | page_count |
| ------------- | ---------: |
| information   |       5789 |
| energy        |       5099 |
| national      |       4829 |
| page          |       4400 |
| office        |       4260 |
| research      |       4034 |
| data          |       4003 |
| program       |       3828 |
| resources     |       3570 |
| environmental |       3553 |
| ...etc...     |        ... |


## Installation

On Debian/Ubuntu Linux, you’ll want these dependencies to build Python and Node.js:

```sh
> sudo apt-get update
> sudo apt-get upgrade
> sudo apt-get install -y build-essential pkg-config libxml2-dev libxslt-dev \
    libz-dev zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev \
    libreadline-dev libffi-dev libbz2-dev liblzma-dev libsqlite3-dev sqlite3
```

Install Pyenv and Python 3.7.x: https://github.com/pyenv/pyenv-installer or https://github.com/pyenv/pyenv

```sh
> curl https://pyenv.run | bash
# Then restart your shell
> pyenv install 3.7.4
> pyenv global 3.7.4
```

Install Nodenv and Node.js 12.x: https://github.com/nodenv/nodenv-installer or https://github.com/nodenv/nodenv

```sh
curl -fsSL https://raw.githubusercontent.com/nodenv/nodenv-installer/master/bin/nodenv-installer | bash
# Then restart your shell
> nodenv install 12.11.1
> nodenv global 12.11.1
```

Clone this repo:

```sh
> git clone xyz
```

Make a virtualenv and install python dependencies:

```sh
> cd xyz
> pyenv virtualenv 3.7.4 wm-term-counter
> pyenv activate wm-term-counter
> pip install --upgrade pip  # Make sure pip is up-to-date
> pip install -r requirements.txt
```

Install Node dependencies:

```sh
> cd readability-server
> npm install -g npm  # Make sure you have an up-to-date NPM
> npm install
```


## License & Copyright

Copyright (C) 2019 Environmental Data and Governance Initiative (EDGI)
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.0.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

See the [`LICENSE`](/LICENSE) file for details.

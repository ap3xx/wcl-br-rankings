# wcl-br-rankings

Project meant to ingest data from Warcraft Logs to query data for Brazilian WOTLK Classic guilds to have our own ranking.

## Architecture

TBD

## Ingestor

Based on Python, requests and PostgreSQL

## How to build

Run `make build-ingestor`.

## How to run

Make sure you have the necessary `.env` file at the root of the project and run `make run-ingestor`.  \
The required env variables are:
* `WCL_API_KEY`
* `DB_HOST`
* `DB_USER`
* `DB_PASSWORD`
* `DB_DATABASE`

## Webpage

Based on Flask + Flask Freeze to build a static website meant to run on github pages.

### How to build

Run `make build-web`.  \
The website will be available in `docs` folder.

**Make sure to run `make clean-web` before commiting to master. `docs` folder is not meant to be present at `main` branch, only**

### How to publish

Run `make publish-web`.  \
The script will commit changes to `gh-docs` branch and publish to github, which will then trigger the github pages deploy.



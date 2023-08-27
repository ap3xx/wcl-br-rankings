INGEST_IMAGE=wcl-br-rankings-ingest

ingest-prepare:
	mkdir -p .logs
	mkdir -p .backup

ingest-build:
	docker build -t $(INGEST_IMAGE) .

ingest-run: ingest-build
	docker stop $(INGEST_IMAGE) || true
	docker rm $(INGEST_IMAGE) || true
	docker run \
		--env-file ./.env \
		--volume $(shell pwd)/.logs:/opt/logs \
		--volume $(shell pwd)/.backup:/opt/backup \
		--name $(INGEST_IMAGE) \
		$(INGEST_IMAGE)

web-prepare:
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -r web-requirements.txt
	touch venv/_EXISTS

web-check-venv:
	test -f venv/_EXISTS

web-clean:
	rm -rf docs

web-build: web-check-venv
	python3 web/app.py build

web-build-fake: web-check-venv
	python3 web/app.py build fake

web-publish: web-check-venv
	@echo "Moving to gh-docs branch"
	git fetch -p
	git checkout gh-docs
	@echo "Updating code"
	git merge main --no-commit --no-ff
	@echo "Cleaning old docs"
	rm -rf docs
	@echo "Building new docs"
	python3 web/app.py build
	@echo "Pushing changes"
	git add docs/
	git commit -m "Publish new version: $$(date +%Y%m%d%H%M%S)"
	git push origin gh-docs
	git checkout main

ingest-and-publish: ingest-build ingest-run web-clean web-publish


INGEST_IMAGE=wcl-br-rankings-ingest

ingest-build:
	docker build -t $(INGEST_IMAGE) .

ingest-run: ingest-build
	docker stop $(INGEST_IMAGE) || true
	docker rm $(INGEST_IMAGE) || true
	docker run \
		--env-file ./.env \
		--volume ./.logs:/opt/logs \
		--volume ./.backup:/opt/backup \
		--name $(INGEST_IMAGE) \
		$(INGEST_IMAGE)

web-clean:
	rm -rf docs

web-build:
	python3 web/app.py build

web-build-fake:
	python3 web/app.py build fake

web-publish:
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


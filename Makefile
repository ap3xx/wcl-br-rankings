INGEST_IMAGE=wcl-br-rankings-ingest

build-ingest:
	docker build -t $(INGEST_IMAGE) .

run-ingest:
	docker stop $(INGEST_IMAGE) || true
	docker rm $(INGEST_IMAGE) || true
	docker run -d --env-file ./.env --name $(INGEST_IMAGE) $(INGEST_IMAGE)

logs-ingest:
	docker logs ${INGEST_IMAGE} -f

clean-web:
	rm -rf docs

build-web:
	python3 web/app.py build

build-web-fake:
	python3 web/app.py build fake

publish-web:
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


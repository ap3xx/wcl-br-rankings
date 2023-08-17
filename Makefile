INGESTOR_PROJECT=wcl-br-ingestor

build-ingestor:
	docker build -t $(INGESTOR_PROJECT) .

run-ingestor:
	docker stop $(INGESTOR_PROJECT) || true
	docker rm $(INGESTOR_PROJECT) || true
	docker run -d --env-file ./.env --name $(INGESTOR_PROJECT) $(INGESTOR_PROJECT)

logs-ingestor:
	docker logs ${INGESTOR_PROJECT} -f

clean-web:
	rm -rf docs

build-web:
	python3 web/app.py build

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


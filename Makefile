.DEFAULT: help
help:
	@echo "make test"
	@echo "	   run  pre-commit, test and coverage"
	@echo "make test-only"
	@echo "	   run tests only"
	@echo "make format"
	@echo "	   run  pre-commit"
	@echo "make clean"
	@echo "	   clean up pyc and caches"
	@echo "make clean-git"
	@echo "	   clean up git remote references"


.PHONY: clean
clean:
	@rm -rf */.pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .coverage
	@find . -name '.coverage.*' -exec rm -f {} +
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: test-only
test-only:
	pytest tests --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml --cov-report=html

.PHONY: format
format:
	pre-commit run --all-files

.PHONY: coverage
coverage:
	coverage report --include=./*py --omit='tests/*.py' -m

.PHONY: test
test: format test-only coverage

## Bump Version number in all files
.PHONY: bump_version
bump_version:
	pycalver bump --release=alpha

.PHONY: bump_release
bump_release:
	pycalver bump --release=final

.PHONY: dist_build
dist_build:
	python setup.py sdist bdist_wheel

.PHONY: dist_publish
dist_publish: bump_version dist_build

.PHONY: dist_release
dist_release: bump_release dist_build

.PHONY: clean-git
clean-git:
	git remote prune origin
	git branch --merged | egrep -v "(^\*|master)" | xargs git branch -d

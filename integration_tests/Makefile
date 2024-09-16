.PHONY: test-setup test egg-info auth-keys-test db

AUTH_DIR ?= ${LOCAL_GIT_REPOS}/wazo-auth/

test-setup: egg-info auth-keys-test

auth-keys-test:
	docker build --pull --no-cache -t wazo-auth-keys-test -f Dockerfile-auth-keys ..

db:
	docker build -f $(AUTH_DIR)/contribs/docker/Dockerfile-db -t wazoplatform/wazo-auth-db $(AUTH_DIR)

test:
	pytest -x

egg-info:
	cd .. && python setup.py egg_info

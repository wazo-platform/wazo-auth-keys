.PHONY: test-setup test egg-info pull-images auth-keys-test db

AUTH_DIR ?= ../../auth/

test-setup: egg-info pull-images auth-keys-test

pull-images:
	docker pull wazopbx/wait
	docker pull wazopbx/wazo-auth:buster
	docker pull wazopbx/wazo-auth-db:buster

auth-keys-test:
	docker build --pull --no-cache -t wazo-auth-keys-test -f Dockerfile-auth-keys ..

db:
	docker build -f $(AUTH_DIR)/contribs/docker/Dockerfile-db -t wazopbx/wazo-auth-db $(AUTH_DIR)

test:
	nosetests -x

egg-info:
	cd .. && python setup.py egg_info

-include .env

ENV ?=development
ROOT_DIR :=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT :=$(shell basename $(ROOT_DIR))
LOG_LEVEL ?= info

.PHONY: help sqitch sqitch-init psql

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sqitch: ## Sqitch container to executing a $cmd on a $db. e.g. `make sqitch db=demo cmd=status`
	test -n "${cmd}"
	test -n "${db}"
	docker run --rm --network hydro_network -v ${ROOT_DIR}:/repo -w /repo/${db} sqitch/sqitch ${cmd}
	# docker run --rm --network ${PROJECT}_default -v ${ROOT_DIR}:/repo -u $(id -u):$(id -g) -v /etc/passwd:/etc/passwd:ro -w /repo/${db} sqitch/sqitch ${cmd}

sqitch-init: ## Sqitch initialize a support postgresql database. e.g. `make sqitch-init db=demo password=password
	test -n "${db}"
	test -n "${password}"
ifeq ("$(wildcard ${db}/sqitch.conf)","")
	$(MAKE) sqitch cmd="init ${db} --uri https://github.com/mahrous-amer/${PROJECT}/tree/master/${db} --engine pg --top-dir /repo/${db} --target db:pg://postgres:${password}@postgres:5432/${db}"
else
	@echo already initialized!
endif

psql: ## psql container to run queries in $db e.g make psql db=demo
	test -n "${db}"
	docker run -it --rm --network hydropro_default bitnami/postgresql:15 psql -h postgres -U postgres -d ${db}
	# docker run -it --rm --network ${PROJECT}_default bitnami/postgresql:15 psql -h postgres -U postgres -d ${db}

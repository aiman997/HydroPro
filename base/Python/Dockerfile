FROM python3.9-alphine

ARG service_dir

COPY $service_dir /app/
WORKDIR /app

RUN if [ -n "$service_dir" ] ; then \
      echo "installing apt and pip deps" \
      && apt-get -y -q update \
      && DEBIAN_FRONTEND=noninteractive \
      && apt-get -y -q --no-install-recommends install $(cat aptfile) \
      && pip install -r requirments.txt; \
    fi

ENV PYTHONPATH="/app/lib"

ENTRYPOINT ["/usr/local/bin/python3"]
CMD ["bin/main.py"]
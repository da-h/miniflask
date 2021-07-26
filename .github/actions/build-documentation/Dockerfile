FROM python:slim

# install luke
RUN pip install lukeparser
RUN pip install colored

COPY entrypoint.sh /entrypoint.sh
WORKDIR /github/workspace

ENTRYPOINT ["/entrypoint.sh"]

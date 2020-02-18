FROM python:slim

# install luke
RUN pip install lukeparser

COPY entrypoint.sh /entrypoint.sh
WORKDIR /github/workspace

ENTRYPOINT ["/entrypoint.sh"]

FROM python:3-slim

ARG HOST=0.0.0.0
ARG PORT=8002
ENV HOST=${HOST}
ENV PORT=${PORT}
ENV PATH="/usr/local/bin:${PATH}"
# Update the base packages
RUN pip install --upgrade servicenow-api

# set the entrypoint to the start.sh script
ENTRYPOINT exec servicenow-mcp --transport=http --host=${HOST} --port=${PORT}

FROM public.ecr.aws/lambda/python:3.12-2025.03.11-arm64

RUN pip install --no-cache-dir roam-research-mcp==0.3.*

COPY entrypoint.sh ./

CMD ["entrypoint.handler"]

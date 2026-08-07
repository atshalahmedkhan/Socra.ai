FROM vllm/vllm-openai:v0.9.2
COPY scripts/validate-adapters.py start-primary.sh start-fallback.sh /opt/socra/
RUN chmod 0555 /opt/socra/start-primary.sh /opt/socra/start-fallback.sh
ENTRYPOINT ["/opt/socra/start-primary.sh"]

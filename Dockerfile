FROM selenium/standalone-chrome
RUN sudo apt-get update && sudo apt-get install -y \
    python3-pip
RUN pip install selenium
COPY ./run.sh /opt/sel/
COPY ./mfa-trigger.py /opt/sel/
COPY ./config.toml /opt/selenium/


# WORKDIR /opt/sel
# RUN '/opt/sel/run.sh'
# ENTRYPOINT ["/opt/sel/run.sh"]



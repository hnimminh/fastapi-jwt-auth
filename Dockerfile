# PLATFORM
FROM debian:buster
LABEL maintainer="Minh Minh"
ENV PLATFORM PyFast3
RUN apt-get update && apt-get install -y python3 python3-dev python3-pip build-essential libffi-dev wait-for-it
# AUTH
COPY ./auth /opt/auth
WORKDIR /opt/auth
RUN pip3 install -r requirements.txt
RUN chmod +x main.py
# EXECUTION
CMD ["./main.py"]

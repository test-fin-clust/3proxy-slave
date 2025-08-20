FROM ubuntu:latest
ARG CFG_NAME=./3proxy.cfg 
ARG CFG_PLACE=/etc/

LABEL "info"="3proxy:image-clear"
#stage integration 3proxy
COPY ${CFG_NAME} ${CFG_PLACE}
#stage cloning config file
COPY ./3proxy/bin/* /bin/
#Instal slave controler
COPY ./3proxy-slave/*.py /opt/

EXPOSE 3128

#install python
RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get clean

#integration config file
COPY ./cfg.yaml ${CFG_PLACE}

ENTRYPOINT ["python3", "/opt/Controller.py", "${CFG_PLACE}cfg.yaml", "3proxy", "${CFG_PLACE}${CFG_NAME}"]
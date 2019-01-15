FROM python:2.7

# Set the working directory to /home/user
WORKDIR /home/user

# Copy the current directory contents into the container
ADD ./ /home/user
ADD ./protoc /usr/bin
ADD ./gnmi/proto/gnmi_ext/gnmi_* /home/user/client_app/

ENV PYBINDPLUGIN=/usr/local/lib/python2.7/site-packages/pyangbind/plugin

# Utils
RUN apt-get update && apt-get install -y net-tools && apt-get install -y vim && apt-get install nano
RUN python -m pip install --no-binary=protobuf -I grpcio-tools==1.15.0
RUN python -m pip install pyang==1.7.5
RUN python -m pip install pyangbind==0.8.1
RUN python -m pip install influxdb==5.2.0
RUN python -m pip install absl-py==0.6.1


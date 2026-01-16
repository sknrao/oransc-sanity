##############################################################################
#
#   Copyright (c) 2019 AT&T Intellectual Property.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################
#
#   This source code is part of the near-RT RIC (RAN Intelligent Controller)
#   platform project (RICP).
#

FROM golang:1.20-bullseye as ubuntu

WORKDIR /opt/xappmock
COPY . . 
ENV PATH=$PATH:/usr/local/go/bin
# Install RMr library and dev files (use release channel)
ARG RMRVER=4.9.4
RUN apt-get update && apt-get install -y wget ca-certificates && update-ca-certificates
RUN wget -nv --content-disposition https://packagecloud.io/o-ran-sc/release/packages/debian/bullseye/rmr_${RMRVER}_amd64.deb/download.deb -O rmr_${RMRVER}_amd64.deb
RUN dpkg -i rmr_${RMRVER}_amd64.deb || apt-get -f install -y
RUN wget -nv --content-disposition https://packagecloud.io/o-ran-sc/release/packages/debian/bullseye/rmr-dev_${RMRVER}_amd64.deb/download.deb -O rmr-dev_${RMRVER}_amd64.deb
RUN dpkg -i rmr-dev_${RMRVER}_amd64.deb || apt-get -f install -y

RUN go build -o xappmock main/xappmock.go
    


FROM debian:bullseye-slim
COPY --from=ubuntu /opt/xappmock/xappmock /opt/xappmock/xappmock
COPY --from=ubuntu /opt/xappmock/resources /opt/xappmock/resources
COPY --from=ubuntu /usr/local/lib/librmr_si.so.4 /usr/local/lib/librmr_si.so.4
WORKDIR /opt/xappmock
ENV LD_LIBRARY_PATH=/usr/local/lib 
ENV RMR_SEED_RT=resources/router.txt
ENV RMR_PORT=5001
#CMD mkdir -p resources/conf  exec ./xappmock
CMD mkdir -p resources/conf &&  exec /bin/bash 

#!/bin/bash
    echo "START: Building Chaos"
    apt-get update
    apt-get install -y ca-certificates
    apt-get install -y build-essential
    apt-get install -y git
    wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz && rm go1.21.6.linux-amd64.tar.gz
    export GOROOT=/usr/local/go
    export GOPATH=/go
    export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
    export GO111MODULE=on
    export CGO_ENABLED=1
    mkdir -p /go/src
    mkdir -p /go/bin
    cd /tmp && go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest
    echo "END: Building Chaos"
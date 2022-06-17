#!/bin/bash
curl -XPOST "http://localhost:9090/2015-03-31/functions/function/invocations" -d '{"hello":"world"}'

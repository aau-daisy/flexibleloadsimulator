#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Must provide a jwt token"
    exit
fi

JWT_TOKEN=${1%/}

for i in {1..50}
do
  echo $i
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${JWT_TOKEN}" \
    -d '{"device_name": "CoffeeMaker1", "model_name": "ExponentialDecay", "params": {"lambda": 0.045, "p_active": 905, "p_peak": 990 }}' \
    "http://goflex-atp.cs.aau.dk:5000/api/v1.0/devices"
done

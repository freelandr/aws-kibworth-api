# Kibworth Ancestry project API

This repository contains the resources associated with the [Kibworth Ancestry Project](http://kibworth-web.s3-website-us-east-1.amazonaws.com/) API.

## Requirements

* Python 3.7
* Serverless Framework
* AWS account

## Usage

Deploy:
```
sls deploy
```
Consume:
```
export ENDPOINT=https://c71up49u6l.execute-api.us-east-1.amazonaws.com/prod
curl -X GET $ENDPOINT/details/[id]
curl -X GET $ENDPOINT/detailsByAddr/[street]
curl -X GET $ENDPOINT/detailsBySurname/[surname]
curl -X GET $ENDPOINT/detailsByFirstnameSurname/[firstnamesurname]
curl -X GET $ENDPOINT/census/[id]
curl -X GET $ENDPOINT/er/[id]
```

#!/bin/bash

sudo kill -9 `ps ax | grep python | awk '{print $1}'`

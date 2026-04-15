#!/usr/bin/env bash
echo "Starting api.."
sleep 3
bash -c 'while !</dev/tcp/importer-datastore/5432; do sleep 1; done; python -u api.py'

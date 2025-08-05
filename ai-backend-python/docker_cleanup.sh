#!/bin/bash
# Stop all running Docker containers
sudo docker stop $(sudo docker ps -q)
# Remove all stopped Docker containers
sudo docker rm $(sudo docker ps -a -q) 
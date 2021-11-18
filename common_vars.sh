#!/bin/bash

# Read port, origin, name, username and path to ssh key
port=$2
origin=$4
name=$6
username=$8
keyfile=${10}

# Update the path of the files that contain dns and replic IP addresses.
dns_file=./dns-hosts.txt
replica_file=./http-repls.txt
build_path=/home/$username/test
replica_build_path=$build_path/replica_source
dns_build_path=$build_path/dns_source

replica_cache_folder=replica_cache

# Insert the files and directories that have to be uploaded to the replica server here.
declare -a replica_source_files
replica_source_files=(httpserver utils $replica_cache_folder)


# Insert the files and directories that have to be uploaded to the dns server here.
declare -a dns_source_files
dns_source_files=(dnsserver utils http-repls.txt)


echo "PORT = $port"
echo "Origin = $origin"
echo "Name = $name"
echo "Username = $username"
echo "SSH-Key path = $keyfile"
echo "DNS IP Location = $dns_file"
echo "Replica IP Location = $replica_file"
echo "Replica Build Directory = $replica_build_path"
echo "DNS Build Directory = $dns_build_path"
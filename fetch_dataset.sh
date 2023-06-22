#!/bin/bash

wget -O ./dataset/dickens.bz2 https://sun.aei.polsl.pl/~sdeor/corpus/dickens.bz2
wget -O ./dataset/webster.bz2 https://sun.aei.polsl.pl/~sdeor/corpus/webster.bz2
wget -O ./dataset/enwik8.zip https://mattmahoney.net/dc/enwik8.zip
wget -O ./dataset/enwik9.zip https://mattmahoney.net/dc/enwik9.zip

bunzip2 ./dataset/dickens.bz2
bunzip2 ./dataset/webster.bz2
unzip ./dataset/enwik8.zip -d ./dataset
unzip ./dataset/enwik9.zip -d ./dataset

rm ./dataset/enwik8.zip
rm ./dataset/enwik9.zip
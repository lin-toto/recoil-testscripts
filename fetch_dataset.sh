#!/bin/bash

wget -O /work/dataset/dickens.bz2 https://sun.aei.polsl.pl/~sdeor/corpus/dickens.bz2
wget -O /work/dataset/webster.bz2 https://sun.aei.polsl.pl/~sdeor/corpus/webster.bz2
wget -O /work/dataset/enwik8.zip https://mattmahoney.net/dc/enwik8.zip
wget -O /work/dataset/enwik9.zip https://mattmahoney.net/dc/enwik9.zip

bunzip2 /work/dataset/dickens.bz2
bunzip2 /work/dataset/webster.bz2
unzip /work/dataset/enwik8.zip -d /work/dataset
unzip /work/dataset/enwik9.zip -d /work/dataset

rm /work/dataset/enwik8.zip
rm /work/dataset/enwik9.zip
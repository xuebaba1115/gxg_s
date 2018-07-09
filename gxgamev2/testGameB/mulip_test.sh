#!/bin/bash

  for i in {1..50};
  do
    python ./test.py -r $i -p $i  > /dev/null &
  done


  for i in {1..50};
  do
    python ./test.py -r $i -c join_room -p $i*10 > /dev/null &
  done  


  #kill -9 `cat ./pid`
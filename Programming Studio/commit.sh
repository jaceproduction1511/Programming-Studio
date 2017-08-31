#!/bin/bash
git pull origin master
git commit -a -m "Auto commit from c9"
git push origin master
rm *.pyc
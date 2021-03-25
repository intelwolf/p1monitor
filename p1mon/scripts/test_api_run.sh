#!/bin/bash
/home/p1mon/.local/bin/gunicorn -b localhost:10721 --workers 4 P1Api:app --reload

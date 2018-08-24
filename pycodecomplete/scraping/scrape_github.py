import os
import sys
import argparse
import json
import requests
import graphene

script_dir = os.path.dirname(__file__)
print(script_dir)

print(__file__)


token_file = '/home/kevin/.secrets/github_oath_token_06aug2018'

rel_path = '~/.secrets/github_oath_token_06aug2018'
abs_file_path = os.path.join(script_dir, rel_path)

print(os.path.isfile(token_file))

print(os.path.abspath(rel_path))
print(os.path.normpath(rel_path))
print(os.path.expanduser(rel_path))

with open(rel_path, 'r') as f:
    token = f.readline()

print(token)

#os.environ.values['GITHUB_API_TOKEN']
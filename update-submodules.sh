#!/bin/bash
exec git submodule foreach 'git pull origin $(basename $(pwd)) --tags'

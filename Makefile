# Makefile for whether
#
# Copyright (C) 2023 Simon Dobson
#
# This file is part of whether, a modular IoT weather station
#
# whether is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# whether is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with whether. If not, see <http://www.gnu.org/licenses/gpl.html>.

# The version we're building
VERSION = 0.1.0


# ----- Sources -----

# Source code
SOURCES_SETUP_IN = setup.py.in
SOURCES_CODE_INIT = \
	whether/__init__.py
SOURCES_CODE = \
	whether/ringbuffer.py \
	whether/utils.py \
	whether/sensortypes.py \
	whether/DHT22.py \
	whether/anemometer.py \
	whether/winddirection.py \
	whether/pijuice.py \
	whether/rpi.py \
	whether/homeassistant.py \
	winddirection.py
SOURCES_TESTS_INIT = \
	test/__init__.py
SOURCES_TESTS = \
	test/test_ringbuffers.py
SOURCES_CHECKS = \
	checks/dht22/code.py \
	checks/anemometer/code.py \
	checks/wind-direction/code.py \
SOURCES_MASTER = \
	code.py

# Library modules needed on the microcontroller
LIBRARIES = \
	adafruit_dht.mpy \
	adafruit_mcp3xxx \
	adafruit_logging.mpy

# Extras for the build and packaging system
SOURCES_EXTRA = \
	README.org \
	LICENSE \
	HISTORY
SOURCES_GENERATED = \
	winddirectioncalibration.py \
	TAGS

# Message broker
MQTT_NAME = mosquitto
MQTT_IMAGE = docker.io/library/eclipse-mosquitto:latest
MQTT_CONFIG = mosquitto.conf
MQTT_DOCKER_OPTIONS = \
	--name $(MQTT_NAME) \
	-p 1883:1883 -p 9001:9001

# Data collection and analysis
TZ = Europe/London
HOME_ASSISTANT_NAME = homeassistant
HOME_ASSISTANT_IMAGE = ghcr.io/home-assistant/home-assistant:stable
HOME_ASSISTANT_CONFIG_DIR = ./home-assistant
HOME_ASSISTANT_DOCKER_OPTIONS = \
	--name $(HOME_ASSISTANT_NAME) \
	--privileged \
	--restart=unless-stopped \
	-e TZ=$(TZ) \
	-v $(HOME_ASSISTANT_CONFIG_DIR):/config \
	--network=host


# ----- Tools -----

# Base commands
PYTHON = python3
PIP = pip
TOX = tox
COVERAGE = coverage
TWINE = twine
FLAKE8 = flake8
MYPY = mypy
GPG = gpg
GIT = git
ETAGS = etags
VIRTUALENV = $(PYTHON) -m venv
ACTIVATE = . $(VENV)/bin/activate
TR = tr
CAT = cat
SED = sed
RM = rm -fr
CP = cp
CHDIR = cd
MKDIR = mkdir -p
ZIP = zip -r
DOCKER = docker

# Makefile environment
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Files that are locally changed vs the remote repo
# (See https://unix.stackexchange.com/questions/155046/determine-if-git-working-directory-is-clean-from-a-script)
GIT_DIRTY = $(shell $(GIT) status --untracked-files=no --porcelain)

# The git branch we're currently working on
GIT_BRANCH = $(shell $(GIT) rev-parse --abbrev-ref HEAD 2>/dev/null)

# Root directory
ROOT = $(shell pwd)

# Requirements for running the library and for the development venv needed to build it
VENV = venv3
VENV_OPTIONS = --system-site-packages
REQUIREMENTS = requirements.txt
DEV_REQUIREMENTS = dev-requirements.txt

# Constructed commands
RUN_TESTS = $(TOX)
RUN_COVERAGE = $(COVERAGE) erase && $(COVERAGE) run -a setup.py test && $(COVERAGE) report -m --include '$(PACKAGENAME)*'


# ----- Top-level targets -----

# Default prints a help message
help:
	@make usage

# Run tests for all versions of Python we're interested in
test: env Makefile
	$(ACTIVATE) && $(RUN_TESTS)

# Run coverage checks over the test suite
coverage: env
	$(ACTIVATE) && $(RUN_COVERAGE)

# Run lint checks
lint: env
	$(ACTIVATE) && $(FLAKE8) $(SOURCES_CODE) --count --statistics --ignore=E501,E303,E301,E302,E261,E741,E265,E402

# Build a development venv from the requirements in the repo
.PHONY: env
env: $(VENV)

$(VENV):
	$(VIRTUALENV) $(VENV) $(VENV_OPTIONS)
	$(CAT) $(REQUIREMENTS) $(DEV_REQUIREMENTS) >$(VENV)/requirements.txt
	$(ACTIVATE) && $(PIP) install -U pip wheel && $(CHDIR) $(VENV) && $(PIP) install -r requirements.txt

# Perform sensor calibration
calibrate: whether/winddirectioncalibration.py

# Deploy the Home Assistant container
server:
	$(MKDIR) $(HOME_ASSISTANT_CONFIG_DIR)
	$(DOCKER) run -d $(HOME_ASSISTANT_DOCKER_OPTIONS) $(HOME_ASSISTANT_IMAGE)
	@echo "Home Assistant sitting on http://localhost:8123"

# Deploy the MQTT broker container
broker:
	$(DOCKER) run -d $(MQTT_DOCKER_OPTIONS) $(MQTT_IMAGE)

# Clean generated files
clean:
	$(RM) $(SOURCES_GENERATED)

# Clean up everything, including the computational environment (which is expensive to rebuild)
reallyclean: clean
	$(RM) $(VENV)


# ----- Generated files -----

# The tags file
TAGS:
	$(ETAGS) -o TAGS $(SOURCES_CODE)

# The wind direction calibration file
winddirectioncalibration.py:
	$(ACTIVATE) && $(PYTHON) scripts/calibrate-direction.py


# ----- Usage -----

define HELP_MESSAGE
Available targets:
   make env          create a development virtual environment
   make calibrate    perform sensor calibration
   make server       deploy a Home Assistant server locally
   make clean        clean up the build
   make reallyclean  clean up the virtualenv as well

endef
export HELP_MESSAGE

usage:
	@echo "$$HELP_MESSAGE"

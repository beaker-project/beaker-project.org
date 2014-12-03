SHELL = /bin/bash
BEAKER = ../beaker
BEAKER_GIT = $(BEAKER)/.git

# Symbolic targets defined in this Makefile:
# 	all-website: 	all the web site bits, *except* yum repos
# 	all:		all of the above, plus yum repos
.PHONY: all
all: all-website yum

include downloads.mk
include old-downloads.mk
include changelogs.mk
INABOX = \
     in-a-box/beaker.ks.html \
     in-a-box/beaker-setup.html \
     in-a-box/beaker-distros.html \
     in-a-box/beaker-virt.html

.PHONY: all-website
all-website: \
     releases/SHA1SUM \
     releases/index.html \
     releases/index.atom \
     $(DOWNLOADS) \
     $(OLD_DOWNLOADS) \
     $(CHANGELOGS) \
     $(INABOX)

downloads.mk: generate-downloads-mk.py git_tags.py
	./generate-downloads-mk.py $(BEAKER_GIT) >$@

changelogs.mk: generate-changelogs-mk.py git_tags.py
	./generate-changelogs-mk.py $(BEAKER_GIT) >$@

releases/index.html: releases/SHA1SUM generate-releases-index.py git_tags.py
	mkdir -p $(dir $@)
	./generate-releases-index.py --format=html $(BEAKER_GIT) >$@

releases/index.atom: releases/SHA1SUM generate-releases-index.py git_tags.py
	mkdir -p $(dir $@)
	./generate-releases-index.py --format=atom $(BEAKER_GIT) >$@

$(OLD_DOWNLOADS):
	mkdir -p $(dir $@)
	cd $(dir $@) && curl -# -R -f -O https://beaker-project.org/$@

# Release artefacts (tarballs and patches) must never change once they have 
# been published. So when "building" one, we always first try to grab it from 
# the public web site in case it has already been published. Only if it doesn't 
# exist should we *actually* build it from scratch here.

releases/%.tar.gz:
	mkdir -p $(dir $@)
	@echo "Trying to fetch release artefact $@" ; \
	curl -# -R -f -o$@ https://beaker-project.org/$@ ; result=$$? ; \
	if [ $$result -ne 22 ] ; then exit $$result ; fi ; \
	echo "Release artefact $@ not published, building it" ; \
	GIT_DIR=$(BEAKER_GIT) git archive --format=tar --prefix=$*/ $* | gzip >$@.tmp && mv $@.tmp $@

releases/%.tar.xz: releases/%.tar.gz
	mkdir -p $(dir $@)
	@echo "Trying to fetch release artefact $@" ; \
	curl -# -R -f -o$@ https://beaker-project.org/$@ ; result=$$? ; \
	if [ $$result -ne 22 ] ; then exit $$result ; fi ; \
	echo "Release artefact $@ not published, building it" ; \
	gunzip -c $< | xz >$@.tmp && mv $@.tmp $@

releases/SHA1SUM: $(DOWNLOADS) $(OLD_DOWNLOADS)
	mkdir -p $(dir $@)
	( cd $(dir $@) && ls -rv $(notdir $(DOWNLOADS)) $(notdir $(OLD_DOWNLOADS)) | xargs sha1sum ) >$@

yum::
	./build-yum-repos.py --config yum-repos.conf --dest $@

in-a-box/%.html: in-a-box/% shocco.sh
	./shocco.sh $< >$@

.PHONY: check clean
check:
# ideas: spell check everything, validate HTML, check for broken links, run sphinx linkcheck builder
	./check-yum-repos.py

clean:
	rm -f changelogs.mk downloads.mk releases/SHA1SUM releases/index.* $(INABOX)

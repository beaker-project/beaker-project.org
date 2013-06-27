SHELL = /bin/bash
BEAKER = beaker-branches/master
BEAKER_GIT = .git/modules/beaker-branches/master
SPHINXBUILD = $(shell command -v sphinx-1.0-build sphinx-build)
SPHINXBUILDOPTS =

# Symbolic targets defined in this Makefile:
# 	all-docs: 	all branches of the Sphinx docs from Beaker git
# 	all-website: 	all the web site bits, *except* yum repos
# 	all:		all of the above, plus yum repos
.PHONY: all
all: all-docs all-website yum

ARTICLES = COPYING.html cobbler-migration.html

include downloads.mk
include old-downloads.mk
include changelogs.mk

include docs.mk # defines all-docs target

# treat warnings as errors only for the released docs
docs: SPHINXBUILDOPTS += -W

.PHONY: all-website
all-website: \
     dev \
     schema/beaker-job.rng \
     releases/SHA1SUM \
     releases/index.html \
     releases/index.atom \
     $(DOWNLOADS) \
     $(OLD_DOWNLOADS) \
     $(CHANGELOGS) \
     in-a-box/beaker.ks.html \
     in-a-box/beaker-setup.html \
     in-a-box/beaker-distros.html \
     in-a-box/beaker-virt.html \
     $(ARTICLES)

docs.mk: beaker-branches generate-docs-mk.sh
	./generate-docs-mk.sh >$@

.PHONY: dev
dev: SPHINXBUILDOPTS += -W
dev:
	$(SPHINXBUILD) $(SPHINXBUILDOPTS) -c $@ -b html ./dev/ $@/

schema/beaker-job.rng: $(BEAKER)/Common/bkr/common/schema/beaker-job.rng
	mkdir -p $(dir $@)
	cp -p $< $@

.PHONY:
git-rev-beaker-master:
	read old_sha <$@ ; \
	new_sha=$$(git ls-tree HEAD beaker-branches/master | awk '{ print $$3 }') && \
	if [[ $$old_sha != $$new_sha ]] ; then echo $$new_sha >$@ ; fi

downloads.mk: git-rev-beaker-master generate-downloads-mk.py git_tags.py
	./generate-downloads-mk.py $(BEAKER_GIT) >$@

changelogs.mk: git-rev-beaker-master generate-changelogs-mk.py git_tags.py
	./generate-changelogs-mk.py $(BEAKER_GIT) >$@

releases/index.html: git-rev-beaker-master releases/SHA1SUM generate-releases-index.py git_tags.py docs
	mkdir -p $(dir $@)
	./generate-releases-index.py --format=html $(BEAKER_GIT) >$@

releases/index.atom: git-rev-beaker-master releases/SHA1SUM generate-releases-index.py git_tags.py
	mkdir -p $(dir $@)
	./generate-releases-index.py --format=atom $(BEAKER_GIT) >$@

$(OLD_DOWNLOADS):
	mkdir -p $(dir $@)
	cd $(dir $@) && curl -# -R -f -O http://beaker-project.org/$@

# Release artefacts (tarballs and patches) must never change once they have 
# been published. So when "building" one, we always first try to grab it from 
# the public web site in case it has already been published. Only if it doesn't 
# exist should we *actually* build it from scratch here.

releases/%.tar.gz:
	mkdir -p $(dir $@)
	@echo "Trying to fetch release artefact $@" ; \
	curl -# -R -f -o$@ http://beaker-project.org/$@ ; result=$$? ; \
	if [ $$result -ne 22 ] ; then exit $$result ; fi ; \
	echo "Release artefact $@ not published, building it" ; \
	( cd $(BEAKER) && mkdir -p /tmp/tito && flock /tmp/tito tito build --tgz --tag=$*-1 ) && cp /tmp/tito/$*.tar.gz $@

releases/%.tar.xz: releases/%.tar.gz
	mkdir -p $(dir $@)
	@echo "Trying to fetch release artefact $@" ; \
	curl -# -R -f -o$@ http://beaker-project.org/$@ ; result=$$? ; \
	if [ $$result -ne 22 ] ; then exit $$result ; fi ; \
	echo "Release artefact $@ not published, building it" ; \
	gunzip -c $< | xz >$@

releases/%.patch:
	mkdir -p $(dir $@)
	@echo "Trying to fetch release artefact $@" ; \
	curl -# -R -f -o$@ http://beaker-project.org/$@ ; result=$$? ; \
	if [ $$result -ne 22 ] ; then exit $$result ; fi ; \
	echo "Release artefact $@ not published, building it" ; \
	( cd $(BEAKER) && mkdir -p /tmp/tito && flock /tmp/tito tito build --tgz --tag=$* ) && cp /tmp/tito/$*.patch $@

releases/SHA1SUM: $(DOWNLOADS) $(OLD_DOWNLOADS)
	mkdir -p $(dir $@)
	( cd $(dir $@) && ls -rv $(notdir $(DOWNLOADS)) $(notdir $(OLD_DOWNLOADS)) | xargs sha1sum ) >$@

yum::
	./build-yum-repos.py --config yum-repos.conf --dest $@

in-a-box/%.html: in-a-box/% shocco.sh
	./shocco.sh $< >$@

# This is annoying... at some point pandoc started ignoring the -5 option,
# instead you have to specify -t html5 to select HTML5 output.
PANDOC_OUTPUT_OPTS := $(if $(shell pandoc --help | grep 'Output formats:.*html5'),-t html5,-t html -5)

%.html: %.txt pandoc-header.html pandoc-before-body.html pandoc-after-body.html pandoc-fixes.py
	pandoc -f markdown $(PANDOC_OUTPUT_OPTS) --standalone --section-divs \
	    --smart --variable=lang=en --css=style.css \
	    --include-in-header=pandoc-header.html \
	    --toc \
	    --include-before-body=pandoc-before-body.html \
	    --include-after-body=pandoc-after-body.html \
	    <$< | ./pandoc-fixes.py >$@

.PHONY: check clean
check:
# ideas: spell check everything, validate HTML, check for broken links, run sphinx linkcheck builder
	./check-yum-repos.py

clean:
	rm changelogs.mk docs.mk downloads.mk
	rm releases/SHA1SUM releases/index.*

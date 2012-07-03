MAJOR_VERSION = 0
BEAKER ?= ../beaker
SPHINXBUILD = $(shell sh -c 'command -v sphinx-1.0-build sphinx-build')
SPHINXBUILDOPTS = -W
SHOCCO=$(HOME)/work/shocco/shocco # XXX fix this

ARTICLES = COPYING.html dev-guide.html cobbler-migration.html

include releases.mk
OLD_TARBALLS = \
    releases/beaker-0.6.16.tar.bz2 \
    releases/beaker-0.6.1.tar.gz \
    releases/beaker-0.6.1.tar.bz2 \
    releases/beaker-0.5.7.tar.bz2 \
    releases/beaker-0.4.75.tar.bz2 \
    releases/beaker-0.4.3.tar.bz2 \
    releases/beaker-0.4.tar.bz2

.PHONY: all
all: guide server-api man yum \
     schema/beaker-job.rng \
     releases/SHA1SUM releases/index.html $(DOWNLOADS) \
     in-a-box/beaker.ks.html \
     in-a-box/beaker-setup.html \
     in-a-box/beaker-distros.html \
     in-a-box/beaker-virt.html \
     $(ARTICLES)

guide::
	# publican doesn't let us specify source or dest dirs, grumble
	( cd $(BEAKER)/pub_doc/Beaker_Guide && \
	  publican build --publish --common_content=../publican-brand --formats=html --langs=en-US ) && \
	rm -rf $@ && \
	cp -r $(BEAKER)/pub_doc/Beaker_Guide/publish/en-US/Beaker/$(MAJOR_VERSION)/html/Deployment_Guide $@

# This __requires__ insanity is needed in Fedora if multiple versions of CherryPy are installed.
server-api::
	env BEAKER=$(abspath $(BEAKER)) PYTHONPATH=$(BEAKER)/Common:$(BEAKER)/Server \
	python -c '__requires__ = ["TurboGears"]; import pkg_resources; execfile("$(SPHINXBUILD)")' \
	$(SPHINXBUILDOPTS) -c $@ -b html $(BEAKER)/Server/apidoc/ $@/

man::
	env BEAKER=$(abspath $(BEAKER)) PYTHONPATH=$(BEAKER)/Common:$(BEAKER)/Client/src \
	$(SPHINXBUILD) $(SPHINXBUILDOPTS) -c $@ -b html $(BEAKER)/Client/doc/ $@/

schema/beaker-job.rng: $(BEAKER)/Common/bkr/common/schema/beaker-job.rng
	mkdir -p $(dir $@)
	cp -p $< $@

releases.mk: $(BEAKER)/beaker.spec generate-releases-mk.py changelog.py
	./generate-releases-mk.py <$< >$@

releases/index.html: $(BEAKER)/beaker.spec releases/SHA1SUM generate-releases-index.py changelog.py
	mkdir -p $(dir $@)
	./generate-releases-index.py <$< >$@

releases/%.tar.gz:
	mkdir -p $(dir $@)
	( cd $(BEAKER) && flock /tmp/tito tito build --tgz --tag=$*-1 ) && cp /tmp/tito/$*.tar.gz $@

releases/%.tar.xz: releases/%.tar.gz
	mkdir -p $(dir $@)
	gunzip -c $< | xz >$@

releases/%.patch:
	mkdir -p $(dir $@)
	( cd $(BEAKER) && flock /tmp/tito tito build --tgz --tag=$* ) && cp /tmp/tito/$*.patch $@

releases/SHA1SUM: $(DOWNLOADS) releases.mk
	mkdir -p $(dir $@)
	( cd $(dir $@) && ls -rv $(notdir $(DOWNLOADS)) $(notdir $(OLD_TARBALLS)) | xargs sha1sum ) >$@

yum::
	./build-yum-repos.py --config yum-repos.conf --dest $@

in-a-box/%.html: in-a-box/%
	$(SHOCCO) $< >$@

%.html: %.txt pandoc-before-body.html pandoc-after-body.html
	pandoc -f markdown -t html -5 --standalone --section-divs --smart --css=style.css \
	    --include-in-header=pandoc-header.html \
	    --include-before-body=pandoc-before-body.html \
	    --include-after-body=pandoc-after-body.html \
	    <$< >$@

.PHONY: check
check:
# ideas: spell check everything, validate HTML, check for broken links
	./check-yum-repos.py

.PHONY: publish
publish:
	env BEAKER="$(abspath $(BEAKER))" ./publish.sh published

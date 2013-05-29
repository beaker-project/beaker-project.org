#!/bin/bash
# vim: set noexpandtab:

dests=()
for branch_dir in beaker-branches/* ; do
    if [[ "$branch_dir" == */master ]] ; then
        dest=docs
    else
        dest="docs-$(basename "$branch_dir")"
    fi
    dests+=("$dest")
    echo ".PHONY: $dest"
    echo "$dest: $branch_dir dev"
    cat <<"EOF"
	mkdir -p $@
        # The templated version moved in Beaker 0.13. We ensure
        # both are generated for the sake of older branches.
	$(MAKE) -C $</Common bkr/__init__.py bkr/common/__init__.py
	# This __requires__ insanity is needed in Fedora if multiple versions of CherryPy are installed.
	BEAKER=$(abspath $<) \
	PYTHONPATH=$</Common:$</Server:$</Client/src \
	python -c '__requires__ = ["CherryPy < 3.0"]; import pkg_resources; execfile("$(SPHINXBUILD)")' \
	$(SPHINXBUILDOPTS) -c docs/ -b html $</documentation/ $@/
EOF
    echo
done
echo ".PHONY: all-docs"
echo "all-docs: ${dests[@]}"

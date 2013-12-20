#!/bin/bash

set -ex

if [[ $1 == "--skip-yum" ]] ; then
    skip_yum=1
fi

# Make sure we have the latest published version.
git fetch beaker-project.org:/srv/www/beaker-project.org/git master:published

# This is the SHA of the current tip of the destination branch,
# on top of which we will commit our new version.
parent=$(git rev-parse refs/heads/published)

if [ "$(git rev-parse HEAD)" = "$parent" ] ; then
    echo "Don't checkout the published branch!" >&2
    exit 1
fi

# Sanity check: the commit from which the current destination branch was built,
# must be an ancestor of the commit we are building from now.
if ! git rev-list HEAD | grep -q $(git show $parent:git-rev) ; then
    echo "Error: tip of 'published' was built from" >&2
    git show $parent:git-rev >&2
    echo "which is not an ancestor of HEAD" >&2
    exit 1
fi

D=/tmp/beaker-project.org-publish-work-tree
rm -rf "$D"
mkdir -p "$D"
# check out HEAD of beaker-project.org into $D
GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish GIT_WORK_TREE="$D" git read-tree HEAD
GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish GIT_WORK_TREE="$D" git checkout-index -a -f
GIT_DIR=$(pwd)/.git git rev-parse HEAD >"$D/git-rev"
# check out each branch submodule of beaker
# (can't use git-submodule for this since it complains about needing a work tree)
GIT_DIR=$(pwd)/.git git ls-tree -r HEAD | grep ^160000 |
while read mode type sha path ; do
    GIT_DIR=$(pwd)/$path/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish-beaker GIT_WORK_TREE="$D" git read-tree --empty
    GIT_DIR=$(pwd)/$path/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish-beaker GIT_WORK_TREE="$D" git read-tree --prefix=$path/ $sha
    GIT_DIR=$(pwd)/$path/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish-beaker GIT_WORK_TREE="$D" git checkout-index -a -f
    echo $sha >"$D/git-rev-beaker-$(basename $path)"
done

# Carry existing release artifacts and RPMs over to the build directory,
# because they are quite expensive to build/fetch and they never change.
# This is purely an optimisation so ignore failures.
mkdir -p "$D/releases" || :
cp -p --reflink=auto releases/*.tar.* releases/*.patch "$D/releases/" || :
mkdir -p "$D/yum/rpms" || :
cp -p --reflink=auto yum/rpms/*.rpm "$D/yum/rpms/" || :

if [[ -n "$skip_yum" ]] ; then
    # check out published yum subdir into $D/yum, we are not going to rebuild it
    rm -rf "$D/yum/rpms"
    GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish-yum GIT_WORK_TREE="$D/yum" git read-tree published:yum
    GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish-yum GIT_WORK_TREE="$D/yum" git checkout-index -a -f
    make -j4 -C "$D" BEAKER_GIT="$(pwd)/.git/modules/beaker-branches/master" all-docs all-website
else
    make -j4 -C "$D" BEAKER_GIT="$(pwd)/.git/modules/beaker-branches/master" all
fi

# Clean out junk that we don't want to publish.
find "$D" -name .doctrees -exec rm -r {} \+

GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish GIT_WORK_TREE="$D" git add -f -A "$D"
tree=$(GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish git write-tree)
commit=$(git commit-tree $tree -p $parent -p $(git rev-parse HEAD) <<EOF
Automatic commit of generated web site from $(git rev-parse HEAD)
EOF
)

# Sanity check: did the new commit delete or change any lines in 
# releases/SHA1SUM? This is verboten!
deleted=$(git diff $parent..$commit --numstat -- releases/SHA1SUM | cut -f1)
if [[ "$deleted" -gt 0 ]] ; then
    echo "Checksum of released artefact changed!"
    git diff $parent..$commit -- releases/SHA1SUM | cat
    exit 1
fi

git update-ref refs/heads/published $commit $parent

rm -rf "$D"

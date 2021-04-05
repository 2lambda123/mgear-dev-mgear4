# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This sphinx extension makes the issue numbers in the changelog into links to
GitHub issues.
"""

from __future__ import print_function

import re

from docutils.nodes import Text, reference

BLOCK_PATTERN = re.compile('\[.+#.+\]', flags=re.DOTALL)
ISSUE_PATTERN = re.compile('#[0-9]+')
REPO_PATTERN = re.compile('[a-zA-Z_]+#') #"^[a-zA-Z0-9_]*$"


def process_changelog_links(app, doctree, docname):

    # if 'changelog' in docname and app.config.github_issues_url is not None:
    if app.config.github_issues_url is not None:

        for item in doctree.traverse():

            if isinstance(item, Text):

                # We build a new list of items to replace the current item. If
                # a link is found, we need to use a 'reference' item.
                children = []

                # First cycle through blocks of issues (delimited by []) then
                # iterate inside each one to find the individual issues.
                prev_block_end = 0
                for block in BLOCK_PATTERN.finditer(item):
                    block_start, block_end = block.start(), block.end()
                    children.append(Text(item[prev_block_end:block_start]))
                    block = item[block_start:block_end]
                    prev_end = 0
                    for m, rm in zip(ISSUE_PATTERN.finditer(block), REPO_PATTERN.finditer(block)):
                        start, end = m.start(), m.end()
                        children.append(Text(block[prev_end:start]))
                        issue_number = block[start:end]

                        start2, end2 = rm.start(),rm.end()
                        # children.append(Text(block[prev_end:start]))
                        repo = block[start2:end2][:-1]
                        aurl = app.config.github_issues_url.replace("mgear_dist", repo)
                        print(aurl)

                        children.append(reference(text=issue_number,
                                                  name=issue_number,
                                                  refuri=aurl + issue_number[1:]))
                        print(issue_number)
                        print(repo)
                        print(item)

                    # for m in REPO_PATTERN.finditer(block):
                    #     start, end = m.start(), m.end()
                    #     children.append(Text(block[prev_end:start]))
                    #     issue_number = block[start:end]
                    #     children.append(reference(text=issue_number,
                    #                               name=issue_number,
                    #                               refuri=app.config.github_issues_url + issue_number[1:]))
                    #     # print(app.config.github_issues_url)
                    #     print(issue_number)
                    #     # print(item)

                        prev_end = end


                    prev_block_end = block_end

                    # If no issues were found, this adds the whole item,
                    # otherwise it adds the remaining text.
                    children.append(Text(block[prev_end:block_end]))

                # If no blocks were found, this adds the whole item, otherwise
                # it adds the remaining text.
                children.append(Text(item[prev_block_end:]))

                # Replace item by the new list of items we have generated,
                # which may contain links.
                item.parent.replace(item, children)


def setup(app):
    app.connect('doctree-resolved', process_changelog_links)
    app.add_config_value('github_issues_url', None, True)

""" A set of tools to help organize my pinboard notes of urls. """

import pinboard, json

#notes:
#description is basically waht i search by in the bookmark bar
#extended is searchable in pinboard
#and tags are just folders so should match my other folders.

#pseudocode
#for each tag that i use, if its a bookmark i want to consolidate
#i need to get all bookmarks that use that tag
#in its tags, i need to remove that tag from it and move that tag to its extended field
#(assuming extended is description and description is title)
#i need to add its consolidation tag *if it doesn't already have it*
#i need to update the bookmark and move on to the next


def remap_bookmark(bookmark, old_tag, tag_map):
    """
    Removes a tag from a bookmark and adds its mapped tag from tag map. Moves the old tag to the
    extended field for future searching, and updates the tag. Only adds parent if its no
    already in the list of tags.
    """
    if old_tag not in bookmark.tags:
        return


    #add old tag to the extended section (which is description, whereas description is title) for
    #searchability add with space at the end if there's something already in description, otherwise
    #just add it without space
    if bookmark.extended == '':
        bookmark.extended = old_tag
    else:
        bookmark.extended = bookmark.extended + " " + old_tag

    #removes old tag
    bookmark.tags.remove(old_tag)

    new_tag = tag_map.get_mapping(old_tag)

    #adds new tag if not in there already
    if new_tag not in bookmark.tags:
        bookmark.tags.append(new_tag)

    #updates
    try:
        bookmark.save()
    except TypeError as error:
        #This is just an error in how the library parses the response since its not unicode aware.
        #This is why you don't type check :tableflip:
        assert error.args == ("the JSON object must be str, not 'bytes'",)

def remap_all_bookmarks(pinboard_, tag_map):
    """
    For each tag that needs to be remapped, find the bookmarks with that tag, and remap them.
    """

    bookmarks = get_all_bookmarks(pinboard_)

    for bookmark in bookmarks:
        for tag in tag_map.all_mapped_tags():
            remap_bookmark(bookmark, tag, tag_map)

def get_all_bookmarks(pinboard_):
    """ Returns all bookmarks, parsed manually as pinboard isn't happy with utf-8 """
    return [
        pinboard.Bookmark(payload, pinboard_.token)
        for payload
        in json.loads(
            pinboard_.posts.all(parse_response=False).readall().decode("utf-8")
        )
    ]

def get_all_tags(pinboard_):
    """ Returns all tags used in a pinboard. """

    bookmarks = get_all_bookmarks(pinboard_)

    tags = set()

    for bookmark in bookmarks:
        for tag in bookmark.tags:
            tags.add(tag)

    return tags

class TagMap(object):
    """ Holds tags that need to be remapped to their 'parents' """

    def __init__(self, dict_, default_parent_tags):
        self._dict = dict_
        self._default_parent_tags = default_parent_tags

    def all_mapped_tags(self):
        return self._dict.keys()

    def all_parent_tags(self):
        return list(self._dict.values()) + self._default_parent_tags

    def add_mapping(self, tag, parent):
        """ Updates this tag map with a new mapped tag and parent pair. """
        self._dict.update({tag: parent})

    def is_mapped(self, tag):
        return tag in self._dict

    def unmapped_tags(self, tag_list):
        """ Returns all tags that are unmapped from a list. """
        return [
            tag
            for tag in tag_list
            if tag not in self.all_mapped_tags() and tag not in self.all_parent_tags()
        ]

    def get_mapping(self, tag):
        return self._dict[tag]

TAG_MAP = TagMap(
    {
    },
    [
        "productivity",
        "management",
        "career",
        "books",
        "programming",
        "ensemble",
        "fitness",
        "family",
        "fashion",
        "guns",
        "music",
        "games",
        "philosophy",
        "rants",
        "memes",
        "wishlist",
        "bookproject",
        "curriculum",
        "simplifi",
    ]
)


def main():
    """ Run as script """
    board = pinboard.Pinboard(token="austinwiltshire:e8658fb0fea065330cab")
    remap_all_bookmarks(board, TAG_MAP)

if __name__ == "__main__":
    main()

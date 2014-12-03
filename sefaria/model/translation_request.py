"""
translation_request.py
Writes to MongoDB Collection: requests
"""
from . import abstract as abst
from sefaria.model.text import Ref
from sefaria.counts import is_ref_translated
from sefaria.system.database import db


class TranslationRequest(abst.AbstractMongoRecord):
    """
    A Request for a section of text to be translated.
    """
    collection   = 'translationRequests'
    history_noun = 'translationRequest'

    required_attrs = [
        "ref",
        "requesters",
        "request_count",
        "completed",
    ]
    optional_attrs = []

    def _init_defaults(self):
        self.requesters = []
        self.completed  = False

    def save(self):
        self.requesters    = list(set(self.requesters))
        self.request_count = len(self.requesters)
        super(TranslationRequest, self).save()

    def _normalize(self):
        self.ref = Ref(self.ref).normal()

    @staticmethod
    def make_request(tref, uid):
        """
        Updates existing TranslationRequest for tref with uid if present,
        creates a new object if not.
        """
        tr = TranslationRequest().load({"ref": tref})
        if tr:
            tr.requesters.append(uid)
        else:
            tr = TranslationRequest({"ref": tref, "requesters": [uid]})
        tr.save()
        return tr

    @staticmethod
    def remove_request(tref, uid):
        """
        Remove uid from TranslationRequest for tref if there are other requesters,
        delete TranslationRequest if not.
        """
        tr = TranslationRequest().load({"ref": tref})
        if tr:
            tr.requesters.remove(uid)
            if len(tr.requesters):
                tr.save()
            else:
                tr.delete()


class TranslationRequestSet(abst.AbstractMongoSet):
    recordClass = TranslationRequest

    """ Default sort
    def __init__(self, query={}, page=0, limit=0, sort=[["request_count", 1]]):
        super(TranslationRequestSet, self).__init__(query, page, limit, sort)
    """

def add_translation_requests_from_source_sheets():
    """
    Walks through all source sheets, checking for included refs that are untranslated.
    Adds the user ID of the sheet owner as a request for each untranslated ref.
    """
    sheets = db.sheets.find()
    for sheet in sheets:
        for ref in sheet.get("included_refs", []):
            try:
                r = Ref(ref)
                if ref and not is_ref_translated(ref):
                    TranslationRequest.make_request(ref, sheet["owner"])
            except:
                continue


"""
def process_index_title_change_in_links(indx, **kwargs):
    if indx.is_commentary():
        pattern = r'^{} on '.format(re.escape(kwargs["old"]))
    else:
        commentators = text.IndexSet({"categories.0": "Commentary"}).distinct("title")
        pattern = r"(^{} \d)|(^({}) on {} \d)".format(re.escape(kwargs["old"]), "|".join(commentators), re.escape(kwargs["old"]))
        #pattern = r'(^{} \d)|( on {} \d)'.format(re.escape(kwargs["old"]), re.escape(kwargs["old"]))
    links = LinkSet({"refs": {"$regex": pattern}})
    for l in links:
        l.refs = [r.replace(kwargs["old"], kwargs["new"], 1) if re.search(pattern, r) else r for r in l.refs]
        l.save()


def process_index_delete_in_links(indx, **kwargs):
    if indx.is_commentary():
        pattern = r'^{} on '.format(re.escape(indx.title))
    else:
        commentators = text.IndexSet({"categories.0": "Commentary"}).distinct("title")
        pattern = r"(^{} \d)|^({}) on {} \d".format(re.escape(indx.title), "|".join(commentators), re.escape(indx.title))
    LinkSet({"refs": {"$regex": pattern}}).delete()
"""
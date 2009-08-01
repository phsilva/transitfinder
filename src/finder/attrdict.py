
class AttrDict (dict):

    def __getattr__ (self, attr):
        if attr in self:
            return self[attr]

        raise AttributeError("Unknown attribute %s" % attr)

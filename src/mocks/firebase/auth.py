class Auth:
    def __init__(self):
        self.user = {}

    def update_user(self, uid, display_name=None, disabled=None, photo_url=None):
        self.user["uid"] = uid
        self.user["display_name"] = display_name
        self.user["disabled"] = disabled
        self.user["photo_url"] = photo_url
        return self.user

    def set_custom_user_claims(self, uid, custom_claims):
        self.user["uid"] = uid
        self.user["custom_claims"] = custom_claims
        return self.user

    def get_user(self, uid):
        try:
            return self.user[uid]
        except KeyError:
            return {"display_name": "default_display_name"}


auth_mock = Auth()

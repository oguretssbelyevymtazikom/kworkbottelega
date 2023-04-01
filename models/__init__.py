from . import database, user, message, link, referral, want, payment, blacklist, _useful


database._Base.metadata.create_all(database._Engine)

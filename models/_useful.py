from . import blacklist, link, message, payment, referral, user, want


def strong_delete_user(user_id):
    """Полное удаление пользователя из системы"""
    User = user.get(user_id)

    if not User:
        return False
    
    UserBlacklists = blacklist.get_all_by_owner(user_id)
    if UserBlacklists:
        for UserBlacklist in UserBlacklists:
            blacklist.delete(UserBlacklist.id)

    UserLinks = link.get_all_by_owner(user_id)
    if UserLinks:
        for UserLink in UserLinks:
            link.delete(UserLink.id)

    UserMessages = message.get_all_by_user(user_id)
    if UserMessages:
        for UserMessage in UserMessages:
            message.delete(UserMessage.user_id, UserMessage.message_id)

    UserPayments = payment.get_all_by_client(user_id)
    if UserPayments:
        for UserPayment in UserPayments:
            payment.delete(UserPayment.payment_id)

    UserReferrals = referral.get_all_by_owner(user_id)
    if UserReferrals:
        for UserReferral in UserReferrals:
            referral.delete(UserReferral.referral_id)
    
from .. import crud


def parse_args(args, after_duration):
    if after_duration is None:
        return args, None

    args = args.split()
    if len(args) > 1:
        duration, *reason = args
        reason = ' '.join(reason)

        if duration.replace('.', '', 1).isdigit():
            duration = float(duration)
        else:
            reason = duration + ' ' + reason
            duration = 0
    elif len(args) == 1:
        reason = args[0]
        duration = None
    else:
        reason = None
        duration = None

    return reason, duration


def get_value(reason, duration, expiration_date):
    value = ''

    if reason:
        value += f'\n**Razón**: {reason}'

    if expiration_date:
        value += f'\n**Duración**: {duration} minutos'

    return value


async def unmoderate(
        func: callable, member_id: int, guild_id: int, moderation_type: str, expiration_needed: bool = True
):
    if func:
        moderation = crud.get_moderation(moderation_type, member_id, guild_id)

        if moderation.expired or not expiration_needed:
            await func()
            crud.revoke_moderation(moderation)

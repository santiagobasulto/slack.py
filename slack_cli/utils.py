def yes_no(option, capitalized=True):
    answer = 'Yes' if option else 'No'
    return answer.lower() if not capitalized else answer


def default_options(**kwargs):
    return {k: v for k, v in kwargs.items() if v}

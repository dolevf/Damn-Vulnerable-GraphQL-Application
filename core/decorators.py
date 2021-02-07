# graphql-utilities library
from functools import wraps

def run_only_once(resolve_func):
    @wraps(resolve_func)
    def wrapper(self, next, root, info, *args, **kwargs):
        has_context = info.context is not None
        decorator_name = "__{}_run__".format(self.__class__.__name__)

        if has_context:
            if isinstance(info.context, dict) and not info.context.get(decorator_name, False):
                info.context[decorator_name] = True
                return resolve_func(self, next, root, info, *args, **kwargs)
            elif not isinstance(info.context, dict) and not getattr(info.context, decorator_name, False):
                setattr(info.context, decorator_name, True)
                return resolve_func(self, next, root, info, *args, **kwargs)

        return next(root, info, *args, **kwargs)

    return wrapper

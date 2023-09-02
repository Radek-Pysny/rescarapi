from typing import Any, TypeAlias


any_logged_value = object()


LogList: TypeAlias = list[dict[str, Any]]


def _show_args(**kwargs) -> str:
    args = []
    for k, v in kwargs.items():
        if v is any_logged_value:
            args.append(f'{k}: ANYTHING')
        else:
            args.append(f'{k}: {v!r}')

    return '{' + ', '.join(args) + '}'


def _show_logs(logs: LogList, max_logs: int = 3) -> str:
    if not logs:
        return ''

    indent = ' ' * 10
    lines = []

    if len(logs) > 1:
        lines.append('')

    lines.extend(f'{indent}{_show_args(**log)}' for log in logs[:max_logs])

    if len(logs) > max_logs:
        lines.append(f'{indent}... {len(logs) - max_logs} more logs')

    if len(logs) > 1:
        lines.append('')

    return '\n'.join(lines)


def found_log(logs: LogList, **kwargs) -> bool:
    for log in logs:
        for k, v in kwargs.items():
            if k not in log:
                break

            if v is any_logged_value:
                continue

            if log[k] != v:
                break
        else:
            return True

    assert False, f'''not found {_show_args(**kwargs)} in [{_show_logs(logs)}]'''


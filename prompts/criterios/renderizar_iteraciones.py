from pathlib import Path


def _render(version, context):
    v = context['vars']
    t = Path(__file__).with_name(f'{version}.txt').read_text(encoding='utf-8')
    return t.replace('{{historia_id}}', v['historia_id']).replace('{{historia}}', v['historia'])


def prompt_v2(context):
    return _render('v2', context)


def prompt_v3(context):
    return _render('v3', context)

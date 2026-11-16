from pathlib import Path


def _render(version, context):
    variables = context['vars']
    plantilla = Path(__file__).with_name(f'{version}.txt').read_text(encoding='utf-8')
    return plantilla.replace('{{historia_id}}', variables['historia_id']).replace('{{historia}}', variables['historia'])


def prompt_v1(context):
    return _render('v1', context)


def prompt_v2(context):
    return _render('v2', context)


def prompt_v3(context):
    return _render('v3', context)

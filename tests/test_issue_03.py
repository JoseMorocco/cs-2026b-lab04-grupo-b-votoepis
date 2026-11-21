from datetime import datetime, timedelta, timezone

import pytest

from agentes.demo.cierre import puede_cerrar


@pytest.mark.xfail(strict=True, reason="ISSUE-03 sembrado: solo se compara el día")
def test_issue_03_respeta_instante_de_cierre():
    cierre = datetime(2026, 11, 21, 18, 0, tzinfo=timezone(timedelta(hours=-5)))
    assert puede_cerrar(cierre - timedelta(seconds=1), cierre) is False
    assert puede_cerrar(cierre, cierre) is True

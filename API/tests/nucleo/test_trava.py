import asyncio
import uuid

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario


@pytest.fixture
async def fabrica(banco_migrado: str):
    engine = create_async_engine(banco_migrado, poolclass=NullPool)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def test_reentrancia_e_promocao_proibida(fabrica) -> None:
    usuario = uuid.uuid4()
    async with fabrica() as s:
        await travar_usuario(s, usuario, ModoTrava.COMPARTILHADA)
        await travar_usuario(s, usuario, ModoTrava.COMPARTILHADA)
        with pytest.raises(RuntimeError, match="promoção"):
            await travar_usuario(s, usuario, ModoTrava.EXCLUSIVA)
    async with fabrica() as s:
        await travar_usuario(s, usuario, ModoTrava.EXCLUSIVA)
        await travar_usuario(s, usuario, ModoTrava.COMPARTILHADA)  # no-op
        with pytest.raises(RuntimeError, match="outro usuário"):
            await travar_usuario(s, uuid.uuid4(), ModoTrava.EXCLUSIVA)


async def test_exclusiva_bloqueia_exclusiva_ate_o_commit(fabrica) -> None:
    usuario = uuid.uuid4()
    ordem: list[str] = []

    async def segunda() -> None:
        async with fabrica() as s:
            await travar_usuario(s, usuario, ModoTrava.EXCLUSIVA)
            ordem.append("segunda")
            await s.commit()

    async with fabrica() as primeira:
        await travar_usuario(primeira, usuario, ModoTrava.EXCLUSIVA)
        tarefa = asyncio.create_task(segunda())
        await asyncio.sleep(0.3)
        assert not tarefa.done()
        ordem.append("primeira")
        await primeira.commit()
    await asyncio.wait_for(tarefa, 5)
    assert ordem == ["primeira", "segunda"]


async def test_compartilhadas_coexistem_e_bloqueiam_exclusiva(fabrica) -> None:
    usuario = uuid.uuid4()
    async with fabrica() as a, fabrica() as b:
        await travar_usuario(a, usuario, ModoTrava.COMPARTILHADA)
        await asyncio.wait_for(
            travar_usuario(b, usuario, ModoTrava.COMPARTILHADA), 2
        )
        async with fabrica() as c:
            exclusiva = asyncio.create_task(
                travar_usuario(c, usuario, ModoTrava.EXCLUSIVA)
            )
            await asyncio.sleep(0.3)
            assert not exclusiva.done()
            await a.rollback()
            await b.rollback()
            await asyncio.wait_for(exclusiva, 5)


async def test_liberada_no_rollback_e_no_commit(fabrica) -> None:
    usuario = uuid.uuid4()
    async with fabrica() as a:
        await travar_usuario(a, usuario, ModoTrava.EXCLUSIVA)
        await a.rollback()
        assert "trava_usuario" not in a.info
        async with fabrica() as b:
            await asyncio.wait_for(
                travar_usuario(b, usuario, ModoTrava.EXCLUSIVA), 2
            )
            await b.commit()
            assert "trava_usuario" not in b.info
        # Nova trava na mesma sessão depois do desfecho.
        await travar_usuario(a, usuario, ModoTrava.EXCLUSIVA)


async def test_rollback_de_savepoint_mantem_a_trava(fabrica) -> None:
    usuario = uuid.uuid4()
    async with fabrica() as a:
        await travar_usuario(a, usuario, ModoTrava.EXCLUSIVA)
        sub = await a.begin_nested()
        await sub.rollback()
        assert a.info["trava_usuario"][0] == usuario
        async with fabrica() as b:
            tarefa = asyncio.create_task(
                travar_usuario(b, usuario, ModoTrava.EXCLUSIVA)
            )
            await asyncio.sleep(0.3)
            assert not tarefa.done()
            await a.rollback()
            await asyncio.wait_for(tarefa, 5)


def test_tipos() -> None:
    assert isinstance(ModoTrava.EXCLUSIVA, str)
    assert AsyncSession is not None

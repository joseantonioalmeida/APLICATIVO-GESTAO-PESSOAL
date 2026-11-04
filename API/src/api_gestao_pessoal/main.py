from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import anyio
from fastapi import FastAPI

from api_gestao_pessoal.database import criar_engine, criar_fabrica_sessoes
from api_gestao_pessoal.email import criar_enviador
from api_gestao_pessoal.erros import registrar_tratadores_erro
from api_gestao_pessoal.rastreamento import (
    configurar_logging,
    middleware_id_requisicao,
)
from api_gestao_pessoal.routers import (
    atividades,
    autenticacao,
    categorias,
    financeiro,
    importancias,
    notificacoes,
    painel,
    saude,
    usuarios,
)
from api_gestao_pessoal.seguranca import HasherSenha, ParametrosArgon2
from api_gestao_pessoal.settings import Settings, obter_settings


def criar_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
        s = settings or obter_settings()
        configurar_logging(s.LOG_NIVEL)
        # Antes da engine: uma falha aqui não deixa conexões abertas.
        hasher = HasherSenha(
            ParametrosArgon2(
                s.ARGON2_TIME_COST,
                s.ARGON2_MEMORY_COST_KIB,
                s.ARGON2_PARALLELISM,
            ),
            anyio.CapacityLimiter(s.ARGON2_MAX_CONCORRENTES),
        )
        await hasher.preparar_ficticio()
        app.state.hasher = hasher
        app.state.enviador_email = criar_enviador(s)
        engine = criar_engine(s)
        app.state.settings = s
        app.state.engine = engine
        app.state.fabrica_sessoes = criar_fabrica_sessoes(engine)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(
        title="API MinhaVida", version="0.1.0", lifespan=ciclo_de_vida
    )
    app.middleware("http")(middleware_id_requisicao)
    registrar_tratadores_erro(app)
    app.include_router(saude.router)
    app.include_router(autenticacao.router, prefix="/api/v1")
    app.include_router(usuarios.router, prefix="/api/v1")
    app.include_router(notificacoes.router, prefix="/api/v1")
    app.include_router(categorias.router, prefix="/api/v1")
    app.include_router(atividades.router, prefix="/api/v1")
    app.include_router(financeiro.router, prefix="/api/v1")
    app.include_router(importancias.router, prefix="/api/v1")
    app.include_router(painel.router, prefix="/api/v1")
    return app


app = criar_app()

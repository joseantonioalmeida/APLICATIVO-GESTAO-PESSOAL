import smtplib
import ssl
from typing import Any, Literal, NamedTuple, Self

import pytest
from pydantic import SecretStr

from api_gestao_pessoal.email import (
    EnviadorEmailMemoria,
    EnviadorEmailSmtp,
    FalhaEnvioEmail,
    MensagemEmail,
    criar_enviador,
    mensagem_codigo,
)

from ..conftest import SEGREDO_JWT_TESTE, SettingsTeste

ENDERECO_SENTINELA = "sentinela.destino@exemplo.com"
USUARIO_SMTP = "usuario-smtp-sintetico"
SENHA_SMTP = "senha-smtp-sintetica"
TIMEOUT_S = 7.0
CORPO_ESPERADO = (
    "Olá, Maria da Silva.\n"
    "Recebemos uma solicitação para redefinir a senha de sua conta "
    "MinhaVida.\n"
    "00012345\n"
    "Insira este código para concluir a redefinição.\n"
    "Obrigado por nos ajudar a manter sua conta segura.\n"
    "Equipe MinhaVida.\n"
)


class Caso(NamedTuple):
    seguranca: Literal["starttls", "tls", "nenhuma"]
    credenciais: bool
    recusar: bool = False


class ClienteFalso:
    """Substituto de `smtplib.SMTP` e `SMTP_SSL` que só registra chamadas."""

    def __init__(
        self,
        host: str,
        porta: int,
        timeout: float,
        context: ssl.SSLContext | None = None,
    ) -> None:
        self.tipo = ""
        self.recusar = False
        self.host = host
        self.porta = porta
        self.timeout = timeout
        self.contexto = context
        self.eventos: list[str] = []
        self.login_usado: tuple[str, str] | None = None
        self.mensagem: Any = None
        self.fechado = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        self.fechado = True

    def starttls(self, context: ssl.SSLContext) -> None:
        self.eventos.append("starttls")
        self.contexto = context

    def ehlo(self) -> None:
        self.eventos.append("ehlo")

    def login(self, usuario: str, senha: str) -> None:
        self.eventos.append("login")
        self.login_usado = (usuario, senha)

    def send_message(self, mensagem: Any) -> None:
        self.eventos.append("send_message")
        self.mensagem = mensagem
        if self.recusar:
            raise smtplib.SMTPRecipientsRefused({
                ENDERECO_SENTINELA: (550, b"recusado")
            })


def instalar_falsos(
    monkeypatch: pytest.MonkeyPatch, *, recusar: bool
) -> list[ClienteFalso]:
    criados: list[ClienteFalso] = []

    def fabricar(tipo: str) -> Any:
        def criar(host: str, porta: int, **opcoes: Any) -> ClienteFalso:
            cliente = ClienteFalso(host, porta, **opcoes)
            cliente.tipo = tipo
            cliente.recusar = recusar
            criados.append(cliente)
            return cliente

        return criar

    monkeypatch.setattr(smtplib, "SMTP", fabricar("SMTP"))
    monkeypatch.setattr(smtplib, "SMTP_SSL", fabricar("SMTP_SSL"))
    return criados


def settings_smtp(caso: Caso) -> SettingsTeste:
    credenciais: dict[str, Any] = {}
    if caso.credenciais:
        credenciais = {
            "SMTP_USUARIO": USUARIO_SMTP,
            "SMTP_SENHA": SecretStr(SENHA_SMTP),
        }
    return SettingsTeste(
        DATABASE_URL=SecretStr("postgresql+psycopg://u:p@h/db"),
        JWT_SEGREDO=SecretStr(SEGREDO_JWT_TESTE),
        EMAIL_MODO="smtp",
        SMTP_HOST="smtp.exemplo.com",
        SMTP_PORTA=2525,
        SMTP_SEGURANCA=caso.seguranca,
        SMTP_REMETENTE="Nao-Responda@Exemplo.com",
        SMTP_TIMEOUT_S=TIMEOUT_S,
        **credenciais,
    )


MENSAGEM = MensagemEmail(
    destinatario=ENDERECO_SENTINELA, assunto="Assunto sintético", corpo="Corpo"
)


@pytest.mark.parametrize(
    "caso",
    [
        pytest.param(Caso("starttls", True), id="starttls_com_credenciais"),
        pytest.param(Caso("starttls", False), id="starttls_sem_credenciais"),
        pytest.param(Caso("tls", True), id="tls_com_credenciais"),
        pytest.param(Caso("nenhuma", False), id="nenhuma_sem_credenciais"),
        pytest.param(
            Caso("starttls", True, recusar=True), id="destinatario_recusado"
        ),
    ],
)
async def test_enviador_smtp(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    caso: Caso,
) -> None:
    criados = instalar_falsos(monkeypatch, recusar=caso.recusar)
    enviador = EnviadorEmailSmtp(settings_smtp(caso))
    if caso.recusar:
        with pytest.raises(FalhaEnvioEmail) as erro:
            await enviador.enviar(MENSAGEM)
        assert erro.value.motivo == "SMTPRecipientsRefused"
        for texto in (str(erro.value), repr(erro.value), caplog.text):
            assert ENDERECO_SENTINELA not in texto
        assert "SMTPRecipientsRefused" in caplog.text
    else:
        await enviador.enviar(MENSAGEM)
    (cliente,) = criados
    assert cliente.tipo == ("SMTP_SSL" if caso.seguranca == "tls" else "SMTP")
    assert cliente.timeout == TIMEOUT_S
    assert cliente.fechado
    esperados = ["starttls", "ehlo"] if caso.seguranca == "starttls" else []
    if caso.credenciais:
        esperados.append("login")
        assert cliente.login_usado == (USUARIO_SMTP, SENHA_SMTP)
    assert cliente.eventos == [*esperados, "send_message"]
    if caso.seguranca != "nenhuma":
        assert cliente.contexto is not None
        assert cliente.contexto.verify_mode == ssl.CERT_REQUIRED
        assert cliente.contexto.check_hostname
    assert cliente.mensagem["To"] == ENDERECO_SENTINELA
    assert cliente.mensagem["From"] == "MinhaVida <nao-responda@exemplo.com>"


def test_mensagem_codigo() -> None:
    mensagem = mensagem_codigo(
        "Maria da Silva", "maria@exemplo.com", "00012345"
    )
    assert mensagem.destinatario == "maria@exemplo.com"
    assert mensagem.assunto == "Maria da Silva, aqui está seu código"
    assert mensagem.corpo == CORPO_ESPERADO


async def test_enviador_em_memoria() -> None:
    enviador = EnviadorEmailMemoria()
    await enviador.enviar(MENSAGEM)
    assert list(enviador.enviadas) == [MENSAGEM]
    enviador.falha_programada = FalhaEnvioEmail("SMTPException")
    with pytest.raises(FalhaEnvioEmail):
        await enviador.enviar(MENSAGEM)
    assert enviador.falha_programada is None
    await enviador.enviar(MENSAGEM)
    assert len(enviador.enviadas) == 2


def test_criar_enviador() -> None:
    memoria = SettingsTeste(
        DATABASE_URL=SecretStr("postgresql+psycopg://u:p@h/db"),
        JWT_SEGREDO=SecretStr(SEGREDO_JWT_TESTE),
        EMAIL_MODO="memoria",
    )
    assert isinstance(criar_enviador(memoria), EnviadorEmailMemoria)
    assert isinstance(
        criar_enviador(settings_smtp(Caso("starttls", False))),
        EnviadorEmailSmtp,
    )


async def test_modo_console_registra_a_mensagem_no_log(
    caplog: pytest.LogCaptureFixture,
) -> None:
    from api_gestao_pessoal.email import (  # noqa: PLC0415
        EnviadorEmailConsole,
        MensagemEmail,
    )

    with caplog.at_level("WARNING"):
        await EnviadorEmailConsole().enviar(
            MensagemEmail("a@exemplo.com", "Assunto", "código 12345678")
        )
    assert "12345678" in caplog.text
    assert "a@exemplo.com" in caplog.text

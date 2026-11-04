"""Envio de e-mail: protocolo, SMTP, memória e texto da recuperação."""

import collections
import email.message
import email.utils
import logging
import smtplib
import ssl
from dataclasses import dataclass
from typing import Protocol, override

import anyio.to_thread

from api_gestao_pessoal.settings import Settings

logger = logging.getLogger(__name__)

NOME_REMETENTE = "MinhaVida"
MAXIMO_MENSAGENS_EM_MEMORIA = 100


@dataclass(frozen=True, slots=True)
class MensagemEmail:
    """Mensagem pronta para envio."""

    destinatario: str
    assunto: str
    corpo: str


class FalhaEnvioEmail(Exception):
    """Falha de envio; guarda só o nome da classe da causa."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class EnviadorEmail(Protocol):
    """Envia mensagens de e-mail."""

    async def enviar(self, mensagem: MensagemEmail) -> None:
        """Envia a mensagem ou lança `FalhaEnvioEmail`."""
        ...


class EnviadorEmailMemoria(EnviadorEmail):
    """Guarda as mensagens em memória (desenvolvimento e testes)."""

    def __init__(self) -> None:
        self.enviadas: collections.deque[MensagemEmail] = collections.deque(
            maxlen=MAXIMO_MENSAGENS_EM_MEMORIA
        )
        self.falha_programada: FalhaEnvioEmail | None = None

    @override
    async def enviar(self, mensagem: MensagemEmail) -> None:
        if self.falha_programada is not None:
            falha = self.falha_programada
            self.falha_programada = None
            raise falha
        self.enviadas.append(mensagem)


class EnviadorEmailConsole(EnviadorEmail):
    """Escreve a mensagem no log (só desenvolvimento: expõe o código)."""

    @override
    async def enviar(self, mensagem: MensagemEmail) -> None:
        logger.warning(
            "E-mail (modo console) para %s | %s\n%s",
            mensagem.destinatario,
            mensagem.assunto,
            mensagem.corpo,
        )


class EnviadorEmailSmtp(EnviadorEmail):
    """Envio por `smtplib`, em thread, com TLS verificado."""

    def __init__(self, settings: Settings) -> None:
        if settings.SMTP_HOST is None or settings.SMTP_REMETENTE is None:
            msg = "SMTP_HOST e SMTP_REMETENTE são obrigatórios"
            raise RuntimeError(msg)
        self._host = settings.SMTP_HOST
        self._porta = settings.SMTP_PORTA
        self._seguranca = settings.SMTP_SEGURANCA
        self._usuario = settings.SMTP_USUARIO
        self._senha = settings.SMTP_SENHA
        self._remetente = settings.SMTP_REMETENTE
        self._timeout = settings.SMTP_TIMEOUT_S

    @override
    async def enviar(self, mensagem: MensagemEmail) -> None:
        await anyio.to_thread.run_sync(
            self._enviar_sincrono, mensagem, abandon_on_cancel=False
        )

    def _montar(self, mensagem: MensagemEmail) -> email.message.EmailMessage:
        msg = email.message.EmailMessage()
        msg["From"] = email.utils.formataddr((NOME_REMETENTE, self._remetente))
        msg["To"] = mensagem.destinatario
        msg["Subject"] = mensagem.assunto
        msg.set_content(mensagem.corpo)
        return msg

    def _transmitir(
        self, msg: email.message.EmailMessage, contexto: ssl.SSLContext
    ) -> None:
        if self._seguranca == "tls":
            cliente = smtplib.SMTP_SSL(
                self._host,
                self._porta,
                timeout=self._timeout,
                context=contexto,
            )
        else:
            cliente = smtplib.SMTP(
                self._host, self._porta, timeout=self._timeout
            )
        with cliente:
            if self._seguranca == "starttls":
                cliente.starttls(context=contexto)
                cliente.ehlo()
            if self._usuario is not None and self._senha is not None:
                cliente.login(self._usuario, self._senha.get_secret_value())
            cliente.send_message(msg)

    def _enviar_sincrono(self, mensagem: MensagemEmail) -> None:
        try:
            msg = self._montar(mensagem)
            contexto = ssl.create_default_context()
            self._transmitir(msg, contexto)
        except (
            smtplib.SMTPException,
            OSError,
            UnicodeError,
            ValueError,
        ) as erro:
            logger.warning(
                "falha no envio de e-mail: motivo=%s codigo_smtp=%s",
                type(erro).__name__,
                getattr(erro, "smtp_code", "-"),
            )
            raise FalhaEnvioEmail(type(erro).__name__) from None


def criar_enviador(settings: Settings) -> EnviadorEmail:
    """Memória, console (desenvolvimento) ou SMTP, conforme `EMAIL_MODO`."""
    if settings.EMAIL_MODO == "memoria":
        return EnviadorEmailMemoria()
    if settings.EMAIL_MODO == "console":
        return EnviadorEmailConsole()
    return EnviadorEmailSmtp(settings)


def mensagem_codigo(nome: str, email: str, codigo: str) -> MensagemEmail:
    """E-mail do código de recuperação (requisito 3.4.4)."""
    corpo = (
        f"Olá, {nome}.\n"
        "Recebemos uma solicitação para redefinir a senha de sua conta "
        "MinhaVida.\n"
        f"{codigo}\n"
        "Insira este código para concluir a redefinição.\n"
        "Obrigado por nos ajudar a manter sua conta segura.\n"
        "Equipe MinhaVida.\n"
    )
    return MensagemEmail(
        destinatario=email,
        assunto=f"{nome}, aqui está seu código",
        corpo=corpo,
    )

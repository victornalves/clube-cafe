"""E-mail simulado: o MVP grava a mensagem e o link em vez de enviar. A caixa só abre com o login de demonstração."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import EmailSimulado
from app.services import auth
from app.services.erros import AcessoNegado


def enviar(
    s: Session,
    *,
    para_nome: str,
    para_email: str,
    assunto: str,
    corpo: str,
    link: str | None = None,
    rotulo_link: str | None = None,
    proposta_id: int | None = None,
) -> EmailSimulado:
    email = EmailSimulado(
        criado_em=datetime.now(UTC),
        para_nome=para_nome,
        para_email=para_email,
        assunto=assunto,
        corpo=corpo,
        link=link,
        rotulo_link=rotulo_link,
        proposta_id=proposta_id,
    )
    s.add(email)
    s.flush()
    return email


def caixa(s: Session, limite: int = 200) -> list[EmailSimulado]:
    """Pública, como os botões de login: só existe enquanto o login de demonstração estiver ligado."""
    if not auth.login_demo_ligado():
        raise AcessoNegado('Caixa de e-mails simulada desligada')
    return list(s.scalars(select(EmailSimulado).order_by(EmailSimulado.id.desc()).limit(limite)))


def da_proposta(s: Session, proposta_id: int) -> list[EmailSimulado]:
    return list(
        s.scalars(select(EmailSimulado).where(EmailSimulado.proposta_id == proposta_id).order_by(EmailSimulado.id))
    )

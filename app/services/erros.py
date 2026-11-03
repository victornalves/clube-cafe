from app.domain.models import Papel, Usuario


class ErroDeNegocio(Exception):
    """Mensagem pronta para mostrar ao usuário."""


class NaoEncontrado(Exception):
    """Também para o que existe mas o usuário não pode ver: quem pede o registro de outro não sabe que ele existe."""


class AcessoNegado(Exception):
    pass


def exigir_papel(usuario: Usuario, papel: Papel):
    if usuario.papel != papel:
        raise AcessoNegado(f'Exige o papel {papel}')

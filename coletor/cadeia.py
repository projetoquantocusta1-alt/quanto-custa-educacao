"""Completa a cadeia de certificados de sites que mandam o certificado sem o intermediário.

Alguns sites do governo (ex.: download.inep.gov.br) entregam só o próprio certificado,
sem o da autoridade intermediária, e a verificação TLS falha. Em vez de DESLIGAR a
verificação, baixamos o intermediário indicado no próprio certificado (campo
"Authority Information Access → CA Issuers"), juntamos à lista padrão (certifi) e
verificamos normalmente. A conexão de dados continua 100% verificada.
"""
import socket
import ssl
from pathlib import Path

import certifi
import requests
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import AuthorityInformationAccessOID, ExtensionOID

PASTA = Path(__file__).resolve().parent.parent / "dados_brutos" / "certs"


def _cert_do_site(host: str, porta: int = 443) -> x509.Certificate:
    # Só lê o certificado para achar o endereço do intermediário; nenhum dado trafega aqui.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection((host, porta), timeout=30) as s, ctx.wrap_socket(s, server_hostname=host) as t:
        return x509.load_der_x509_certificate(t.getpeercert(binary_form=True))


def _url_emissor(cert: x509.Certificate) -> str | None:
    try:
        aia = cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
    except x509.ExtensionNotFound:
        return None
    for d in aia:
        if d.access_method == AuthorityInformationAccessOID.CA_ISSUERS:
            return d.access_location.value
    return None


def _carregar(dados: bytes) -> x509.Certificate:
    try:
        return x509.load_der_x509_certificate(dados)
    except ValueError:
        return x509.load_pem_x509_certificate(dados)


def pacote_para(host: str, max_niveis: int = 3) -> str:
    """Caminho de um arquivo PEM = certifi + intermediários do host (gerado uma vez e reaproveitado)."""
    PASTA.mkdir(parents=True, exist_ok=True)
    destino = PASTA / f"{host}.pem"
    if destino.exists():
        return str(destino)
    pems, cert = [], _cert_do_site(host)
    for _ in range(max_niveis):
        url = _url_emissor(cert)
        if not url:
            break
        cert = _carregar(requests.get(url, timeout=30).content)
        pems.append(cert.public_bytes(Encoding.PEM).decode())
        if cert.issuer == cert.subject:   # chegou na raiz
            break
    if not pems:
        raise ssl.SSLError(f"{host}: certificado sem endereço do intermediário")
    destino.write_text(Path(certifi.where()).read_text() + "\n" + "\n".join(pems))
    return str(destino)

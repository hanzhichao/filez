import base64
import datetime
import re
from typing import Dict, Any


# ---------- 小工具 ----------
def _der_time(der_bytes: bytes) -> datetime.datetime:
    """UTCTime / GeneralizedTime → datetime"""
    if len(der_bytes) == 13:  # UTCTime YYMMDDhhmmssZ
        return datetime.datetime.strptime(der_bytes.decode(), "%y%m%d%H%M%SZ")
    elif len(der_bytes) == 15:  # GeneralizedTime YYYYMMDDhhmmssZ
        return datetime.datetime.strptime(der_bytes.decode(), "%Y%m%d%H%M%SZ")
    else:
        raise ValueError("Invalid time format")


def _int_from_bytes(b: bytes) -> int:
    return int.from_bytes(b, byteorder='big', signed=False)


# ---------- 解析 RSA 公钥（SubjectPublicKeyInfo） ----------
def _parse_rsa_pubkey(der: bytes) -> Dict[str, Any]:
    # 简单手动 DER 解析 (SEQUENCE { n, e })
    seq, rest = _der_sequence(der)
    if rest: raise ValueError("Extra data after RSA pubkey")
    n, der = _der_integer(seq)
    e, der = _der_integer(der)
    if der: raise ValueError("Extra data after RSA integers")
    return {"type": "RSA", "n": n, "e": e, "bits": n.bit_length()}


# ---------- 极简 DER 解析器 ----------
def _der_sequence(der: bytes):
    if der[0] != 0x30: raise ValueError("Not a SEQUENCE")
    length, offset = _der_length(der[1:])
    return der[offset:offset + length], der[offset + length:]


def _der_integer(der: bytes):
    if der[0] != 0x02: raise ValueError("Not an INTEGER")
    length, offset = _der_length(der[1:])
    return _int_from_bytes(der[offset:offset + length]), der[offset + length:]


def _der_length(der: bytes):
    first = der[0]
    if first & 0x80 == 0:
        return first, 1
    n_bytes = first & 0x7f
    if n_bytes > 2: raise ValueError("Long length not supported")
    return _int_from_bytes(der[1:1 + n_bytes]), 1 + n_bytes


# ---------- 解析 X509 基础字段 ----------
def _parse_x509_der(der: bytes) -> Dict[str, Any]:
    cert, _ = _der_sequence(der)
    # 手工定位：版本(可选) → 序列号 → 算法 → 颁发者 → 有效期 → 主体 → 公钥
    # 这里只演示核心字段；完整 ASN.1 请用 cryptography
    seq, cert = _der_sequence(cert)  # TBSCertificate
    # 版本
    if seq[0] == 0xa0:
        version_der, seq = _der_sequence(seq[2:])  # skip context tag
        version = _int_from_bytes(version_der) + 1
    else:
        version = 1
    # 序列号
    serial, seq = _der_integer(seq)
    # 跳过算法标识符
    _, seq = _der_sequence(seq)
    # 颁发者
    issuer_der, seq = _der_sequence(seq)
    issuer = _der_rdn_sequence(issuer_der)
    # 有效期
    not_before, seq = _der_time(_der_sequence(seq)[0])
    not_after, seq = _der_time(_der_sequence(seq)[0])
    # 主体
    subject_der, seq = _der_sequence(seq)
    subject = _der_rdn_sequence(subject_der)
    # 公钥
    pubkey_der, _ = _der_sequence(seq)
    pubkey = _parse_rsa_pubkey(pubkey_der)

    return {
        "version": version,
        "serial_number": serial,
        "issuer": issuer,
        "subject": subject,
        "not_before": not_before,
        "not_after": not_after,
        "public_key": pubkey,
    }


def _der_rdn_sequence(der: bytes) -> str:
    # 极简：只把 SEQUENCE OF SET OF SEQUENCE 拼成 "/CN=xxx/O=yyy"
    names = []
    while der:
        try:
            set_seq, der = _der_sequence(der)
            seq, _ = _der_sequence(set_seq)
            oid, remain = _der_object_identifier(seq)
            value, _ = _der_printable_string(remain)
            oid_name = {b'\x55\x04\x03': "CN", b'\x55\x04\x0a': "O", b'\x55\x04\x06': "C",
                        b'\x55\x04\x08': "ST", b'\x55\x04\x07': "L"}.get(oid, f"OID-{oid.hex()}")
            names.append(f"{oid_name}={value}")
        except Exception:
            break
    return "/".join(names)


def _der_object_identifier(der: bytes):
    if der[0] != 0x06: raise ValueError("Not OID")
    length, offset = _der_length(der[1:])
    return der[offset:offset + length], der[offset + length:]


def _der_printable_string(der: bytes):
    if der[0] not in (0x13, 0x12):  # PrintableString or UTF8String
        raise ValueError("Not Printable/UTF8String")
    length, offset = _der_length(der[1:])
    return der[offset:offset + length], der[offset + length:]


# ---------- 对外入口 ----------
def parse_pem_to_dict(pem_text: str) -> Dict[str, Any]:
    """输入 PEM 字符串（可含多个段），返回字典"""
    result: Dict[str, Any] = {}
    for match in re.finditer(r'-----BEGIN ([A-Z ]+)-----\n(.*?)-----END \1-----', pem_text, re.S):
        label, b64 = match.groups()
        der = base64.b64decode(b64.replace('\n', ''))
        label = label.lower()
        if label == 'certificate':
            result["cert"] = _parse_x509_der(der)
        elif label in ('rsa private key', 'private key'):
            # 仅解析 RSA 私钥基础结构（简化）
            result["private_key"] = {"type": "RSA", "raw": der.hex()}  # 或扩展解析
        elif label == 'public key':
            result["public_key"] = _parse_rsa_pubkey(der)
        else:
            result.setdefault(label.replace(' ', '_'), der.hex())
    return result

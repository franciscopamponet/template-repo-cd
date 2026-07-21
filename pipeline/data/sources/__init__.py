"""Implementações concretas do Protocol `DataSource` (Decisão 3).

Cada implementação traz suas dependências de plataforma de forma lazy (dentro dos
métodos), para que o repo importe sem spark/sqlalchemy instalados (Rule 06).
"""

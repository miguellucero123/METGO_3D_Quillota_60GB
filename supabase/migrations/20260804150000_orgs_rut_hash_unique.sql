-- Unicidad real de RUT por sitio/faena (rut_enc AES no es determinístico).
-- rut_hash = HMAC-SHA256 del RUT normalizado (app: pii_crypto.rut_lookup_hash).

alter table public.orgs
  add column if not exists rut_hash text;

-- Backfill no automático: filas antiguas sin hash quedan nullable hasta re-registro/migración ops.
create unique index if not exists orgs_sitio_faena_rut_hash_uidx
  on public.orgs (sitio, coalesce(faena, ''), rut_hash)
  where rut_hash is not null;

comment on column public.orgs.rut_hash is
  'HMAC del RUT normalizado para unicidad; no es reversible sin METGO_PII_KEK';

-- P2 KYC manual (ADR_KYC_IDENTIDAD): estado de verificación por org
-- pending = registro nuevo; verified / rejected = revisión ops

ALTER TABLE public.orgs
  ADD COLUMN IF NOT EXISTS kyc_status text NOT NULL DEFAULT 'pending'
    CHECK (kyc_status IN ('pending', 'verified', 'rejected'));

ALTER TABLE public.orgs
  ADD COLUMN IF NOT EXISTS kyc_notes text;

ALTER TABLE public.orgs
  ADD COLUMN IF NOT EXISTS kyc_reviewed_at timestamptz;

ALTER TABLE public.orgs
  ADD COLUMN IF NOT EXISTS kyc_reviewed_by text;

COMMENT ON COLUMN public.orgs.kyc_status IS
  'KYC manual: pending|verified|rejected (piloto; gate pago opcional METGO_KYC_GATE_PAID)';

CREATE INDEX IF NOT EXISTS orgs_kyc_status_idx ON public.orgs (kyc_status);

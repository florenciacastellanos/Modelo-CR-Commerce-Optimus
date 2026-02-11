-- ══════════════════════════════════════════════════════════════════════════════
-- SITE FILTERS - CONTACT RATE COMMERCE
-- ══════════════════════════════════════════════════════════════════════════════
-- Description: Site (country) filter examples
-- Available Sites: MLA, MLB, MLC, MCO, MEC, MLM, MLU, MPE
-- Excluded: MLV (Venezuela)
-- ══════════════════════════════════════════════════════════════════════════════

-- ══════════════════════════════════════════════════════════════════════════════
-- 1. SINGLE SITE (Argentina)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.SIT_SITE_ID = 'MLA'

-- ══════════════════════════════════════════════════════════════════════════════
-- 2. MULTIPLE SITES (Argentina + Chile)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.SIT_SITE_ID IN ('MLA', 'MLC')

-- ══════════════════════════════════════════════════════════════════════════════
-- 3. LATAM (All except Brasil)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.SIT_SITE_ID IN ('MLA', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE')

-- ══════════════════════════════════════════════════════════════════════════════
-- 4. ALL SITES (Including Brasil - ⚠️ requires sampling)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.SIT_SITE_ID IN ('MLA', 'MLB', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE')
-- Note: Always exclude MLV (Venezuela)

-- ══════════════════════════════════════════════════════════════════════════════
-- 5. EXCLUDE SPECIFIC SITE (All except Brasil)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.SIT_SITE_ID NOT IN ('MLB')
AND C.SIT_SITE_ID IN ('MLA', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE')

-- ══════════════════════════════════════════════════════════════════════════════
-- SITE INFORMATION
-- ══════════════════════════════════════════════════════════════════════════════
/*
Site  | Country       | Volume | Considerations
------|---------------|--------|----------------------------------
MLA   | Argentina     | High   | Main market
MLB   | Brasil        | Very High | ⚠️ Requires sampling
MLC   | Chile         | Medium | -
MCO   | Colombia      | Medium | -
MEC   | Ecuador       | Low-Medium | -
MLM   | México        | High   | -
MLU   | Uruguay       | Low    | -
MPE   | Perú          | Medium | -
MLV   | Venezuela     | - | ❌ EXCLUDED (always)
*/

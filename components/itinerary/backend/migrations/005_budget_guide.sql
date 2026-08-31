-- Optional tour-guide slice on budget allocation (include/remove by preference)
ALTER TABLE budget_split ADD COLUMN IF NOT EXISTS guide NUMERIC DEFAULT 0;
ALTER TABLE budget_split ADD COLUMN IF NOT EXISTS guide_pct NUMERIC DEFAULT 0;
ALTER TABLE budget_split ADD COLUMN IF NOT EXISTS include_guide BOOLEAN DEFAULT FALSE;

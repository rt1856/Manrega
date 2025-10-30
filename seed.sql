USE mgnrega_db;

INSERT INTO districts (state, district_code, district_name, centroid_lat, centroid_lon) VALUES
('Gujarat','GD-GNR','Gandhinagar',23.2156,72.6369),
('Gujarat','GD-SRT','Surat',21.1702,72.8311),
('Gujarat','GD-PBR','Porbandar',21.6417,69.6042);

-- sample monthly metrics (Year 2025 months)
INSERT INTO monthly_metrics (district_id, year, month, person_days, households, avg_wage, beneficiaries, source_updated_at)
VALUES
(1,2025,9,2510000,58000,235.00,125480,'2025-09-10'),
(2,2025,9,2480000,62000,240.00,142000,'2025-09-10'),
(3,2025,9,920000,23000,210.00,45000,'2025-09-10');

-- Add some older months for trend
INSERT INTO monthly_metrics (district_id, year, month, person_days, households, avg_wage, beneficiaries)
VALUES
(1,2025,8,2400000,57000,232.00,122000),
(1,2025,7,2300000,56000,230.00,118000),
(1,2025,6,2200000,55000,228.00,115000);

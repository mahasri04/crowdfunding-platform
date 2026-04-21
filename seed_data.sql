INSERT INTO campaigns (id, title, goal, pledged, deadline)
VALUES
    (1, 'Community Library Upgrade', 1000, 250, '2026-12-31 23:59:59'),
    (2, 'Neighborhood Garden', 500, 500, '2026-10-15 23:59:59');

INSERT INTO pledges (id, campaign_id, user_name, amount)
VALUES
    (1, 1, 'alice', 100),
    (2, 1, 'bob', 150),
    (3, 2, 'charlie', 500);

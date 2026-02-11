-- Sample data for FastAPI application database
-- This matches the users defined in the Keycloak realm configuration

-- Insert users (matching Keycloak realm users)
INSERT INTO users (
    id, 
    external_id, 
    email, 
    full_name, 
    bio, 
    notification_preferences, 
    theme_preference, 
    created_at, 
    updated_at, 
    is_active
) VALUES 
(
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid,
    'keycloak-admin-sub-id-12345',
    'admin@lksnext.com',
    'Admin User',
    'System administrator with full access to manage the application.',
    '{"email": true, "push": true, "sms": false}',
    'dark',
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '1 day',
    true
),
(
    'b1fecd99-8d1c-4ef9-bb7e-7cc0ce491b22'::uuid,
    'keycloak-testuser-sub-id-67890',
    'testuser@lksnext.com',
    'Test User',
    'Standard user for testing application functionality.',
    '{"email": true, "push": false, "sms": false}',
    'light',
    NOW() - INTERVAL '15 days',
    NOW() - INTERVAL '2 hours',
    true
),
(
    'c2ddef99-7e2d-4ef0-bb8f-8dd1df502c33'::uuid,
    'keycloak-inactive-sub-id-11111',
    'inactive@lksnext.com',
    'Inactive User',
    'User account that has been deactivated.',
    '{"email": false, "push": false, "sms": false}',
    'system',
    NOW() - INTERVAL '60 days',
    NOW() - INTERVAL '30 days',
    false
);

-- Insert items (inventory items owned by users)
INSERT INTO items (
    id,
    name,
    description,
    price,
    available,
    owner_id,
    created_at,
    updated_at,
    is_active
) VALUES
(
    'd3eef000-8f3e-4ef1-bb9e-9ee2ee613d44'::uuid,
    'Laptop Pro 15"',
    'High-performance laptop with 16GB RAM, 512GB SSD, perfect for development work.',
    1299.99,
    true,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid, -- Admin user
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '5 days',
    true
),
(
    'e4ff0111-9c4f-4ef2-bb0f-0ff3ff724e55'::uuid,
    'Wireless Mouse',
    'Ergonomic wireless mouse with precision tracking and long battery life.',
    29.99,
    true,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid, -- Admin user
    NOW() - INTERVAL '15 days',
    NOW() - INTERVAL '3 days',
    true
),
(
    'f5001222-0c5e-4ef3-bb1e-100470835f66'::uuid,
    'Standing Desk',
    'Adjustable height standing desk for healthy workspace setup.',
    399.99,
    false,
    'b1fecd99-8d1c-4ef9-bb7e-7cc0ce491b22'::uuid, -- Test user
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '1 day',
    true
),
(
    '06112333-1c6e-4ef4-bb2e-211581946077'::uuid,
    'Coffee Maker',
    'Programmable coffee maker with built-in grinder and thermal carafe.',
    149.99,
    true,
    'b1fecd99-8d1c-4ef9-bb7e-7cc0ce491b22'::uuid, -- Test user
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '2 hours',
    true
),
(
    '17223444-2c7e-4ef5-bb3e-322692057188'::uuid,
    'Vintage Camera',
    'Classic film camera in excellent condition, perfect for photography enthusiasts.',
    89.99,
    true,
    'c2ddef99-7e2d-4ef0-bb8f-8dd1df502c33'::uuid, -- Inactive user
    NOW() - INTERVAL '45 days',
    NOW() - INTERVAL '30 days',
    false
);

-- Insert tasks (to-do items assigned to users)
INSERT INTO tasks (
    id,
    title,
    description,
    status,
    priority,
    due_date,
    owner_id,
    created_at,
    updated_at,
    is_active
) VALUES
(
    '28334555-3c8e-4ef6-bb4e-433703168299'::uuid,
    'Setup Development Environment',
    'Install and configure all necessary development tools including IDE, database, and testing frameworks.',
    'COMPLETED',
    'HIGH',
    NOW() - INTERVAL '25 days',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid, -- Admin user
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '25 days',
    true
),
(
    '39445666-4c9e-4ef7-bb5e-544814279300'::uuid,
    'Review Security Policies',
    'Conduct quarterly review of application security policies and update as needed.',
    'IN_PROGRESS',
    'URGENT',
    NOW() + INTERVAL '5 days',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid, -- Admin user
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '1 day',
    true
),
(
    '40556777-5c0e-4ef8-bb6e-655925390411'::uuid,
    'Test User Authentication',
    'Verify that user login, logout, and session management work correctly across all browsers.',
    'PENDING',
    'MEDIUM',
    NOW() + INTERVAL '7 days',
    'b1fecd99-8d1c-4ef9-bb7e-7cc0ce491b22'::uuid, -- Test user
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '3 hours',
    true
),
(
    '51667888-6c1e-4ef9-bb7e-766036401522'::uuid,
    'Update Documentation',
    'Review and update API documentation to reflect recent changes and new endpoints.',
    'PENDING',
    'LOW',
    NOW() + INTERVAL '14 days',
    'b1fecd99-8d1c-4ef9-bb7e-7cc0ce491b22'::uuid, -- Test user
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '1 hour',
    true
),
(
    '62778999-7c2e-4e00-bb8e-877147512633'::uuid,
    'Performance Optimization',
    'Analyze application performance and implement optimizations for faster response times.',
    'CANCELLED',
    'MEDIUM',
    NOW() - INTERVAL '5 days',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid, -- Admin user
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '10 days',
    true
),
(
    '73880000-8c3e-4e01-bb9e-988258623744'::uuid,
    'Database Backup Strategy',
    'Implement automated database backup strategy with disaster recovery procedures.',
    'PENDING',
    'HIGH',
    NOW() + INTERVAL '3 days',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid, -- Admin user
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '6 hours',
    true
),
(
    '84991111-9c4e-4e02-bb0f-099369734855'::uuid,
    'Old Task from Inactive User',
    'This task belongs to an inactive user and should be handled appropriately.',
    'PENDING',
    'LOW',
    NOW() - INTERVAL '10 days',
    'c2ddef99-7e2d-4ef0-bb8f-8dd1df502c33'::uuid, -- Inactive user
    NOW() - INTERVAL '40 days',
    NOW() - INTERVAL '35 days',
    false
);

-- Display summary of inserted data
SELECT 'Users inserted:' as summary, COUNT(*) as count FROM users
UNION ALL
SELECT 'Items inserted:', COUNT(*) FROM items
UNION ALL  
SELECT 'Tasks inserted:', COUNT(*) FROM tasks;

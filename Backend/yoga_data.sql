-- Insert yoga asana data
INSERT INTO yoga_asana (name, sanskrit_name, description, difficulty, duration_minutes, benefits, instructions) VALUES
(
    'Surya Namaskar',
    'Sūrya Namaskāra',
    'A sequence of twelve powerful yoga poses, also known as "Sun Salutation". It is a comprehensive workout for the entire body.',
    'Beginner to Intermediate',
    10,
    'Improves cardiovascular health, strengthens muscles, enhances flexibility, and calms the mind.',
    'Begin with Pranamasana (Prayer pose) and flow through a sequence of 12 postures, coordinating each movement with your breath.'
),
(
    'Chakrasan',
    'Chakrasana',
    'An advanced back-bending pose, also known as "Wheel Pose". It resembles a wheel and gives a deep stretch to the spine.',
    'Advanced',
    2,
    'Strengthens the spine, arms, wrists, and legs. Opens the chest and shoulders, increasing lung capacity.',
    'Lie on your back, bend your knees, place your hands by your ears with fingers pointing towards shoulders, and lift your entire body off the floor.'
),
(
    'Vrikshasan',
    'Vrikshasana',
    'A fundamental balancing pose, also known as "Tree Pose". It improves balance, focus, and concentration.',
    'Beginner',
    1,
    'Strengthens legs, ankles, and core. Improves sense of balance and brings stability to the mind.',
    'Stand tall on one leg, place the sole of the other foot on your inner thigh. Bring hands to a prayer position at your chest.'
),
(
    'Chandra Namaskar',
    'Chandra Namaskāra',
    'A sequence of poses performed to honor the moon, also known as "Moon Salutation". It is calming and restorative.',
    'Beginner to Intermediate',
    10,
    'Cools the body, calms the mind, stretches the spine, hamstrings, and backs of the legs. Balances energy.',
    'A graceful flow of poses, including side bends and low lunges, that opens the hips and promotes relaxation.'
),
(
    'Shirshasana',
    'Śīrṣāsana',
    'An advanced inversion pose, known as "Headstand". It is often called the "king" of all asanas.',
    'Advanced',
    3,
    'Calms the brain, relieves stress, strengthens the core, arms, and shoulders. Improves blood circulation to the head.',
    'From a kneeling position, interlock your fingers to form a base. Place the crown of your head on the mat and slowly lift your legs up.'
);

-- Insert yoga asana images
INSERT INTO yoga_asana_images (asana_id, image_url, display_order) VALUES
-- Images for Surya Namaskar (asana_id = 1)
(1, 'https://drive.google.com/file/d/16D76GjtZ0GH4Vd8GpuxV2qOolhcrPu2V/view?usp=drive_link', 1),
(1, 'https://drive.google.com/file/d/1v-i9FXBvMou3QdEXI4ZahmKTFvfXEe87/view?usp=drive_link', 2),
(1, 'https://drive.google.com/file/d/1Xnsghnqc36B7O8KhOz3IW3vgZPVNoAeV/view?usp=drive_link', 3),
(1, 'https://drive.google.com/file/d/1BngPcW0HKtSyuXD8xOGLn2vNqY4Y_7t3/view?usp=drive_link', 4),
(1, 'https://drive.google.com/file/d/1xx8xBBMnyXllsadh0cFTC66o6Va3LRN_/view?usp=drive_link', 5),
(1, 'https://drive.google.com/file/d/19NlB5WXGuFCrN_zh8TzBFddZRTCvJK2i/view?usp=drive_link', 6),
(1, 'https://drive.google.com/file/d/1PoMWic_ZPrAGGJ6kfwp_loBm110Vgdp-/view?usp=drive_link', 7),
(1, 'https://drive.google.com/file/d/1tIEVQM6KNFYnPxGX-EBGSHSFh4i46iDj/view?usp=drive_link', 8),
(1, 'https://drive.google.com/file/d/1R_l8AJUsG38g3ngXeonRvxZ6YoW8F7hI/view?usp=drive_link', 9),
(1, 'https://drive.google.com/file/d/1Xnsghnqc36B7O8KhOz3IW3vgZPVNoAeV/view?usp=drive_link', 10),
(1, 'https://drive.google.com/file/d/1v-i9FXBvMou3QdEXI4ZahmKTFvfXEe87/view?usp=drive_link', 11),
(1, 'https://drive.google.com/file/d/16D76GjtZ0GH4Vd8GpuxV2qOolhcrPu2V/view?usp=drive_link', 12),

-- Images for Chakrasan (asana_id = 2)
(2, 'https://drive.google.com/file/d/1WPNFWkRHWXiF9mRBWU4ZTjCgPQ5K8h2i/view?usp=drive_link', 1),
(2, 'https://drive.google.com/file/d/1joucK9wiszycBqBKSBDDyA6ZdkS8TvaD/view?usp=drive_link', 2),
(2, 'https://drive.google.com/file/d/1l0OdRyDrXMyFwi1v3D2OXRdsewg6T65n/view?usp=drive_link', 3),
(2, 'https://drive.google.com/file/d/1HHAeUQtZarUp10lHNILPTJJlu1ELe31H/view?usp=drive_link', 4),
(2, 'https://drive.google.com/file/d/1joucK9wiszycBqBKSBDDyA6ZdkS8TvaD/view?usp=drive_link', 5),
(2, 'https://drive.google.com/file/d/1WPNFWkRHWXiF9mRBWU4ZTjCgPQ5K8h2i/view?usp=drive_link', 6),

-- Images for Vrikshasan (asana_id = 3)
(3, 'https://drive.google.com/file/d/11MZRZqE52AjB9AQosSItPGOuCrYYtUjj/view?usp=drive_link', 1),
(3, 'https://drive.google.com/file/d/1MdbcK5P9pEanV6TvYBU9L3hDPt_Ri7nJ/view?usp=drive_link', 2),
(3, 'https://drive.google.com/file/d/17Vc7DPxhS-vMeTlZ-wZCjF9YrVUy7dV6/view?usp=drive_link', 3),
(3, 'https://drive.google.com/file/d/194sdUDPIQV3d9p25m8einhT8zRvxl8DZ/view?usp=drive_link', 4),

-- Images for Chandra Namaskar (asana_id = 4)
(4, 'https://drive.google.com/file/d/16BOmc2agkVrubR4WoQ4YpWDatstRB9Nh/view?usp=drive_link', 1),
(4, 'https://drive.google.com/file/d/189hGNUBgX7Tqh9XpnVk3xV714WjJHIKQ/view?usp=drive_link', 2),
(4, 'https://drive.google.com/file/d/1k7UTZbBPYmRCVgUWHgd-ixR9dM2L-loz/view?usp=drive_link', 3),
(4, 'https://drive.google.com/file/d/1MhMw1WMzWrGhw1uHuHVqz6qRidvqWGTp/view?usp=drive_link', 4),
(4, 'https://drive.google.com/file/d/1DeOTqgZWFcFdyFlv8vhmLbyLyBfCCUqH/view?usp=drive_link', 5),
(4, 'https://drive.google.com/file/d/1YRWIGk8MGegYz-wa7Z4TTGvlN7e5bm1j/view?usp=drive_link', 6),
(4, 'https://drive.google.com/file/d/1lR7ojqDc85wmIRf7xFuzAY_KsS1OBv7M/view?usp=drive_link', 7),
(4, 'https://drive.google.com/file/d/1Nm3KBva1qnQ0uc3t24pvrb4e3pI_cmRs/view?usp=drive_link', 8),
(4, 'https://drive.google.com/file/d/1lR7ojqDc85wmIRf7xFuzAY_KsS1OBv7M/view?usp=drive_link', 9),
(4, 'https://drive.google.com/file/d/1YRWIGk8MGegYz-wa7Z4TTGvlN7e5bm1j/view?usp=drive_link', 10),
(4, 'https://drive.google.com/file/d/1DeOTqgZWFcFdyFlv8vhmLbyLyBfCCUqH/view?usp=drive_link', 11),
(4, 'https://drive.google.com/file/d/1MhMw1WMzWrGhw1uHuHVqz6qRidvqWGTp/view?usp=drive_link', 12),
(4, 'https://drive.google.com/file/d/1k7UTZbBPYmRCVgUWHgd-ixR9dM2L-loz/view?usp=drive_link', 13),
(4, 'https://drive.google.com/file/d/189hGNUBgX7Tqh9XpnVk3xV714WjJHIKQ/view?usp=drive_link', 14),
(4, 'https://drive.google.com/file/d/16BOmc2agkVrubR4WoQ4YpWDatstRB9Nh/view?usp=drive_link', 15),

-- Images for Shirshasana (asana_id = 5)
(5, 'https://drive.google.com/file/d/1NVHUkG-24-bUbJ3TMFSrJ8GulbBSuzRF/view?usp=drive_link', 1),
(5, 'https://drive.google.com/file/d/1bkO6Gq4Ux-KRmMh0zLELlPEhI4vx4Tk4/view?usp=drive_link', 2),
(5, 'https://drive.google.com/file/d/10nZyMtDpaldK7_2O2dMnOTG7_RxoS4vr/view?usp=drive_link', 3),
(5, 'https://drive.google.com/file/d/1ZuOo_dE-zf8TFK13eydbBXnr-IjZPhz2/view?usp=drive_link', 4),
(5, 'https://drive.google.com/file/d/10nZyMtDpaldK7_2O2dMnOTG7_RxoS4vr/view?usp=drive_link', 5),
(5, 'https://drive.google.com/file/d/1bkO6Gq4Ux-KRmMh0zLELlPEhI4vx4Tk4/view?usp=drive_link', 6),
(5, 'https://drive.google.com/file/d/1NVHUkG-24-bUbJ3TMFSrJ8GulbBSuzRF/view?usp=drive_link', 7);

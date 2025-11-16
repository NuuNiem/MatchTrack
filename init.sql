DELETE FROM item;
DELETE FROM user;

INSERT INTO user (username, password_hash) VALUES ('test', 'scrypt:32768:8:1$7zidsjxee8qJJNth$9b368982d5ab144dc60718e85b8a495d2f575a0b6b8046fe41b5898c992ba4b4139303eb39c4f41e59fdf2baa019c621669de7bf6a302b3345cbf837348767aa');

INSERT INTO item (title, description, owner_id) VALUES 
('HJK - FC Inter', 'Jännittävä kotipeli, voitto viime hetkillä', 1),
('IFK Mariehamn - HJK', 'Vieraspeli Maarianhaminassa, tasapeli', 1),
('HJK - KuPS', 'Liigaottelu Töölössä, hyvä tunnelma stadionilla', 1);

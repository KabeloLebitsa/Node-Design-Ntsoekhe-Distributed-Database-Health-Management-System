CREATE TRIGGER before_insert_user
BEFORE INSERT ON users
FOR EACH ROW
BEGIN

  DECLARE user_type TEXT;
  SELECT NEW.Role INTO user_type;

  IF user_type NOT IN ('patient', 'doctor') THEN
    RAISE ROLLBACK
  END IF;


  DECLARE last_id INTEGER;
  SELECT MAX(UserID) INTO last_id FROM users;


  IF user_type = 'patient' THEN
    SET NEW.user_id = 'p' || LPAD(CAST(last_id + 1 AS TEXT), 4, '0');
  ELSE
    SET NEW.user_id = 'd' || LPAD(CAST(last_id + 1 AS TEXT), 4, '0');
  END IF;

END;

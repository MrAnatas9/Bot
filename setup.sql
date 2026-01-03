-- ========== ОСНОВНЫЕ ТАБЛИЦЫ ==========

-- Пользователи
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  nickname TEXT NOT NULL,
  job TEXT,
  selected_jobs JSONB DEFAULT '[]',
  coins INTEGER DEFAULT 25,
  level INTEGER DEFAULT 1,
  exp INTEGER DEFAULT 0,
  messages_sent INTEGER DEFAULT 0,
  is_admin BOOLEAN DEFAULT FALSE,
  debt INTEGER DEFAULT 0,
  registration_date TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Задания
CREATE TABLE IF NOT EXISTS tasks (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  reward_coins INTEGER DEFAULT 0,
  reward_exp INTEGER DEFAULT 0,
  status TEXT DEFAULT 'active', -- active, assigned, proof_submitted, completed, rejected, expired
  deadline TIMESTAMP,
  assigned_to BIGINT,
  assigned_at TIMESTAMP,
  proof_text TEXT,
  proof_submitted_at TIMESTAMP,
  completed_at TIMESTAMP,
  rejection_reason TEXT,
  rejected_at TIMESTAMP,
  expired_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Транзакции
CREATE TABLE IF NOT EXISTS transactions (
  id BIGSERIAL PRIMARY KEY,
  from_user_id BIGINT NOT NULL,
  to_user_id BIGINT NOT NULL,
  amount INTEGER NOT NULL,
  reason TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Логи администратора
CREATE TABLE IF NOT EXISTS admin_logs (
  id BIGSERIAL PRIMARY KEY,
  action TEXT NOT NULL,
  user_id BIGINT NOT NULL,
  reason TEXT,
  admin_id BIGINT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Сообщения администратору
CREATE TABLE IF NOT EXISTS admin_messages (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  message_type TEXT, -- premium, job_change, other
  text TEXT NOT NULL,
  status TEXT DEFAULT 'pending', -- pending, approved, rejected
  response TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ========== ИНДЕКСЫ ==========
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(from_user_id, to_user_id);

-- ========== АДМИН ==========
INSERT INTO users (
  user_id, username, nickname, job, selected_jobs, 
  coins, level, is_admin, registration_date
) VALUES (
  6495178643, 'admin', '👑 Глава Клана', '👑 Глава Клана', 
  '["👑 Глава Клана"]', 999999, 10, TRUE, NOW()
) ON CONFLICT (user_id) DO UPDATE SET
  nickname = EXCLUDED.nickname,
  coins = EXCLUDED.coins,
  level = EXCLUDED.level;

-- ========== ТРИГГЕРЫ ==========
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ========== ПРАВА ==========
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

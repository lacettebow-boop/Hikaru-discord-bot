from __future__ import annotations
import sqlite3, os, json
from pathlib import Path
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv_config(guild_id TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, PRIMARY KEY(guild_id,key));
CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, body TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, body TEXT NOT NULL, due_at TEXT NOT NULL, delivered INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS timezones(user_id TEXT PRIMARY KEY, timezone TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS birthdays(guild_id TEXT NOT NULL, user_id TEXT NOT NULL, month INTEGER NOT NULL, day INTEGER NOT NULL, opted_in INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(guild_id,user_id));
CREATE TABLE IF NOT EXISTS warnings(id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT NOT NULL, target_id TEXT NOT NULL, actor_id TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT, actor_id TEXT NOT NULL, action TEXT NOT NULL, target TEXT, reason TEXT, details TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', payload TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT NOT NULL, user_id TEXT NOT NULL, channel_id TEXT, status TEXT NOT NULL DEFAULT 'open', claimed_by TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS suggestions(id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT NOT NULL, user_id TEXT NOT NULL, body TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS confirmations(token TEXT PRIMARY KEY, guild_id TEXT NOT NULL, actor_id TEXT NOT NULL, action TEXT NOT NULL, payload TEXT NOT NULL, expires_at TEXT NOT NULL);
"""
def now():
    return datetime.now(timezone.utc).isoformat()

class Database:
    def __init__(self, path):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as c:
            c.executescript(SCHEMA)

    def connect(self):
        c = sqlite3.connect(self.path, timeout=15)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("PRAGMA journal_mode=WAL")
        return c

    def execute(self, sql, params=()):
        with self.connect() as c:
            cur = c.execute(sql, params)
            return cur.lastrowid

    def all(self, sql, params=()):
        with self.connect() as c:
            return [dict(x) for x in c.execute(sql, params).fetchall()]

    def one(self, sql, params=()):
        with self.connect() as c:
            row = c.execute(sql, params).fetchone()
            return dict(row) if row else None

    def audit(self, guild_id, actor_id, action, target=None, reason=None, details=None):
        return self.execute(
            "INSERT INTO audit(guild_id,actor_id,action,target,reason,details,created_at) VALUES(?,?,?,?,?,?,?)",
            (str(guild_id) if guild_id else None, str(actor_id), action, str(target) if target else None,
             reason, json.dumps(details or {}, ensure_ascii=False), now()))

    def config(self, guild_id, key, value=None):
        gid = str(guild_id or 0)
        if value is None:
            row = self.one("SELECT value FROM kv_config WHERE guild_id=? AND key=?", (gid,key))
            return row["value"] if row else None
        self.execute("INSERT INTO kv_config(guild_id,key,value) VALUES(?,?,?) ON CONFLICT(guild_id,key) DO UPDATE SET value=excluded.value", (gid,key,str(value)))
        return str(value)

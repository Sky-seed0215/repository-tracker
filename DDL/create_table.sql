CREATE TABLE users (
  discord_id bigint,
  prefix text,
  owner text,
  repo text,
  primary key(discord_id, prefix)
)

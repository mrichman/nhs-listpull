drop table if exists job_status;
create table job_status (
  id integer primary key autoincrement,
  list_type_id integer not null default 0,
  record_count integer not null default 0,
  status integer not null default 0,
  ev_job_id integer not null default 0,
  created_at datetime not null default (datetime('now')),
  csv blob
);

drop table if exists list_types;
create table list_types (
  id integer primary key autoincrement,
  name text not null
);

insert into list_types(name) values ('Entire House File + Autoship');
insert into list_types(name) values ('Entire House File - Autoship');
insert into list_types(name) values ('Re-engagement Files');
insert into list_types(name) values ('Autoship Only');
insert into list_types(name) values ('Category Cross-Sell');
insert into list_types(name) values ('By Product Purchased');

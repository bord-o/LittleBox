CREATE DATABASE docker;
GRANT ALL PRIVILEGES ON DATABASE dockerdb TO docker;

drop table if exists files;

create table if not exists files (
    file_index serial,
    hash text not null,
    file_path text not null,
    update_at timestamp,
    primary key (file_index)
);

insert into files (hash, file_path, update_at) values ('testhash', '/testhash/filename', now());

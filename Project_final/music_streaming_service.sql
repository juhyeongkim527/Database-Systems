drop database if exists music_streaming_service;
create database if not exists music_streaming_service;
use music_streaming_service;

drop table if exists admin;
create table if not exists admin (
    `id` int auto_increment not null,
    `aid` varchar(15) not null,
    `apw` varchar(20) not null,
    `name` varchar(30) not null,
    `email` varchar(50) not null,
    primary key (`id`),
    index (`aid`),
    unique (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists admin_role;
create table if not exists admin_role(
    `adm_id` int not null,
    `adm_role` varchar(20) not null,
    primary key (`adm_id`, `adm_role`),
    constraint `admin_role_ibfk_1` foreign key (`adm_id`) references `admin` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists user;
create table if not exists user (
    `id` int auto_increment not null,
    `name` varchar(30) not null,
    `email` varchar(50) not null,
    `sign_up_date` date not null,
    `uid` varchar(15) not null,
    `upw` varchar(20) not null,
    `birth_date` date not null,
    `gender` varchar(1) not null,
    primary key (`id`),
    index (`uid`),
    unique (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists music;
create table if not exists music (
    `id` int auto_increment not null,
    `adm_id` int not null,
    `name` varchar(50) not null,
    `album` varchar(50) default null,
    `genre` varchar(20) not null,
    `lyrics_file_path` text default null,
    `duration` time not null,
    `cover_img_path` text default null,
    `file_path` text not null,
    `release_date` date not null,
    `play_count` int default 0,
    `register_date` date not null,
    `like_count` int default 0,
    primary key (`id`),
    unique (`name`),
    constraint `music_ibfk_1` foreign key (`adm_id`) references `admin` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists music_artist;
create table if not exists music_artist (
    `mus_id` int not null,
    `mus_artist` varchar(50) not null,
    primary key (`mus_id`, `mus_artist`),
    constraint `music_artist_ibfk_1` foreign key (`mus_id`) references `music` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists like_music;
create table if not exists like_music (
    `usr_id` int not null,
    `mus_id` int not null,
    `like_date` date not null,
    primary key (`usr_id`, `mus_id`),
    constraint `like_music_ibfk_1` foreign key (`usr_id`) references `user` (`id`) on delete cascade,
    constraint `like_music_ibfk_2` foreign key (`mus_id`) references `music` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists dislike_music;
create table if not exists dislike_music (
    `usr_id` int not null,
    `mus_id` int not null,
    `dislike_date` date not null,
    primary key (`usr_id`, `mus_id`),
    constraint `dislike_music_ibfk_1` foreign key (`usr_id`) references `user` (`id`) on delete cascade,
    constraint `dislike_music_ibfk_2` foreign key (`mus_id`) references `music` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists user_music_log;
create table if not exists user_music_log (
    `mus_id` int not null,
    `usr_id` int not null,
    `play_duration` time not null,
    `play_date_time` datetime not null,
    primary key (`mus_id`, `usr_id`, `play_date_time`),
    constraint `user_music_log_ibfk_1` foreign key (`mus_id`) references `music` (`id`) on delete cascade,
    constraint `user_music_log_ibfk_2` foreign key (`usr_id`) references `user` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists play_list;
create table if not exists play_list (
    `id` int auto_increment not null,
    `create_usr_id` int not null,
    `name` varchar(50) not null,
    `create_date` date not null,
    `view_access` varchar(1) not null,
    `share_access` varchar(1) not null,
    primary key (`id`),
    constraint `play_list_ibfk_1` foreign key (`create_usr_id`) references `user` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists play_list_music;
create table if not exists play_list_music (
    `pl_id` int not null,
    `mus_id` int not null,
    `register_date` date not null,
    `music_order` int default null,
    primary key (`pl_id`, `mus_id`),
    constraint `play_list_music_ibfk_1` foreign key (`pl_id`) references `play_list` (`id`) on delete cascade,
    constraint `play_list_music_ibfk_2` foreign key (`mus_id`) references `music` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists play_list_share;
create table if not exists play_list_share (
    `usr_id` int not null,
    `pl_id` int not null,
    `share_date` date not null,
    `view_access` varchar(1) not null,
    primary key (`usr_id`, `pl_id`),
    constraint `play_list_share_ibfk_1` foreign key (`usr_id`) references `user` (`id`) on delete cascade,
    constraint `play_list_share_ibfk_2` foreign key (`pl_id`) references `play_list` (`id`) on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
--
-- PostgreSQL database dump
--

-- Dumped from database version 14.3
-- Dumped by pg_dump version 14.3

-- Started on 2022-09-12 12:16:14 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;


COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.histories (
    pid integer NOT NULL,
    price numeric(19,4) NOT NULL,
    start_date date NOT NULL,
    start_time time(0) without time zone NOT NULL,
    end_date date NOT NULL,
    end_time time(0) without time zone NOT NULL,
    currency character(1) NOT NULL,
    shipping numeric(7,4) NOT NULL
);

CREATE SEQUENCE public.histories_pid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.histories_pid_seq OWNED BY public.histories.pid;

CREATE TABLE public.products (
    pid integer NOT NULL,
    prod_name character varying NOT NULL,
    short_url character varying(50) NOT NULL,
    dom_name character varying(40) NOT NULL,
    dom_tld character varying(6) NOT NULL,
    brand character varying(40),
    category character varying(20),
    color character varying(20) NOT NULL,
    size character varying(10) NOT NULL
);

CREATE SEQUENCE public.products_pid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_pid_seq OWNED BY public.products.pid;

ALTER TABLE ONLY public.histories ALTER COLUMN pid SET DEFAULT nextval('public.histories_pid_seq'::regclass);

ALTER TABLE ONLY public.products ALTER COLUMN pid SET DEFAULT nextval('public.products_pid_seq'::regclass);

SELECT pg_catalog.setval('public.histories_pid_seq', 1, false);

ALTER TABLE ONLY public.histories
    ADD CONSTRAINT histories_pk PRIMARY KEY (pid, price, start_date, start_time, end_date, end_time, currency);

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pk PRIMARY KEY (pid);

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_un_attrs UNIQUE (prod_name, dom_name, dom_tld, color, size);

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_un_url UNIQUE (short_url);

ALTER TABLE ONLY public.histories
    ADD CONSTRAINT histories_fk FOREIGN KEY (pid) REFERENCES public.products(pid);


